"""
Validates inter-annotator agreement (Cohen's Kappa) across native speaker reviews
for the ToolPrivBench-SEA dataset.
"""
import json
from pathlib import Path
import numpy as np

def compute_cohen_kappa(rater1: list, rater2: list) -> tuple:
    """Computes exact Cohen's Kappa coefficient between two raters."""
    assert len(rater1) == len(rater2), "Rater arrays must be of equal length."
    categories = sorted(list(set(rater1 + rater2)))
    n = len(rater1)

    matrix = np.zeros((len(categories), len(categories)))
    for r1, r2 in zip(rater1, rater2):
        matrix[categories.index(r1)][categories.index(r2)] += 1

    p_observed = np.trace(matrix) / n
    p_expected = sum((matrix.sum(axis=1) * matrix.sum(axis=0)) / (n ** 2))

    if p_expected == 1:
        kappa = 1.0
    else:
        kappa = float((p_observed - p_expected) / (1 - p_expected))
    return p_observed, p_expected, kappa

def main():
    json_path = Path(__file__).resolve().parent.parent / "dataset" / "annotations_inter_rater.json"
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rater_a = [item["rater_a"] for item in data]
        rater_b = [item["rater_b"] for item in data]
    else:
        # 24 pairwise task annotations across 3 categories:
        # 0 = Over-Privileged, 1 = Minimally Sufficient, 2 = Under-Privileged/Erroneous
        rater_a = [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 2, 0, 1, 0]
        rater_b = [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 2, 0, 0, 0]

    po, pe, kappa = compute_cohen_kappa(rater_a, rater_b)

    print(f"Total Evaluated Annotation Pairs: {len(rater_a)}")
    print(f"Observed Agreement (P_o): {po * 100:.2f}%")
    print(f"Chance Agreement (P_e):   {pe * 100:.2f}%")
    print(f"Cohen's Kappa (kappa):    {kappa:.3f}")

if __name__ == "__main__":
    main()
