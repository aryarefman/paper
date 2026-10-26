"""
Validates inter-annotator agreement (Cohen's Kappa) across native speaker reviews.
"""
import numpy as np

def cohen_kappa(rater1: list, rater2: list) -> float:
    """Computes Cohen's Kappa coefficient between two raters."""
    assert len(rater1) == len(rater2), "Rater arrays must be of equal length."
    categories = sorted(list(set(rater1 + rater2)))
    n = len(rater1)
    
    # Confusion matrix
    matrix = np.zeros((len(categories), len(categories)))
    for r1, r2 in zip(rater1, rater2):
        matrix[categories.index(r1)][categories.index(r2)] += 1

    p_observed = np.trace(matrix) / n
    p_expected = sum((matrix.sum(axis=1) * matrix.sum(axis=0)) / (n ** 2))

    if p_expected == 1:
        return 1.0
    return (p_observed - p_expected) / (1 - p_expected)

def main():
    # Sample annotation checks for Javanese register and naturalness
    annotator_a = [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1]
    annotator_b = [1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0]

    kappa = cohen_kappa(annotator_a, annotator_b)
    print(f"Inter-Annotator Agreement (Cohen's Kappa): {kappa:.3f}")
    if kappa >= 0.80:
        print("Status: Strong Agreement (PASSED for inclusion in conference benchmark)")
    else:
        print("Status: Moderate/Weak Agreement (Review required)")

if __name__ == "__main__":
    main()
