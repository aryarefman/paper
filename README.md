# Least-Privilege Guardrails for Multilingual LLM Agents

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Target Venue: ACL / ICSE 2027](https://img.shields.io/badge/Target%20Venue-ACL%20%2F%20ICSE-red.svg)]()
[![Affiliation: ITS Surabaya & NUS SoC](https://img.shields.io/badge/Affiliation-ITS%20%7C%20NUS%20SoC-orange.svg)]()

> **Paper Title:** *Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection (English, Indonesian, Javanese)*  
> **Authors:** Undergraduate Research Initiative (Institut Teknologi Sepuluh Nopember & National University of Singapore)

---

## 📌 Abstract & Overview

Large Language Model (LLM) agents are increasingly entrusted with autonomous tool invocation across enterprise, cloud, and civic administration systems. However, recent security benchmarks reveal that agents frequently exhibit **over-privileged tool selection**—invoking high-permission APIs (e.g., `delete_all_records`, `system_exec`) when lower-permission alternatives (e.g., `lookup_record`) fully satisfy user intent. 

While this vulnerability has been studied primarily on standard English benchmarks, the security implications of **cross-lingual transfer** into regional Southeast Asian languages (such as Indonesian and low-resource regional languages like Javanese) remain unexplored. In this repository, we investigate how morphological shifts, honorifics (krama/ngoko), and intent ambiguity trigger privilege escalation in multilingual LLMs. To mitigate this vulnerability, we propose a **deterministic, mechanistic least-privilege guardrail** that intercepts tool emissions at runtime, inspects argument constraints against a hierarchical permission lattice, and automatically downgrades unauthorized or excessive privileges without sacrificing task utility.

---

## 🏛️ System Architecture

```
                                      [User Query]
                    (English / Bahasa Indonesia / Basa Jawa)
                                           │
                                           ▼
                            [Multilingual LLM Agent]
                       (SEA-LION, Qwen 2.5, Llama 3.1, GPT-4o)
                                           │
                        Emits Candidate Call: T_cand(args)
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                   DETERMINISTIC LEAST-PRIVILEGE VERIFIER (OUR METHOD)                  │
│                                                                                        │
│  1. Parameter Scope Inspector:                                                         │
│     Deterministically validates argument boundaries (e.g., ID lookup vs. wildcard).    │
│                                                                                        │
│  2. Privilege Lattice Subsumption:                                                     │
│     Maps tools to formal poset: [ReadOnly_Single] ≺ [ReadOnly_Batch] ≺ [Write] ≺ [All] │
│                                                                                        │
│  3. Deterministic Downgrade Engine:                                                    │
│     If args require [ReadOnly_Single], automatically downgrades T_cand from             │
│     [ReadOnly_Batch] to [ReadOnly_Single] before API dispatch.                         │
│                                                                                        │
│  4. Transient-Fault Quarantine:                                                        │
│     Prevents agents from panic-escalating to high-privilege alternatives upon timeouts.│
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
                               [Safe Execution Engine]
```

---

## 📂 Repository Structure

```text
├── paper/                             # LaTeX Conference Paper (ACL / ICSE Format)
│   ├── main.tex                       # Master LaTeX document
│   ├── references.bib                 # Comprehensive BibTeX entries
│   ├── figures/                       # Vector diagrams and empirical plots
│   └── sections/                      # Modular LaTeX sections (00 to 07)
│
├── resources/                         # Academic Materials & Literature Review
│   ├── literature_review.md           # Taxonomy and analysis of 15+ related papers
│   ├── reading_notes/                 # Detailed paper summaries (ToolPrivBench, SEA-LION, etc.)
│   └── presentations/                 # Slide decks for lab meetings and seminar proposals
│
├── dataset/                           # ToolPrivBench-SEA Benchmark
│   ├── README.md                      # Annotation guidelines & Cohen's Kappa validation
│   ├── schemas/                       # Formal JSON tool schemas with permission levels
│   ├── en/tasks.json                  # English benchmark tasks
│   ├── id/tasks.json                  # Indonesian adapted tasks
│   └── jv/tasks.json                  # Javanese adapted tasks (ngoko & krama registers)
│
├── src/                               # Core Python Implementation
│   ├── core/                          # Lattice engine, inspector, verifier, fault injector
│   ├── agents/                        # Connectors for open & closed multilingual LLMs
│   ├── evaluation/                    # Metrics: OPR, TCR, Security Gain, Latency
│   └── utils/                         # Logging, configuration, and helpers
│
├── scripts/                           # Execution & Analysis Scripts
│   ├── run_benchmark.py               # Main CLI runner across models and languages
│   ├── evaluate_results.py            # Generates publication-ready tables and figures
│   └── validate_annotations.py        # Computes inter-annotator agreement metrics
│
├── tests/                             # Unit & Integration Tests (pytest)
├── pyproject.toml                     # Python package configuration
└── requirements.txt                   # Pinned runtime dependencies
```

---

## 📊 Core Research Questions & Metrics

* **RQ1 (Cross-Lingual Vulnerability):** Does language shift from English to Indonesian and Javanese increase the **Over-Privilege Rate ($OPR$)** in open multilingual LLMs?
  $$OPR = \frac{1}{|D|} \sum_{i=1}^{|D|} \mathbb{I}\Big(\text{Priv}(t_i^{\text{chosen}}) \sqsupset \text{Priv}(t_i^{\text{optimal}})\Big)$$

* **RQ2 (Mechanistic Mitigation):** Can a deterministic permission lattice downgrade over-privileged tool calls while maintaining a high **Task Completion Rate ($TCR$)**?
  $$TCR = \frac{1}{|D|} \sum_{i=1}^{|D|} \mathbb{I}\Big(\text{TaskSuccess}(q_i, t_i^{\text{executed}}) = 1\Big)$$

* **RQ3 (Fault Robustness):** Does the verifier prevent unauthorized privilege escalation when lower-privilege APIs experience synthetic transient faults (HTTP 504 / Timeouts)?

---

## 🚀 Quickstart & Reproduction

### 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/arya4/paper.git
cd paper

# Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Running Unit Tests

```bash
pytest tests/ -v
```

### 3. Running the Benchmark

```bash
# Evaluate baseline model on Indonesian test set without guardrail
python scripts/run_benchmark.py --model sea-lion-7b --lang id --mode baseline

# Evaluate model with Deterministic Least-Privilege Guardrail
python scripts/run_benchmark.py --model sea-lion-7b --lang id --mode verifier --inject-faults

# Generate comparative evaluation tables and figures
python scripts/evaluate_results.py --input-dir results/ --output-dir paper/figures/
```

---

## 📖 Citation

If you use this benchmark, methodology, or code in your research, please cite:

```bibtex
@inproceedings{aryarefman2027leastprivilege,
  author    = {Arya, Refman and Collaborators},
  title     = {Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection},
  booktitle = {Proceedings of the Annual Meeting of the Association for Computational Linguistics (ACL)},
  year      = {2027},
  publisher = {Association for Computational Linguistics}
}
```

---

## 📜 License

This project is licensed under the [Apache License 2.0](LICENSE).
