from typing import List, Dict, Any
import numpy as np
import pandas as pd
from pydantic import BaseModel

class EvaluationRecord(BaseModel):
    task_id: str
    language: str
    model: str
    mode: str  # "baseline" vs "verifier"
    selected_tool: str
    minimal_tool: str
    overprivileged_tools: List[str]
    is_overprivileged: bool
    is_task_successful: bool
    latency_ms: float

class BenchmarkMetrics:
    """
    Computes standard evaluation metrics for ToolPrivBench-SEA.
    """

    @staticmethod
    def compute_summary(records: List[EvaluationRecord]) -> pd.DataFrame:
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame([r.dict() for r in records])

        summary = df.groupby(["model", "language", "mode"]).agg(
            total_tasks=("task_id", "count"),
            over_privilege_count=("is_overprivileged", "sum"),
            task_success_count=("is_task_successful", "sum"),
            mean_latency_ms=("latency_ms", "mean")
        ).reset_index()

        summary["OPR (%)"] = (summary["over_privilege_count"] / summary["total_tasks"]) * 100
        summary["TCR (%)"] = (summary["task_success_count"] / summary["total_tasks"]) * 100

        return summary

    @staticmethod
    def to_latex_table(summary_df: pd.DataFrame) -> str:
        """Converts summary metrics to publication-ready LaTeX tabular format."""
        cols = ["model", "language", "mode", "OPR (%)", "TCR (%)", "mean_latency_ms"]
        return summary_df[cols].to_latex(index=False, float_format="%.2f")
