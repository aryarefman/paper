# Presentation Deck: Research Proposal for NUS SRI & ITS Tugas Akhir

**Title:** Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection  
**Presenter:** Arya Refman (Institut Teknologi Sepuluh Nopember)  
**Host Institution:** National University of Singapore (School of Computing)

---

### Slide 1: Title & Motivation
* **Title:** Least-Privilege Guardrails for Multilingual LLM Agents
* **The Rise of Autonomous Agents:** From chat assistants to autonomous action-takers (API execution, database transactions).
* **The Vulnerability:** LLM agents frequently pick "over-privileged" tools (e.g., global admin operations instead of single-record reads).
* **The Question:** What happens when agents are commanded in Southeast Asian languages?

---

### Slide 2: The Core Problem: Cross-Lingual Intent Ambiguity
* English benchmarks (*ToolPrivBench*) show a ~35% over-privilege rate.
* In Indonesian and Javanese, semantic dispersion and polite registers (*krama/ngoko*) introduce intent ambiguity.
* Agents default to broader, higher-privilege tools as an uncalibrated heuristic to avoid failure.

---

### Slide 3: Research Questions
* **RQ1:** Does cross-lingual transfer into Indonesian and Javanese increase the Over-Privilege Rate ($OPR$)?
* **RQ2:** Can a deterministic, schema-constrained verifier downgrade over-privileged tools without sacrificing Task Completion Rate ($TCR$)?
* **RQ3:** Does the verifier prevent panic privilege escalation under transient tool timeouts (HTTP 504)?

---

### Slide 4: Proposed Methodology
* **Mathematical Foundation:** Lattice Theory for permission ordering:
  $$\text{ReadOnly\_Single} \sqsubset \text{ReadOnly\_Batch} \sqsubset \text{Write} \sqsubset \text{Admin}$$
* **Deterministic Guardrail:**
  1. Intercepts candidate tool call.
  2. Inspects argument scope (e.g., verifying single user ID vs. wildcard).
  3. Downgrades candidate tool to minimal sufficient equivalent.
  4. Quarantines transient errors to prevent escalation.

---

### Slide 5: Experimental Setup & Benchmarks
* **Benchmark:** *ToolPrivBench-SEA* (150 tasks translated & validated via Cohen's Kappa agreement).
* **Models:** SEA-LION-7B, Qwen-2.5-7B, Llama-3.1-8B, GPT-4o.
* **Metrics:** Over-Privilege Rate ($OPR$), Task Completion Rate ($TCR$), Latency Overhead ($\Delta t < 50\text{ms}$).

---

### Slide 6: Expected Contributions & Timeline
* **Deliverables:**
  1. First cross-lingual over-privilege benchmark for Southeast Asian languages.
  2. Open-source deterministic least-privilege verification middleware.
  3. Submission-ready conference paper (ACL / ICSE 2027) & ITS Tugas Akhir.
* **10-Week Timeline:**
  * W1–W3: Benchmark translation & native speaker validation.
  * W4–W5: Baseline vulnerability experiments across models.
  * W6–W8: Guardrail implementation & transient error testing.
  * W9–W10: Evaluation & paper drafting.
