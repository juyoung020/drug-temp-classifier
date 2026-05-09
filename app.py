import streamlit as st

from llm_client import stream_query_ollama
from log_manager import save_log
from ontology import build_scene_repr, classify_drug, save_owl

st.set_page_config(
    page_title="약품 보관 온도 인식 시스템",
    page_icon="💊",
    layout="wide",
)

st.title("💊 약품 보관 온도 인식 시스템")
st.caption("Gemma4 · EasyOCR · OWL 온톨로지 · 완전 로컬")

col_input, col_stream, col_result = st.columns([1, 2, 1.1])
llm_result: dict | None = None
ocr_text   = ""
img_color  = ""
clip_desc  = ""
scene_repr: str | None = None

# ── 1. 입력 ────────────────────────────────────────────────────────────────────
with col_input:
    st.subheader("입력")

    uploaded_file = st.file_uploader(
        "이미지 업로드 (jpg / jpeg / png)",
        type=["jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )

    image_bytes: bytes | None = None
    image_filename = "텍스트 입력"

    if uploaded_file:
        image_bytes = uploaded_file.read()
        image_filename = uploaded_file.name
        st.image(image_bytes, caption=uploaded_file.name, width=240)

        # OCR — LLM보다 먼저 독립 실행
        with st.spinner("OCR 텍스트 추출 중..."):
            try:
                from ocr_client import extract_text
                ocr_text = extract_text(image_bytes)
            except Exception as e:
                ocr_text = ""
                st.caption(f"OCR 실패: {e}")

        if ocr_text:
            st.caption(f"OCR: {ocr_text[:80]}")

        # 색상·형태 추출 + Symbolic Scene Representation 생성
        with st.spinner("색상·형태 분석 중 (CLIP)..."):
            try:
                from image_analyzer import detect_form, extract_dominant_color
                img_color = extract_dominant_color(image_bytes)
                clip_desc = detect_form(image_bytes)
                scene_repr = build_scene_repr(ocr_text, clip_desc, img_color)
            except Exception:
                pass

        if scene_repr:
            st.caption("온톨로지 장면 표현 생성됨 → LLM에 주입")

    st.divider()

    text_input: str = st.text_input(
        "약품명 직접 입력 (테스트)",
        placeholder="예: 인슐린, Sol-M Pen Needle ...",
    )

    analyze_btn = st.button("분석 시작", type="primary", use_container_width=True)

# ── 2. 인식결과 — 온톨로지 맥락 · LLM 응답 나란히 ────────────────────────────
with col_stream:
    st.subheader("인식결과")

    if not analyze_btn:
        st.info("분석을 시작하면 온톨로지 맥락과 LLM 응답이 표시됩니다.")

    elif not image_bytes and not text_input.strip():
        st.warning("이미지 또는 약품명을 입력해주세요.")

    else:
        onto_col, json_col = st.columns(2)

        with onto_col:
            st.caption("🧠 온톨로지 장면 표현")
            if scene_repr:
                st.code(scene_repr, language=None)
            else:
                st.info("신호 없음 — 힌트 없이 LLM 실행")

        with json_col:
            st.caption("📝 LLM 응답")
            response_ph = st.empty()

        response_text = ""

        for event in stream_query_ollama(
            image_bytes,
            text_input.strip() or None,
            ocr_text=ocr_text,
            scene_repr=scene_repr,
        ):
            if event["type"] == "chunk":
                response_text += event["text"]
                response_ph.code(response_text + "▌", language="json")

            elif event["type"] == "result":
                try:
                    import json as _json
                    pretty = _json.dumps(_json.loads(response_text), indent=2, ensure_ascii=False)
                except Exception:
                    pretty = response_text
                response_ph.code(pretty, language="json")
                llm_result = event

            elif event["type"] == "error":
                response_ph.error(f"⚠️ {event['text']}")
                llm_result = {
                    "drug_name":  text_input.strip() or "오류",
                    "category":   None,
                    "image_text": "",
                    "intuition":  "",
                    "form":       "other",
                    "color":      "",
                    "raw_response": "",
                    "error": event["text"],
                }

        if llm_result is None:
            llm_result = {
                "drug_name":  text_input.strip() or "알 수 없음",
                "category":   None,
                "image_text": "",
                "intuition":  "",
                "form":       "other",
                "color":      "",
                "raw_response": response_text,
                "error": "응답 없음",
            }

# ── 3. 분석 결과 ───────────────────────────────────────────────────────────────
with col_result:
    st.subheader("분석 결과")

    if not analyze_btn or (not image_bytes and not text_input.strip()):
        st.info("분석 완료 후 결과가 여기에 표시됩니다.")

    elif llm_result is not None:
        drug_name  = llm_result["drug_name"]
        category   = llm_result.get("category")
        image_text = llm_result.get("image_text", "")
        intuition  = llm_result.get("intuition", "")
        form       = llm_result.get("form", "other")
        color      = llm_result.get("color", "")

        onto_temp, onto_desc, confidence = classify_drug(
            category=category,
            drug_name=drug_name,
            image_text=image_text,
            intuition=intuition,
            color=color,
            form=form,
        )

        final_temp = onto_temp

        if llm_result.get("error"):
            st.error(f"⚠️ {llm_result['error']}")

        # 약품명 · 계열
        st.markdown(f"### {drug_name}")
        st.markdown(f"**{onto_desc}**")

        st.divider()

        if category and category != "unknown":
            st.info(f"LLM 분류: `{category}`")

        # 신호 요약
        signals = []
        if ocr_text:
            signals.append(f"OCR: {ocr_text[:50]}")
        if image_text and image_text != ocr_text:
            signals.append(f"텍스트: {image_text[:40]}")
        if intuition:
            signals.append(f"직관: {intuition[:30]}")
        if form and form != "other":
            signals.append(f"형태: {form}")
        if color:
            signals.append(f"색상: {color}")
        if signals:
            st.caption("신호  \n" + "  \n".join(signals))

        # 신뢰도
        if confidence == "HIGH":
            st.success("신뢰도 HIGH — LLM·온톨로지 일치")
        elif confidence == "LOW":
            st.error("신뢰도 LOW — 직접 확인 필요")
        else:
            st.warning("신뢰도 MID")

        st.divider()

        # 최종 온도
        st.metric("최종 목표 온도", f"{final_temp[0]}~{final_temp[1]}°C")

        log_path = save_log(
            image_filename=image_filename,
            drug_name=drug_name,
            ontology_result={"temp_range": onto_temp, "description": onto_desc},
            final_temp_range=final_temp,
            confidence=confidence,
        )
        st.caption(f"로그: {log_path}")
        save_owl()
