# Literature Review: Trustworthy Agentic AI & Multilingual Least-Privilege Execution

This document provides a systematic review of the literature supporting the research:  
**"Least-Privilege Guardrails for Multilingual LLM Agents: A Cross-Lingual Verifier Against Over-Privileged Tool Selection (English, Indonesian, Javanese)"**.

---

## 1. Taxonomy of Related Work

Research in this domain spans four intersecting pillars:
1. **Agent Tool Authorization & Over-Privilege:** Vulnerabilities where LLMs select actions with unnecessarily high privilege scopes.
2. **Multilingual LLM Evaluation & Robustness:** Performance drops and semantic distortion when querying models outside English.
3. **Southeast Asian Foundation Models:** Regional models (e.g., SEA-LION) and their socioethical alignment.
4. **Runtime Verification & Software Assurance for Agents:** Ensuring deterministic safety guarantees around stochastic neural outputs.

```
       [Agent Tool Security & Over-Privilege]
      (ToolPrivBench, FORTIS, MiniScope, Progent)
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    OUR RESEARCH GAP                         │
│  "Does cross-lingual transfer into low-resource Austronesian │
│   languages (Indonesian, Javanese) exacerbate over-         │
│   privileged tool selection, and can a mechanistic verifier │
│   provably downgrade privileges under transient faults?"    │
└─────────────────────────────────────────────────────────────┘
                         ▲
                         │
    [Multilingual LLM Robustness & SEA AI]
   (MAPS, Lumen-bench, SEA-LION, SEA-HELM)
```

---

## 2. Comparative Matrix of Key Literature

| Paper / System | Venue / Year | Primary Languages | Focus Area | Tested Privilege Escalation? | Tested Transient Tool Faults? | Proposed Defense Mechanism |
| :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| **ToolPrivBench** (Yu et al.) | arXiv 2024 | English only | Over-privileged tool choice | Yes | Yes (transient) | Prompt-based instructions (partially effective) |
| **FORTIS** (Zhang et al.) | NeurIPS 2024 | English only | Over-privilege in agent skills | Yes | No | Static permission scanning |
| **MiniScope** (Chen et al.) | USENIX Sec 2024 | English only | Least-privilege authorization | Yes | No | Policy-based proxy |
| **MAPS** (Huang et al.) | ACL 2024 | 11 Languages (En, Zh, Es...) | Agent task & security degradation | No | No | None (Pure benchmark) |
| **Lumen-bench** | arXiv 2024 | 5 Languages | Tool-calling ethics & safety | No | No | Benchmark |
| **SEA-LION / SEA-HELM** | ACL 2024 | SEA (Id, Vi, Th, Tl, Ms) | Regional foundation models | No | No | Alignment training |
| **AutoCodeRover** (Zhang et al.) | ISSTA 2024 | English | Autonomous program repair & trust | No | No | Iterative AST search & verification |
| **OUR WORK** | Target: ACL/ICSE 2027 | **English, Indonesian, Javanese** | **Cross-lingual over-privilege & runtime guardrails** | **YES** | **YES** | **Deterministic Lattice-Based Mechanistic Verifier** |

---

## 3. Detailed Syntheses of Foundational Papers

### 3.1 Over-Privilege Vulnerability
* **ToolPrivBench (Yu et al., 2024):** Demonstrated that when provided with a toolset containing both minimal and over-privileged tools (e.g., `read_single_mail` vs. `read_entire_inbox`), state-of-the-art models (GPT-4, Claude-3.5) pick the over-privileged tool up to **38.4% of the time**. Crucially, when transient errors (HTTP 504 timeouts) are simulated on the minimal tool, models panic and escalate to high-privilege tools in over **60% of cases**.
* **Limitation of Prior Work:** The benchmark was evaluated entirely in English with high-resource Western naming conventions.

### 3.2 Multilingual Tool Degradation
* **"Lost in Execution" (2024) & MAPS (2024):** Showed that multilingual tool execution suffers from *semantic distortion*. Even when the LLM generates a semantically correct answer in text, its function-calling API calls suffer from dropped parameters, hallucinated keys, and schema mismatches when translating non-English user intent into English-named tool schemas.
* **Our Hypothesis:** This semantic confusion creates an "intent ambiguity buffer" where the agent, unsure whether a narrow query fits a narrow tool, defaults to the broadest available tool to ensure task completion.

### 3.3 Southeast Asian Context (SEA-LION & Javanese)
* **AI Singapore SEA-LION Project (2024–2026):** Developed regional language models specifically tuned for Indonesian, Malay, Thai, and Vietnamese. However, SEA-HELM's safety evaluation does not incorporate agentic function-calling permissions or regional languages with complex honorific registers such as **Javanese (Basa Jawa: Ngoko vs. Krama)**.
* In Javanese, polite speech (*krama*) uses indirect expressions and passive voice that obscure grammatical objects, causing standard semantic parsers to miscalculate whether a query refers to an individual record or a global database.

---

## 4. Key Takeaways for Thesis Methodology

1. **Do not rely on prompt-based self-reflection:** ToolPrivBench proved that adding *"Please only pick the least privileged tool"* in system prompts only reduces over-privilege by ~12%, and collapses completely under error conditions.
2. **Enforce deterministically via Lattice Theory:** The verifier must operate outside the LLM's stochastic decoding loop, inspecting parameter arguments and mapping them through a mathematical partial order.
