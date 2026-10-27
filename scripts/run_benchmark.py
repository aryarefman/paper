import argparse
import json
import os
import sys
import time
from typing import List, Dict, Any
from pathlib import Path

# Ensure root directory in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import config
from src.core.lattice import PermissionLattice, ToolSchema, PermissionLevel
from src.core.verifier import LeastPrivilegeVerifier
from src.core.fault_simulator import FaultSimulator
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
            for item in data:
                perm = PermissionLevel[item["permission_level"]]
                tools.append(ToolSchema(
                    name=item["name"],
                    description=item["description"],
                    permission_level=perm,
                    domain=item.get("domain", schema_file.stem.replace("_tools", "")),
                    capability=item.get("capability", "general"),
                    parameters=item.get("parameters", {})
                ))
    return tools

def main():
    parser = argparse.ArgumentParser(description="Run ToolPrivBench-SEA Benchmark")
    parser.add_argument("--model", type=str, default="sea-lion-7b", help="Model name or identifier")
    parser.add_argument("--lang", type=str, default="all", choices=["en", "id", "jv", "all"], help="Language to evaluate")
    parser.add_argument("--mode", type=str, default="all", choices=["baseline", "prompt_defense", "verifier", "all"], help="Evaluation mode")
    parser.add_argument("--inject-faults", action="store_true", help="Simulate transient API timeouts and test escalation")
    parser.add_argument("--output-dir", type=str, default="results", help="Directory to save execution logs")
    args = parser.parse_args()

    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Initialize Permission Lattice & Verifier
    all_tools = load_all_tool_schemas(config.schemas_dir)
    lattice = PermissionLattice(all_tools)
    verifier = LeastPrivilegeVerifier(lattice)
    fault_sim = FaultSimulator(failure_rate=0.5, seed=42)

    # Initialize Agent
    if "gpt" in args.model.lower():
        agent = OpenAIAgent(model_name=args.model)
    else:
        agent = HuggingFaceAgent(model_id=args.model)

    languages = ["en", "id", "jv"] if args.lang == "all" else [args.lang]
    modes = ["baseline", "prompt_defense", "verifier"] if args.mode == "all" else [args.mode]

    all_records: List[EvaluationRecord] = []

    for mode in modes:
        is_prompt_defense = (mode == "prompt_defense")
        use_verifier = (mode == "verifier")

        for lang in languages:
            task_file = config.dataset_dir / lang / "tasks.json"
            if not task_file.exists():
                logger.warning(f"Task file not found: {task_file}")
                continue

            with open(task_file, "r", encoding="utf-8") as f:
                tasks = json.load(f)

            logger.info(f"Running mode='{mode}', lang='{lang}', model='{args.model}' on {len(tasks)} tasks")

            for task in tasks:
                start_t = time.perf_counter()

                # Turn 1: Agent Selects Tool
                t1_output = agent.select_tool(
                    user_query=task["user_query"],
                    available_tools=task["candidate_tools"],
                    language=lang,
                    prompt_defense=is_prompt_defense
                )
                selected_tool_name = t1_output.tool_name
                selected_args = t1_output.arguments

                fault_injected = False
                panic_escalated = False

                # Handle Transient Faults on Minimal Tool if enabled
                if args.inject_faults and selected_tool_name == task["minimal_sufficient_tool"]:
                    is_fault, fault_resp = fault_sim.simulate_execution(
                        tool_name=selected_tool_name,
                        arguments=selected_args,
                        is_minimal_tool=True
                    )
                    if is_fault:
                        fault_injected = True
                        # Turn 2: Agent responds to fault
                        t2_output = agent.handle_retry(
                            user_query=task["user_query"],
                            failed_tool=selected_tool_name,
                            error_message=fault_resp["message"],
                            available_tools=task["candidate_tools"],
                            language=lang,
                            prompt_defense=is_prompt_defense
                        )
                        # Check if agent attempted to escalate privilege
                        t2_tool_obj = lattice.get_tool(t2_output.tool_name)
                        min_tool_obj = lattice.get_tool(task["minimal_sufficient_tool"])
                        if t2_tool_obj and min_tool_obj and t2_tool_obj.permission_level.strictly_subsumes(min_tool_obj.permission_level):
                            panic_escalated = True

                        selected_tool_name = t2_output.tool_name
                        selected_args = t2_output.arguments

                # Apply Deterministic Verifier Guardrail if in 'verifier' mode
                executed_tool_name = selected_tool_name
                executed_args = selected_args

                if use_verifier:
                    # Deterministic verifier operates solely on candidate tool and arguments,
                    # inferring domain and capability directly from tool schema without ground truth leakage
                    final_tool, final_args, v_res = verifier.verify_and_route(
                        candidate_tool_name=selected_tool_name,
                        arguments=selected_args
                    )
                    executed_tool_name = final_tool
                    executed_args = final_args
                    if panic_escalated and v_res.was_downgraded:
                        # Escalation successfully blocked and downgraded by verifier
                        panic_escalated = False

                latency = (time.perf_counter() - start_t) * 1000

                # Resolve Tool Metadata
                sel_tool_obj = lattice.get_tool(selected_tool_name)
                exec_tool_obj = lattice.get_tool(executed_tool_name)
                min_tool_obj = lattice.get_tool(task["minimal_sufficient_tool"])

                sel_priv = sel_tool_obj.permission_level if sel_tool_obj else PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED
                exec_priv = exec_tool_obj.permission_level if exec_tool_obj else PermissionLevel.LEVEL_4_ADMIN_UNRESTRICTED
                min_priv = min_tool_obj.permission_level if min_tool_obj else PermissionLevel.LEVEL_1_READ_SINGLE

                exec_cap = exec_tool_obj.capability if exec_tool_obj else "unknown"

                record = BenchmarkMetrics.evaluate_task(
                    task_id=task["task_id"],
                    language=lang,
                    model=args.model,
                    mode=mode,
                    selected_tool=selected_tool_name,
                    executed_tool=executed_tool_name,
                    minimal_tool=task["minimal_sufficient_tool"],
                    required_capability=task["capability"],
                    executed_capability=exec_cap,
                    selected_privilege=sel_priv,
                    executed_privilege=exec_priv,
                    minimal_privilege=min_priv,
                    fault_injected=fault_injected,
                    panic_escalated=panic_escalated,
                    latency_ms=latency,
                    execution_backend=t1_output.mode
                )
                all_records.append(record)

    # Compute Summary
    summary_df = BenchmarkMetrics.compute_summary(all_records)
    print("\n" + "="*80)
    print("EVALUATION RESULTS SUMMARY:")
    print("="*80)
    print(summary_df.to_string(index=False))

    # Save Real Results
    result_file = output_path / f"benchmark_results_{args.model.replace('/', '_')}.json"
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump([r.dict() for r in all_records], f, indent=2)
    logger.info(f"Saved real execution records to {result_file}")

    summary_file = output_path / f"benchmark_summary_{args.model.replace('/', '_')}.csv"
    summary_df.to_csv(summary_file, index=False)
    logger.info(f"Saved summary to {summary_file}")

if __name__ == "__main__":
    main()
