"""
Ablation Study: Capability-Preserving vs Domain-Only Lattice Downgrading.
Evaluates the impact on Task Completion Rate (TCR) when capability indexing
is removed from the permission lattice (reverting to naive domain-only PoLP).
"""
import json
import sys
from pathlib import Path
import pandas as pd

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.config import config
from src.core.lattice import PermissionLattice, ToolSchema, PermissionLevel
from src.core.verifier import LeastPrivilegeVerifier
from scripts.run_benchmark import load_all_tool_schemas

def run_ablation():
    all_tools = load_all_tool_schemas(config.schemas_dir)
    lattice = PermissionLattice(all_tools)
    verifier = LeastPrivilegeVerifier(lattice)

    # Load English tasks as archetype set
    task_file = config.dataset_dir / "en" / "tasks.json"
    with open(task_file, "r", encoding="utf-8") as f:
        tasks = json.load(f)

    results = []

    for task in tasks:
        # Simulate over-privileged selection (agent chooses trap tool if available)
        selected_tool_name = task["overprivileged_trap_tools"][0] if task["overprivileged_trap_tools"] else task["minimal_sufficient_tool"]
        arguments = {"user_id": "5025201048"}
        if "IF" in task["user_query"]:
            arguments = {"department_code": "IF"}
        elif "settings.json" in task["user_query"] or "audit.log" in task["user_query"]:
            arguments = {"filename": "settings.json", "user_id": "arya"}

        # 1. Standard Verifier with Capability Preservation
        final_tool_cap, _, res_cap = verifier.verify_and_route(
            candidate_tool_name=selected_tool_name,
            arguments=arguments,
            domain=task["domain"],
            required_capability=task["capability"]
        )
        tool_obj_cap = lattice.get_tool(final_tool_cap)
        tcr_cap = (tool_obj_cap.capability == task["capability"]) if tool_obj_cap else False

        # 2. Ablated Verifier without Capability Indexing (naive domain-only least privilege)
        # Finds the first minimal tool in the domain regardless of capability
        domain_tools = [t for t in all_tools if t.domain == task["domain"]]
        domain_tools.sort(key=lambda t: t.permission_level.value)
        naive_minimal_tool = domain_tools[0].name if domain_tools else selected_tool_name

        tool_obj_naive = lattice.get_tool(naive_minimal_tool)
        tcr_naive = (tool_obj_naive.capability == task["capability"]) if tool_obj_naive else False

        results.append({
            "task_id": task["task_id"],
            "domain": task["domain"],
            "required_capability": task["capability"],
            "selected_trap_tool": selected_tool_name,
            "verifier_tool_with_capability": final_tool_cap,
            "tcr_with_capability": tcr_cap,
            "ablated_naive_tool": naive_minimal_tool,
            "tcr_without_capability": tcr_naive
        })

    df = pd.DataFrame(results)
    tcr_with = df["tcr_with_capability"].mean() * 100
    tcr_without = df["tcr_without_capability"].mean() * 100

    print("="*70)
    print("ABLATION STUDY: Capability Preservation vs Domain-Only Downgrade")
    print("="*70)
    print(df[["task_id", "domain", "required_capability", "verifier_tool_with_capability", "tcr_with_capability", "ablated_naive_tool", "tcr_without_capability"]].to_string(index=False))
    print("-"*70)
    print(f"TCR with Capability Preservation:     {tcr_with:.1f}%")
    print(f"TCR without Capability (Domain-Only): {tcr_without:.1f}%")
    print("="*70)

    out_file = Path("results/ablation_capability_results.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary": {
                "tcr_with_capability_pct": tcr_with,
                "tcr_without_capability_pct": tcr_without,
                "utility_drop_pct": tcr_with - tcr_without
            },
            "task_breakdown": results
        }, f, indent=2)
    print(f"Saved ablation results to {out_file}")

if __name__ == "__main__":
    run_ablation()
