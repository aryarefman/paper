# Reading Notes: Runtime Trust in Agentic Systems & AutoCodeRover

* **Authors:** Prof. Abhik Roychoudhury's Research Group (NUS School of Computing)
* **Core Topic:** Automated software repair, program synthesis, and runtime assurance for autonomous LLM agents.

---

## 1. Key Conceptual Insights
* **The Vulnerability of Neural Autonomy:** LLMs generating code or invoking APIs cannot be treated as trusted binaries. They require runtime sandboxing, policy checks, and formal verification.
* **AutoCodeRover Architecture:** Combines LLMs with abstract syntax tree (AST) code search and test-driven validation loops to repair GitHub issues autonomously. In May 2026, integrated into commercial static analysis (SonarQube).
* **The 2026 Singapore Consensus on AI Safety:** Outlined ten foundational principles for agentic systems:
  1. *Least Privilege:* Agents should operate with minimum viable access.
  2. *Auditability:* Action trajectories must be verifiable.
  3. *Interruptibility:* Systems must fail-safe upon abnormal behavior.

---

## 2. Direct Alignment with Our Proposal
* Our project applies the principle of **runtime assurance and least privilege** to cross-lingual agent tool execution.
* By building a deterministic verifier that intercepts API calls, we implement the *Least Privilege* and *Interruptibility* tenets of the Singapore Consensus.
