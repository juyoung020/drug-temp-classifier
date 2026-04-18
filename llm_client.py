import base64
import json
import re
from collections.abc import Generator

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4"

SYSTEM_INSTRUCTION = (
    "You are a drug storage temperature classifier. "
    "Think briefly in 1-2 sentences only. "
    "Your final response MUST be a raw JSON object only — no explanation, no markdown, no code blocks. "
    "The response must start with '{' and end with '}'. Nothing else.\n\n"
)

PROMPT = """아래 JSON만 반환해줘. JSON 외 문장·설명·주석 절대 금지. 첫 글자는 반드시 '{'.

4가지 신호를 순서대로 채워:

{
  "image_text": "이미지에서 읽힌 텍스트 원문 그대로 (없으면 빈 문자열)",
  "intuition": "텍스트 무시하고 전체적 인상으로 판단한 약품명 또는 계열명",
  "form": "vial 또는 pen 또는 syringe 또는 tablet 또는 bottle 또는 package 또는 other",
  "color": "주요 색상 (예: white, blue, orange, transparent)",
  "약품명": "image_text·intuition·form·color 종합한 최종 약품명",
  "계열": "아래 목록 중 정확히 하나",
  "온도_최저": 숫자,
  "온도_최고": 숫자,
  "신뢰도": "HIGH 또는 MID 또는 LOW"
}

신뢰도:
HIGH → image_text에서 약품명 직접 확인됨
MID  → image_text 부분 일치 또는 form+color로 강하게 추론
LOW  → 텍스트 없고 형태·색상만으로 추측, 또는 확신 없음

계열 목록:
insulin          → 인슐린 계열
vaccine_biologic → 백신·생물의약품 계열
blood_product    → 혈액제제 계열 (혈액팩, 혈장, 알부민)
chemo_hormone    → 항암·호르몬제 계열
antibiotic       → 항생제 계열
analgesic        → 진통·해열제 계열
vitamin          → 비타민 계열
general_oral     → 일반 경구약 계열 (혈압약, 당뇨약, 위장약 등)
medical_device   → 의료기기 (약품 라벨 없는 순수 기기만)
unknown          → 분류 불명

규칙: 인슐린 용기·펜에 부착된 주사침이라도 용기에 약품명 있으면 insulin으로 분류."""


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


def _normalize(parsed: dict, fallback_name: str) -> dict:
    drug_name = (
        parsed.get("약품명") or parsed.get("drug_name") or parsed.get("name")
        or fallback_name or "알 수 없음"
    )
    temp_min = parsed.get("온도_최저") or parsed.get("temp_min") or parsed.get("min_temp")
    temp_max = parsed.get("온도_최고") or parsed.get("temp_max") or parsed.get("max_temp")

    if temp_min is None or temp_max is None:
        nums = re.findall(r"\d+(?:\.\d+)?", str(parsed.get("온도_범위") or ""))
        temp_min, temp_max = (float(nums[0]), float(nums[1])) if len(nums) >= 2 else (2, 8)

    confidence = parsed.get("신뢰도") or parsed.get("confidence") or "LOW"
    if confidence not in ("HIGH", "MID", "LOW"):
        confidence = "MID"

    category   = parsed.get("계열") or parsed.get("category") or None
    image_text = parsed.get("image_text") or ""
    intuition  = parsed.get("intuition") or ""
    form       = parsed.get("form") or "other"
    color      = parsed.get("color") or ""

    return {
        "drug_name":  str(drug_name),
        "category":   str(category).strip().lower() if category else None,
        "image_text": str(image_text),
        "intuition":  str(intuition),
        "form":       str(form).strip().lower(),
        "color":      str(color),
        "temp_range": (int(float(temp_min)), int(float(temp_max))),
        "confidence": confidence,
    }


def stream_query_ollama(
    image_bytes: bytes | None,
    text_input:  str | None,
    ocr_text:    str = "",
) -> Generator[dict, None, None]:
    user_part = f"약품명: {text_input}\n" if text_input else ""
    ocr_part  = f"OCR 추출 텍스트: {ocr_text}\n" if ocr_text else ""
    prompt = SYSTEM_INSTRUCTION + user_part + ocr_part + "\n" + PROMPT
    payload: dict = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "think": True,
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
                    "temp_range": (2, 8),
                    "confidence": "LOW",
                    "raw_response": full_text,
                    "error": "JSON 파싱 실패 — 기본 냉장 온도(2~8°C) 적용",
                }

    except requests.exceptions.ConnectionError:
        yield {"type": "error", "text": "Ollama 서버 연결 실패 (localhost:11434)"}
    except requests.exceptions.Timeout:
        yield {"type": "error", "text": "응답 시간 초과 (120초)"}
    except Exception as e:
        yield {"type": "error", "text": f"처리 오류: {e}"}
