import argparse
import json
import sys
from pathlib import Path
import pandas as pd

# Ensure workspace root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.evaluation.metrics import EvaluationRecord, BenchmarkMetrics

def main():
    parser = argparse.ArgumentParser(description="Evaluate ToolPrivBench results and output tables")
    parser.add_argument("--input-dir", type=str, default="results", help="Directory containing JSON results")
    parser.add_argument("--output-latex", type=str, default="paper/sections/table_results.tex", help="Path to LaTeX output table")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    records = []

    for file in sorted(input_path.glob("benchmark_results_*.json")):
        with open(file, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            for item in data:
                records.append(EvaluationRecord(**item))

    if not records:
        print("No evaluation records found in input-dir.")
        return

    summary = BenchmarkMetrics.compute_summary(records)
    print("\n" + "="*80)
    print("AGGREGATED BENCHMARK SUMMARY (COMPUTED DIRECTLY FROM LOGS):")
    print("="*80)
    print(summary.to_string(index=False))

    # Calculate overall latency statistics
    all_latencies = [r.latency_ms for r in records]
    if all_latencies:
        mean_lat = pd.Series(all_latencies).mean()
        std_lat = pd.Series(all_latencies).std()
        print(f"\nOverall Latency: {mean_lat:.2f} ± {std_lat:.2f} ms")

    latex_table = BenchmarkMetrics.generate_latex_table_1(records)
    latex_out_path = Path(args.output_latex)
    latex_out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(latex_out_path, "w", encoding="utf-8") as f:
        f.write(latex_table)
    print(f"\nSaved publication Table 1 to {latex_out_path}")

if __name__ == "__main__":
    main()
