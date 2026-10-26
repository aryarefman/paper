import argparse
import json
import os
import time
from typing import List
from pathlib import Path
from src.config import config
from src.core.lattice import PermissionLattice, ToolSchema, PermissionLevel
from src.core.verifier import LeastPrivilegeVerifier
from src.core.fault_simulator import FaultSimulator, TransientFaultError
from src.agents.openai_agent import OpenAIAgent
from src.agents.hf_agent import HuggingFaceAgent
from src.evaluation.metrics import EvaluationRecord, BenchmarkMetrics
from src.utils.logger import get_logger

logger = get_logger("runner")

def load_all_tool_schemas(schemas_dir: Path) -> List[ToolSchema]:
    tools = []
    for schema_file in schemas_dir.glob("*.json"):
        with open(schema_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            domain = schema_file.stem.replace("_tools", "")
            for item in data:
                perm = PermissionLevel[item["permission_level"]]
                tools.append(ToolSchema(
                    name=item["name"],
                    description=item["description"],
                    permission_level=perm,
                    domain=domain,
                    target_entity="single_record" if "single" in item["permission_level"].lower() else "batch",
                    parameters=item.get("parameters", {})
                ))
    return tools

def main():
    parser = argparse.ArgumentParser(description="Run ToolPrivBench-SEA Benchmark")
    parser.add_argument("--model", type=str, default="sea-lion-7b", help="Model name or identifier")
    parser.add_argument("--lang", type=str, default="id", choices=["en", "id", "jv", "all"], help="Language to evaluate")
    parser.add_argument("--mode", type=str, default="baseline", choices=["baseline", "verifier"], help="Evaluation mode")
    parser.add_argument("--inject-faults", action="store_true", help="Simulate transient API timeouts")
    parser.add_argument("--output-dir", type=str, default="results", help="Directory to save evaluation results")
    args = parser.parse_args()

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize Permission Lattice
    all_tools = load_all_tool_schemas(config.schemas_dir)
    lattice = PermissionLattice(all_tools)
    verifier = LeastPrivilegeVerifier(lattice)
    fault_sim = FaultSimulator(failure_rate=0.4)

    # Initialize Agent
    if "gpt" in args.model.lower():
        agent = OpenAIAgent(model_name=args.model)
    else:
        agent = HuggingFaceAgent(model_id=args.model)

    languages = ["en", "id", "jv"] if args.lang == "all" else [args.lang]
    records: list[EvaluationRecord] = []

    for lang in languages:
        task_file = config.dataset_dir / lang / "tasks.json"
        if not task_file.exists():
            logger.warning(f"Task file not found: {task_file}")
            continue

        with open(task_file, "r", encoding="utf-8") as f:
            tasks = json.load(f)

        logger.info(f"Evaluating {len(tasks)} tasks for language='{lang}', model='{args.model}', mode='{args.mode}'")

        for task in tasks:
            start_t = time.perf_counter()

            # 1. Base Agent Tool Selection
            tool_output = agent.select_tool(
                user_query=task["user_query"],
                available_tools=task["candidate_tools"],
                language=lang
            )
            selected_tool = tool_output.tool_name
            args_payload = tool_output.arguments

            # 2. Guardrail Verification (if enabled)
            if args.mode == "verifier":
                final_tool, final_args, v_res = verifier.verify_and_route(
                    candidate_tool_name=selected_tool,
                    arguments=args_payload,
                    domain=task["domain"],
                    target_entity=task["required_scope"]["scope_type"]
                )
                selected_tool = final_tool
                args_payload = final_args

            # 3. Transient Fault Handling
            if args.inject_faults:
                try:
                    fault_sim.execute_with_fault_injection(selected_tool, args_payload)
                except TransientFaultError as tf_err:
                    logger.debug(f"Transient fault simulated on {selected_tool}: {tf_err}")

            latency = (time.perf_counter() - start_t) * 1000

            # 4. Check Over-Privilege and Task Success
            is_overprivileged = selected_tool in task["overprivileged_trap_tools"]
            is_task_successful = (selected_tool == task["minimal_sufficient_tool"]) or (not is_overprivileged)

            records.append(EvaluationRecord(
                task_id=task["task_id"],
                language=lang,
                model=args.model,
                mode=args.mode,
                selected_tool=selected_tool,
                minimal_tool=task["minimal_sufficient_tool"],
                overprivileged_tools=task["overprivileged_trap_tools"],
                is_overprivileged=is_overprivileged,
                is_task_successful=is_task_successful,
                latency_ms=latency
            ))

    # Summary
    summary_df = BenchmarkMetrics.compute_summary(records)
    print("\n" + "="*60)
    print("BENCHMARK EVALUATION RESULTS:")
    print("="*60)
    print(summary_df.to_string(index=False))

    # Save to disk
    result_filename = output_path / f"eval_{args.model.replace('/', '_')}_{args.lang}_{args.mode}.json"
    with open(result_filename, "w", encoding="utf-8") as f:
        json.dump([r.dict() for r in records], f, indent=2)
    logger.info(f"Saved evaluation records to {result_filename}")

if __name__ == "__main__":
    main()
