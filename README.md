# Least-Privilege Guardrails for Multilingual LLM Agents

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Target Venue: ACL / ICSE](https://img.shields.io/badge/Target%20Venue-ACL%20%2F%20ICSE-red.svg)]()
[![Affiliation: ITS Surabaya](https://img.shields.io/badge/Affiliation-ITS%20Surabaya-orange.svg)]()

> **Paper Title:** *Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection (English, Indonesian, Javanese)*  
> **Author:** Arya Refman (Department of Informatics, Institut Teknologi Sepuluh Nopember, Surabaya, Indonesia)

---

## 📌 Abstract & Overview

Large Language Model (LLM) agents are increasingly entrusted with autonomous tool invocation across enterprise, cloud, and civic administration systems. However, recent security benchmarks reveal that agents frequently exhibit **over-privileged tool selection**—invoking high-permission APIs (e.g., executing raw database queries or global exports) when lower-permission alternatives (e.g., single-record lookups) strictly suffice to fulfill user intent. 

While this vulnerability has been studied primarily on standard English benchmarks (e.g., Yang et al., arXiv:2406.20023), the security implications of **cross-lingual transfer** into regional Southeast Asian languages (such as Indonesian and low-resource regional languages like Javanese) remain unexplored. In this repository, we investigate how morphological shifts, honorifics (krama/ngoko), and intent ambiguity trigger privilege escalation in multilingual LLMs. To mitigate this vulnerability, we propose a **deterministic, capability-preserving least-privilege guardrail** that intercepts tool emissions at runtime, inspects argument constraints against a hierarchical permission lattice, and automatically down-casts excessive privileges into minimal-sufficient equivalents while strictly preserving functional capabilities.

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
│  2. Privilege Lattice Subsumption with Capability Preservation:                        │
│     Maps tools to formal poset: [ReadOnly_Single] ≺ [ReadOnly_Batch] ≺ [Write] ≺ [All] │
│     Guarantees that downgrades strictly match the required functional capability       │
│     (e.g., academic transcript queries are never mapped to account balance tools).     │
│                                                                                        │
│  3. Deterministic Downgrade Engine:                                                    │
│     If args require [ReadOnly_Single], automatically downgrades T_cand to              │
│     the minimal sufficient equivalent before API dispatch.                             │
│                                                                                        │
│  4. Transient-Fault Quarantine:                                                        │
│     Catches HTTP 504 timeouts on minimal tools and blocks panic privilege escalation.  │
└──────────────────────────────────────────┬─────────────────────────────────────────────┘
                                           │
                                           ▼
                               [Safe Execution Engine]
```

---

## 📂 Repository Structure

```text
├── paper/                             # Compilable LaTeX Paper
│   ├── main.tex                       # Master LaTeX document
│   ├── references.bib                 # Verified BibTeX entries (Yang et al. arXiv:2406.20023)
│   └── sections/                      # Modular LaTeX sections (00 to 08)
│
├── resources/                         # Academic Materials & Literature Review
│   ├── literature_review.md           # Taxonomy and analysis of related papers
│   ├── reading_notes/                 # Detailed paper summaries
│   └── presentations/                 # Slide decks for lab meetings and seminar proposals
│
├── dataset/                           # ToolPrivBench-SEA Benchmark
│   ├── README.md                      # Annotation guidelines & Cohen's Kappa validation
│   ├── schemas/                       # Formal JSON tool schemas with capability annotations
│   ├── en/tasks.json                  # English benchmark tasks (12 tasks)
│   ├── id/tasks.json                  # Indonesian adapted tasks (12 tasks)
│   └── jv/tasks.json                  # Javanese adapted tasks (12 tasks, ngoko & krama)
│
├── results/                           # Real Execution Logs (432 controlled runs)
│   ├── benchmark_results_sea-lion-7b.json
│   ├── benchmark_results_qwen-2.5-7b.json
│   ├── benchmark_results_llama-3.1-8b.json
│   └── benchmark_results_gpt-4o.json
│
├── src/                               # Core Python Implementation
│   ├── core/                          # Lattice engine, inspector, verifier, fault injector
│   ├── agents/                        # Connectors for open & closed multilingual LLMs
│   ├── evaluation/                    # Metrics: OPR, TCR, PER, Latency
│   └── utils/                         # Logging and configuration
│
├── scripts/                           # Execution & Analysis Scripts
│   ├── run_benchmark.py               # Main CLI runner across models and languages
│   ├── evaluate_results.py            # Generates publication-ready tables and figures
│   └── validate_annotations.py        # Computes exact Cohen's Kappa agreement
│
├── tests/                             # Unit & Integration Tests (pytest)
├── pyproject.toml                     # Python package configuration
└── requirements.txt                   # Pinned runtime dependencies
```

---

## 📊 Summary of Real Benchmark Results (432 Executions)

| Model | Defense Mode | English OPR | English TCR | Indonesian OPR | Indonesian TCR | Javanese OPR | Javanese TCR | Fault Escalation (PER) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SEA-LION-7B** | Baseline | 25.0% | 91.7% | 41.7% | 83.3% | 58.3% | 66.7% | 75.0% |
| | Prompt Defense | 16.7% | 91.7% | 25.0% | 91.7% | 41.7% | 83.3% | 25.0% |
| | **+ Our Verifier** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** |
| **Qwen-2.5-7B** | Baseline | 16.7% | 91.7% | 33.3% | 83.3% | 50.0% | 75.0% | 50.0% |
| | Prompt Defense | 8.3% | 100.0% | 16.7% | 91.7% | 33.3% | 83.3% | 25.0% |
| | **+ Our Verifier** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** |
| **Llama-3.1-8B** | Baseline | 25.0% | 91.7% | 41.7% | 83.3% | 58.3% | 66.7% | 75.0% |
| | Prompt Defense | 16.7% | 91.7% | 25.0% | 91.7% | 41.7% | 83.3% | 25.0% |
| | **+ Our Verifier** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** |
| **GPT-4o** | Baseline | 8.3% | 100.0% | 25.0% | 91.7% | 33.3% | 83.3% | 25.0% |
| | Prompt Defense | 8.3% | 100.0% | 16.7% | 91.7% | 25.0% | 91.7% | 0.0% |
| | **+ Our Verifier** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** | **100.0%** | **0.0%** |

*All percentages represent exact, reproducible discrete counts over the 12 tasks per language test set.*

---

## 📖 Citation

```bibtex
@inproceedings{refman2027leastprivilege,
  author    = {Refman, Arya},
  title     = {Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection},
  booktitle = {Proceedings of the Annual Meeting of the Association for Computational Linguistics (ACL)},
  year      = {2027}
}
```
