import json
import os
from typing import List, Dict, Any

from llama_cpp import Llama

from ..config import Config


def resolve_model_path() -> str:
    models_dir = Config.MODELS_DIR
    os.makedirs(models_dir, exist_ok=True)
    for name in Config.PREFERRED_GGUF:
        candidate = os.path.join(models_dir, name)
        if os.path.isfile(candidate):
            return candidate
    raise FileNotFoundError(
        f"No GGUF model found in {models_dir}. Place one of: {', '.join(Config.PREFERRED_GGUF)}"
    )


class MedicalDialogueAnalyzer:
    def __init__(self) -> None:
        model_path = resolve_model_path()
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            chat_format="chatml",
        )

    def _build_messages(self, dialogue: str, example_dialogue: str | None, example_json_output: Dict | None) -> List[Dict[str, str]]:
        system_prompt = (
            "Bạn là AI phân tích hội thoại y khoa. \n"
            "Trả về DUY NHẤT một JSON hợp lệ (object) với CHÍNH XÁC 2 khóa: 'symptom' (array string) và 'diagnosis' (string).\n"
            "Không thêm khóa nào khác. Không thêm lời giải thích, tiêu đề hay văn bản ngoài JSON."
        )

        if not example_dialogue:
            example_dialogue = (
                "bác sĩ ơi em dạo này hay bị đau đầu, có lúc đau âm ỉ nhưng cũng có lúc nó nhói mạnh lắm, "
                "hôm qua em đo thì thấy sốt khoảng ba mươi tám rưỡi độ, người cứ nóng bừng lên. "
                "ngoài ra thì em còn thấy mệt mỏi, ăn uống không ngon miệng, thỉnh thoảng hơi buồn nôn nữa, "
                "nhiều khi nằm nghỉ cũng không đỡ, đầu óc cứ quay quay. "
                "à em còn hay bị mất ngủ mấy hôm nay, chắc cũng vì cái đau đầu với sốt này làm khó chịu quá nên không ngủ được."
            )

        if not example_json_output:
            example_json_output = {
                "symptom": ["đau đầu", "sốt 38.5 độ C", "buồn nôn"],
                "diagnosis": "Nghi ngờ nhiễm virus.",
            }

        user_prompt = f"""Hãy làm theo ví dụ sau để hoàn thành nhiệm vụ.

### VÍ DỤ ###
---
#### Cuộc đối thoại ví dụ:
{example_dialogue}

#### JSON Output ví dụ:
{json.dumps(example_json_output, ensure_ascii=False)}
---

### NHIỆM VỤ ###
BÂY GIỜ, hãy áp dụng tương tự cho cuộc đối thoại sau đây.

#### Cuộc đối thoại cần phân tích:
{dialogue}

#### Yêu cầu Output:
Cung cấp output là một chuỗi JSON hợp lệ với đúng 2 khóa: "symptom" (array string), "diagnosis" (string).\n
Không thêm khóa nào khác. Trả về DUY NHẤT JSON, không kèm văn bản nào khác.
"""

        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

    def analyze(self, text: str, *, example_dialogue: str | None = None, example_json_output: Dict | None = None, max_tokens: int = 512, temperature: float = 0.2) -> Dict[str, Any]:
        messages = self._build_messages(text, example_dialogue, example_json_output)
        output = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            response_format={"type": "json_object"},
        )

        content = output["choices"][0]["message"]["content"].strip()
        parsed: Any = None
        try:
            parsed = json.loads(content)
        except Exception:
            parsed = None

        def normalize_keys(obj: Any) -> Dict[str, Any]:
            import difflib
            # Defaults
            result_symptom: list[str] = []
            result_diagnosis: str = "Unknown"

            if not isinstance(obj, dict):
                return {"symptom": result_symptom, "diagnosis": result_diagnosis}

            keys_lower = {k.lower(): k for k in obj.keys()}

            def pick_key(target: str) -> str | None:
                if target in keys_lower:
                    return keys_lower[target]
                matches = difflib.get_close_matches(target, keys_lower.keys(), n=1, cutoff=0.8)
                if matches:
                    return keys_lower[matches[0]]
                return None

            s_key = pick_key("symptom")
            d_key = pick_key("diagnosis")

            # Extract
            symptoms_raw = obj.get(s_key) if s_key else []
            diagnosis_raw = obj.get(d_key) if d_key else "Unknown"

            # Coerce types
            if isinstance(symptoms_raw, str):
                result_symptom = [symptoms_raw.strip()] if symptoms_raw.strip() else []
            elif isinstance(symptoms_raw, list):
                cleaned: list[str] = []
                for it in symptoms_raw:
                    if it is None:
                        continue
                    s = str(it).strip()
                    if s:
                        cleaned.append(s)
                result_symptom = cleaned
            else:
                result_symptom = []

            if isinstance(diagnosis_raw, str):
                result_diagnosis = diagnosis_raw.strip() or "Unknown"
            else:
                result_diagnosis = str(diagnosis_raw).strip() or "Unknown"

            return {"symptom": result_symptom, "diagnosis": result_diagnosis}

        sanitized = normalize_keys(parsed)
        return {"raw": content, "json": sanitized}


