# Research Title Candidates: NUS Internship & ITS Tugas Akhir

This document outlines the primary and alternative research directions curated for the **NUS SoC Summer Research Internship (SRI)** and **ITS Tugas Akhir (Bachelor's Thesis)**, with long-term viability for **Singapore PhD (SINGA / NUS Research Scholarship)** applications.

---

## 1. Selected Research Direction (CHAMPION)

> **"Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection (English, Indonesian, Javanese)"**
> 
> * **Status:** Selected as Primary Champion Topic
> * **Field:** Trustworthy Agentic AI, Runtime Verification, Multilingual NLP, Access Control
> * **Target NUS Labs:** 
>   1. Software Engineering Research Group (**Prof. Abhik Roychoudhury**) — Focus on runtime trust, program repair, and agentic software assurance.
>   2. Web IR / NLP Group (WING) (**Prof. Min-Yen Kan**) — Focus on foundation model socioethical alignment and multilingual evaluation.
> * **Target ITS Bidang Minat:** 
>   1. Lab RPL (Software Engineering) — Focus on API authorization and runtime verification.
>   2. Lab KCV / AIL (Artificial Intelligence) — Focus on cross-lingual intent preservation.
>   3. Lab NCC (Cybersecurity) — Focus on Principle of Least Privilege (PoLP) and access control.

---

## 2. Comprehensive Comparison Table

| Feature / Metric | **Candidate 1 (Selected Champion)** | **Candidate 2 (Backup A)** | **Candidate 3 (Backup B)** |
| :--- | :--- | :--- | :--- |
| **Research Title** | **Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection (English, Indonesian, Javanese)** | **Cross-Lingual Hallucination Mitigation in Multilingual Retrieval-Augmented Generation for Regional Public-Service Systems** | **Automated Runtime Fuzzing and Stress-Testing of Tool-Using LLM Agents Under Low-Resource Linguistic Perturbations** |
| **Primary Domain** | Trustworthy Agentic AI & Runtime Verification | Multilingual NLP & Retrieval-Augmented Generation (RAG) | Automated Software Engineering & Agent Reliability Testing |
| **The Core Problem / Gap** | Agents pick overly permissive tools (e.g., `db_delete_all` instead of `db_read_record`) when prompted in non-English due to intent ambiguity. | RAG pipelines hallucinate or retrieve mismatched legal/civic data when queries transition between regional dialects and English. | LLM agent tool-call execution pipelines crash or exhibit unhandled exceptions under morphology-rich regional language inputs. |
| **Engineering Contribution (The Method)** | **Deterministic Least-Privilege Policy Engine:** A schema-constrained lattice that intercepts calls, checks arguments, and auto-downgrades privileges. | **Attributed Cross-Lingual RAG Guard:** A dual-encoder factuality verifier validating source-attribution across Indonesian/regional texts. | **Metamorphic Agent Fuzzer:** An automated test generator that mutates prompts across dialects to discover execution faults and security leaks. |
| **Target NUS SoC Labs** | • **Prof. Abhik Roychoudhury** (Software Engineering / Agent Trust)<br>• **Prof. Min-Yen Kan** (WING / Multilingual NLP) | • **Prof. Min-Yen Kan** (WING / Information Retrieval)<br>• **Prof. Stephane Bressan** (Data Science & NLP) | • **Prof. Abhik Roychoudhury** (Automated Program Repair & Testing - AutoCodeRover) |
| **Target ITS Lab (Bidang Minat)** | • **RPL** (Software Systems & Security)<br>• **KCV/AIL** (Agent Reasoning)<br>• **NCC** (Access Control & Security) | • **KCV/AIL** (NLP & Semantic Search)<br>• **Sistem Informasi** (Enterprise Information Systems) | • **RPL** (Automated Software Testing & QA)<br>• **NCC** (System Security Testing) |
| **Compute & Hardware Feasibility** | **Extremely High:** Software-only. Evaluated on open-weight 7B/8B models (SEA-LION, Qwen 2.5, Llama 3.1) or APIs on a single GPU/laptop. | **High:** Requires vector databases (Chroma/Milvus) and small embedding models. Negligible GPU requirements. | **Extremely High:** Black-box/gray-box fuzzing pipeline. Can run completely on standard CPU workstations and API keys. |
| **10–12 Week Execution Risk** | **Low:** Benchmark adaptation (150 tasks) + rule-based verifier layer can be finished and tested in 2.5 months. | **Low to Moderate:** Depends on dataset curation quality for public-service/legal documents. | **Low:** Generating linguistic mutations and logging crash/leak rates is straightforward to execute. |
| **Direct PhD (S3) Scaling Potential** | **Exceptional:** Expands into 4-year formal verification, type systems for agents, and multi-agent access control protocols. | **Good:** Expands into neuro-symbolic knowledge graphs and generalized cross-lingual grounding. | **High:** Expands into automated bug-finding, symbolic execution, and self-healing agent architectures. |
