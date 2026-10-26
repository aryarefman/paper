# Reading Notes: SEA-LION & SEA-HELM (AI Singapore, 2024–2026)

* **Full Title:** *SEA-LION: Southeast Asian Languages in One Network*
* **Core Topic:** Foundation language models pretrained on Southeast Asian text corpora (Indonesian, Malay, Thai, Vietnamese, Filipino, Tamil).

---

## 1. Relevance to Our Research
* **Why SEA-LION?** 
  * It is the flagship regional model developed in Singapore by AI Singapore (AISG) in partnership with NUS and NTU researchers.
  * It represents the primary open-weights model targeted for deployment in Southeast Asian governmental and enterprise infrastructure.
* **The Gap in SEA-LION / SEA-HELM:**
  * SEA-HELM benchmarks linguistic competence (MMLU translation, QA, sentiment) and basic safety guardrails (toxicity, bias).
  * **Gap:** It does not benchmark **agentic tool-use security** or **principle of least privilege**.
  * **Gap:** It does not benchmark **Javanese**, despite Javanese having ~80 million speakers in the ASEAN region.

---

## 2. Technical Setup for Our Experiments
* **Target Models:**
  * `aisingapore/sea-lion-7b-instruct`
  * `Qwen/Qwen2.5-7B-Instruct`
  * `meta-llama/Meta-Llama-3.1-8B-Instruct`
* **Inference Strategy:**
  * Local inference via Hugging Face `transformers` or `vLLM` with 4-bit/8-bit quantization to fit on consumer GPUs (RTX 3090/4090).
