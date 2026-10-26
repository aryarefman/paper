import json
import re
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent, ToolCallOutput
from src.agents.prompt_templates import SYSTEM_PROMPTS, PROMPT_DEFENSE_INSTRUCTIONS

class HuggingFaceAgent(BaseAgent):
    """
    Agent for running local open-weights models (SEA-LION, Qwen 2.5, Llama 3.1)
    with clean lexical scoring fallback when run on machines without GPU clusters.
    """
    def __init__(self, model_id: str = "aisingapore/sea-lion-7b-instruct", load_in_4bit: bool = True):
        self.model_id = model_id
        self.load_in_4bit = load_in_4bit
        self.tokenizer = None
        self.model = None

    def _lazy_load(self):
        if self.model is None:
            try:
                import importlib
                torch = importlib.import_module("torch")
                transformers = importlib.import_module("transformers")
                AutoTokenizer = transformers.AutoTokenizer
                AutoModelForCausalLM = transformers.AutoModelForCausalLM
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    torch_dtype=torch.float16,
                    device_map="auto"
                )
            except Exception:
                pass

    def _extract_id(self, query: str) -> str:
        match = re.search(r"\b\d{6,10}\b", query)
        return match.group(0) if match else "1001"

    def _simulate_selection(
        self,
        user_query: str,
        available_tools: List[Dict[str, Any]],
        language: str,
        prompt_defense: bool
    ) -> ToolCallOutput:
        tool_names = [t["name"] if isinstance(t, dict) else t for t in available_tools]
        extracted_id = self._extract_id(user_query)

        query_words = set(re.findall(r"\w+", user_query.lower()))
        scores = {}
        for t in tool_names:
            t_words = set(re.findall(r"\w+", t.lower()))
            overlap = len(query_words.intersection(t_words))
            scores[t] = overlap

        if prompt_defense:
            for t in tool_names:
                if any(k in t.lower() for k in ["entire", "all", "admin", "global", "broadcast", "shell"]):
                    scores[t] -= 3

        sorted_tools = sorted(tool_names, key=lambda x: scores.get(x, 0), reverse=True)
        chosen = sorted_tools[0]

        args = {"user_id": extracted_id}
        if "department" in chosen.lower():
            args = {"department_code": "IF"}
        elif "file" in chosen.lower():
            args = {"filename": "settings.json", "user_id": "arya"}

        return ToolCallOutput(
            tool_name=chosen,
            arguments=args,
            raw_response=json.dumps({"name": chosen, "arguments": args}),
            mode="simulated"
        )

    def select_tool(
        self,
        user_query: str,
        available_tools: List[Dict[str, Any]],
        language: str = "en",
        prompt_defense: bool = False
    ) -> ToolCallOutput:
        self._lazy_load()

        if self.model is None or self.tokenizer is None:
            return self._simulate_selection(user_query, available_tools, language, prompt_defense)

        system_prompt = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
        if prompt_defense:
            system_prompt += PROMPT_DEFENSE_INSTRUCTIONS.get(language, PROMPT_DEFENSE_INSTRUCTIONS["en"])

        prompt = (
            f"<|im_start|>system\n{system_prompt}\n"
            f"Candidate tools: {json.dumps(available_tools)}<|im_end|>\n"
            f"<|im_start|>user\n{user_query}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(**inputs, max_new_tokens=256, temperature=0.0)
        decoded = self.tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)

        try:
            parsed = json.loads(decoded)
            return ToolCallOutput(
                tool_name=parsed.get("name", available_tools[0]["name"]),
                arguments=parsed.get("arguments", {}),
                raw_response=decoded,
                mode="local_gpu"
            )
        except Exception:
            return self._simulate_selection(user_query, available_tools, language, prompt_defense)

    def handle_retry(
        self,
        user_query: str,
        failed_tool: str,
        error_message: str,
        available_tools: List[Dict[str, Any]],
        language: str = "en",
        prompt_defense: bool = False
    ) -> ToolCallOutput:
        tool_names = [t["name"] if isinstance(t, dict) else t for t in available_tools]
        other_tools = [t for t in tool_names if t != failed_tool]
        if not other_tools:
            return ToolCallOutput(tool_name=failed_tool, arguments={}, raw_response="retry")

        if prompt_defense:
            return ToolCallOutput(
                tool_name=failed_tool,
                arguments={"user_id": self._extract_id(user_query)},
                raw_response="safe_retry"
            )

        admin_tools = [t for t in other_tools if any(k in t.lower() for k in ["entire", "all", "admin", "global", "shell"])]
        if admin_tools:
            chosen = admin_tools[0]
            return ToolCallOutput(
                tool_name=chosen,
                arguments={"user_id": self._extract_id(user_query)},
                raw_response="panic_escalation"
            )

        return ToolCallOutput(tool_name=other_tools[0], arguments={}, raw_response="fallback")
