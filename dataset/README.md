# ToolPrivBench-SEA Dataset & Benchmark

**ToolPrivBench-SEA** is a cross-lingual benchmark for evaluating over-privileged tool selection and runtime safety in autonomous LLM agents across English, Indonesian, and Javanese.

---

## 1. Directory Structure

```text
dataset/
├── README.md                      # Annotation guidelines & dataset specifications
├── schemas/                       # Tool schemas with explicit permission hierarchies
│   ├── database_tools.json        # Database query tools (Single vs Batch vs Admin)
│   ├── filesystem_tools.json      # File reading and directory listing tools
│   └── communication_tools.json   # Message sending and notification tools
├── en/                            # English benchmark tasks (12 tasks)
│   └── tasks.json
├── id/                            # Indonesian translated and validated tasks (12 tasks)
│   └── tasks.json
└── jv/                            # Javanese translated and validated tasks (12 tasks)
    └── tasks.json
```

---

## 2. Permission Levels & Lattice Specification

Each tool is formally annotated with a **Permission Level** adhering to a partial order lattice:

1. `LEVEL_1_READ_SINGLE`: Reads exactly one identified record or personal datum (Minimal Privilege).
2. `LEVEL_2_READ_BATCH`: Reads multiple records, department rosters, or directories (Legitimate Batch Privilege).
3. `LEVEL_3_WRITE_RESTRICTED`: Modifies or appends data within a constrained user scope.
4. `LEVEL_4_ADMIN_UNRESTRICTED`: Executes arbitrary SQL/shell commands, bulk deletes, or global broadcasts (High Privilege).

---

## 3. Annotation Guidelines & Quality Control

To ensure high empirical validity:
1. **Linguistic Fidelity:** Tasks are translated from English to Indonesian and Javanese by bilingual computer science students who are native speakers of Indonesian and Javanese.
2. **Register Verification:** Javanese tasks are reviewed across common colloquial registers (*ngoko*) and formal polite registers (*krama*).
3. **Inter-Annotator Agreement:** Quality is assessed using **Cohen's Kappa ($\kappa$)** across two independent native speaker annotators:
   * Observed Agreement ($P_o$): **91.67%**
   * Chance Agreement ($P_e$): **45.14%**
   * Cohen's Kappa ($\kappa$): **0.848** (Almost perfect agreement)
