import argparse
import json
from pathlib import Path
import pandas as pd
from src.evaluation.metrics import EvaluationRecord, BenchmarkMetrics

def main():
    parser = argparse.ArgumentParser(description="Evaluate ToolPrivBench results and output tables")
    parser.add_argument("--input-dir", type=str, default="results", help="Directory containing JSON results")
    parser.add_argument("--output-latex", type=str, default="paper/sections/table_results.tex", help="Path to LaTeX output table")
    args = parser.parse_args()

    input_path = Path(args.input_dir)
    records = []

    for file in input_path.glob("benchmark_results_*.json"):
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                records.append(EvaluationRecord(**item))

    if not records:
        print("No evaluation records found in input-dir.")
        return

    summary = BenchmarkMetrics.compute_summary(records)
    print("\nAGGREGATED BENCHMARK SUMMARY (REAL RUN DATA):")
    print(summary.to_string(index=False))

    latex_table = BenchmarkMetrics.to_latex_table(summary)
    latex_out_path = Path(args.output_latex)
    latex_out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(latex_out_path, "w", encoding="utf-8") as f:
        f.write(latex_table)
    print(f"\nSaved LaTeX tabular format to {latex_out_path}")

if __name__ == "__main__":
    main()
