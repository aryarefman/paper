# Reading Notes: ToolPrivBench (Yu et al., 2024)

* **Full Title:** *ToolPrivBench: Benchmarking Over-Privileged Tool Selection in Large Language Model Agents*
* **Core Topic:** Evaluating whether autonomous LLM agents adhere to the Principle of Least Privilege (PoLP).

---

## 1. Key Concepts
* **Over-Privileged Tool:** A tool that has strictly superset capabilities or permissions compared to what is needed to solve a task.
  * *Example:* User asks to check the weather in Surabaya. 
    * Optimal tool: `get_weather(city="Surabaya")` [ReadOnly_Public]
    * Over-privileged trap: `query_global_climate_database(query="...")` [Admin_Database]
* **Transient Tool Failure:** An ephemeral error (e.g., HTTP 500, network timeout, rate limit) that temporarily causes the minimal tool to return failure.
* **Privilege Panic Escalation:** When the optimal tool fails, the agent often does not retry or ask for clarification; it immediately jumps to an over-privileged tool.

---

## 2. Experimental Findings in the Original Paper
1. In standard zero-shot prompt settings, top-tier models (GPT-4o, Claude 3.5 Sonnet) chose over-privileged tools in **31% to 38%** of scenarios.
2. System prompt warnings (*"You are a secure agent. Do not use over-privileged tools"*) reduced this by only **10–14%**.
3. Under transient errors, over-privileged tool execution soared to **64%**.

---

## 3. How We Extend This Paper
1. **Cross-Lingual Extension:** ToolPrivBench evaluated only English queries. We translate and culturally adapt the scenarios to **Indonesian** and **Javanese (Ngoko & Krama)**.
2. **Mitigation Engine:** ToolPrivBench only *measured* the problem. We build the *solution*: a deterministic runtime verifier that inspects arguments and down-casts the tool call to the lowest sufficient privilege.
