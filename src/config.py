import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent

class BenchmarkConfig(BaseModel):
    dataset_dir: Path = BASE_DIR / "dataset"
    results_dir: Path = BASE_DIR / "results"
    schemas_dir: Path = BASE_DIR / "dataset" / "schemas"
    default_models: list[str] = [
        "aisingapore/sea-lion-7b-instruct",
        "Qwen/Qwen2.5-7B-Instruct",
        "meta-llama/Meta-Llama-3.1-8B-Instruct"
    ]
    languages: list[str] = ["en", "id", "jv"]
    max_tokens: int = 512
    temperature: float = 0.0
    timeout_seconds: float = 30.0

config = BenchmarkConfig()
