import base64
import json
import re
from collections.abc import Generator

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:e4b"

from ontology import _DRUG_CONFIG

_CATEGORY_ENUM = list(_DRUG_CONFIG.keys()) + ["unknown"]
_CATEGORY_LINES = "\n".join(
    f"  {key:<18} → {cfg['description']}"
    for key, cfg in _DRUG_CONFIG.items()
) + "\n  unknown            → 분류 불명"

SYSTEM_INSTRUCTION = (
    "You are a drug storage temperature classifier. "
    "Analyze the provided image and/or drug name and classify it into exactly one category.\n\n"
    f"Category definitions:\n{_CATEGORY_LINES}\n\n"
    "Respond in JSON only."
)

PROMPT = (
    "Analyze the image and fill in the following fields:\n"
    "- image_text: ONLY the exact text visible on the packaging/label. "
    "Copy it verbatim. Do NOT describe or explain. If no text is visible, use empty string.\n"
    "- form: Physical form of the drug/device.\n"
    "- color: Primary color.\n"
    "- 약품명: Final drug name conclusion.\n"
    "- 계열: One category from the list defined in your instructions.\n"
    "- intuition: Drug name or category in 3 words or less. No explanation."
)


def _encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def _parse_response(text: str) -> dict | None:
    cleaned = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{.*?\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


_VALID_CATEGORIES = set(_CATEGORY_ENUM)

_VALID_FORMS   = {"vial", "pen", "syringe", "tablet", "bottle", "package", "other"}
_VALID_COLORS  = {"white", "transparent", "yellow", "orange", "red", "blue", "green", "pink", "purple", "brown", "amber", "other"}


def _normalize(parsed: dict, fallback_name: str) -> dict:
    drug_name = (
        parsed.get("약품명") or parsed.get("drug_name") or parsed.get("name")
        or fallback_name or "알 수 없음"
    )

    raw_category = parsed.get("계열") or parsed.get("category") or None
    category = str(raw_category).strip().lower() if raw_category else None
    if category not in _VALID_CATEGORIES:
        category = None

    raw_form = str(parsed.get("form") or "other").strip().lower()
    form = raw_form if raw_form in _VALID_FORMS else "other"

    image_text = parsed.get("image_text") or ""
    intuition  = parsed.get("intuition") or ""
    raw_color  = str(parsed.get("color") or "other").strip().lower()
    color      = raw_color if raw_color in _VALID_COLORS else "other"

    return {
        "drug_name":  str(drug_name),
        "category":   category,
        "image_text": str(image_text),
        "intuition":  str(intuition),
        "form":       form,
        "color":      color,
    }


def stream_query_ollama(
    image_bytes: bytes | None,
    text_input:  str | None,
    ocr_text:    str = "",
    scene_repr:  str | None = None,
) -> Generator[dict, None, None]:
    user_part  = f"약품명: {text_input}\n" if text_input else ""
    ocr_part   = f"OCR 추출 텍스트: {ocr_text}\n" if ocr_text else ""
    scene_part = f"{scene_repr}\n\n" if scene_repr else ""
    prompt = user_part + ocr_part + scene_part + "\n" + PROMPT
    payload: dict = {
        "model": MODEL_NAME,
        "system": SYSTEM_INSTRUCTION,
        "prompt": prompt,
        "stream": True,
        "think": False,
        "format": {
            "type": "object",
            "properties": {
                "image_text": {"type": "string"},
                "form":       {"type": "string", "enum": ["vial", "pen", "syringe", "tablet", "bottle", "package", "other"]},
                "color":      {"type": "string", "enum": ["white", "transparent", "yellow", "orange", "red", "blue", "green", "pink", "purple", "brown", "amber", "other"]},
                "약품명":     {"type": "string"},
                "계열":       {"type": "string", "enum": _CATEGORY_ENUM},
                "intuition":  {"type": "string"},
            },
            "required": ["image_text", "intuition", "form", "color", "약품명", "계열"],
        },
    }
    if image_bytes:
        payload["images"] = [_encode_image(image_bytes)]

    try:
        with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120) as response:
            if not response.ok:
                try:
                    error_msg = response.json().get("error", response.text)
                except Exception:
                    error_msg = response.text
                yield {"type": "error", "text": f"Ollama 오류: {error_msg}"}
                return

            full_text = ""
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if chunk := data.get("thinking", ""):
                    yield {"type": "thinking", "text": chunk}
                if chunk := data.get("response", ""):
                    full_text += chunk
                    yield {"type": "chunk", "text": chunk}
                if data.get("done"):
                    break

            parsed = _parse_response(full_text)
            if parsed:
                yield {
                    "type": "result",
                    **_normalize(parsed, fallback_name=text_input or ""),
                    "raw_response": full_text,
                    "error": None,
                }
            else:
                yield {
                    "type": "result",
                    "drug_name":  text_input or "파싱 실패",
                    "category":   None,
                    "image_text": "",
                    "intuition":  "",
                    "form":       "other",
                    "color":      "",
                    "raw_response": full_text,
                    "error": "JSON 파싱 실패",
                }

    except requests.exceptions.ConnectionError:
        yield {"type": "error", "text": "Ollama 서버 연결 실패 (localhost:11434)"}
    except requests.exceptions.Timeout:
        yield {"type": "error", "text": "응답 시간 초과 (120초)"}
    except Exception as e:
        yield {"type": "error", "text": f"처리 오류: {e}"}
