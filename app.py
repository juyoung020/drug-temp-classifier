import streamlit as st

from llm_client import stream_query_ollama
from log_manager import save_log
from ontology import classify_drug, save_owl

st.set_page_config(
    page_title="약품 보관 온도 인식 시스템",
    page_icon="💊",
    layout="wide",
)

st.title("💊 약품 보관 온도 인식 시스템")
st.caption("Gemma4 · EasyOCR · OWL 온톨로지 · 완전 로컬")

col_input, col_stream, col_result = st.columns([1, 2, 1.1])
llm_result: dict | None = None
ocr_text = ""

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

    st.divider()

    text_input: str = st.text_input(
        "약품명 직접 입력 (테스트)",
        placeholder="예: 인슐린, Sol-M Pen Needle ...",
    )

    analyze_btn = st.button("분석 시작", type="primary", use_container_width=True)

# ── 2. 인식결과 — 추론 · JSON 나란히 ──────────────────────────────────────────
with col_stream:
    st.subheader("인식결과")

    if not analyze_btn:
        st.info("분석을 시작하면 LLM 추론이 실시간으로 표시됩니다.")

    elif not image_bytes and not text_input.strip():
        st.warning("이미지 또는 약품명을 입력해주세요.")

    else:
        think_col, json_col = st.columns(2)

        with think_col:
            st.caption("💭 추론 (Thinking)")
            thinking_ph = st.empty()

        with json_col:
            st.caption("📝 JSON 응답")
            response_ph = st.empty()

        thinking_text = ""
        response_text = ""

        for event in stream_query_ollama(
            image_bytes,
            text_input.strip() or None,
            ocr_text=ocr_text,
        ):
            if event["type"] == "thinking":
                thinking_text += event["text"]
                thinking_ph.markdown(thinking_text + "▌")

            elif event["type"] == "chunk":
                response_text += event["text"]
                response_ph.code(response_text + "▌", language=None)

            elif event["type"] == "result":
                thinking_ph.markdown(thinking_text or "*(thinking 미지원)*")
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
                    "temp_range": (2, 8),
                    "confidence": "LOW",
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
                "temp_range": (2, 8),
                "confidence": "LOW",
                "raw_response": response_text,
                "error": "응답 없음",
            }

# ── 3. 약품명 · 계열 · 최종 결과 ──────────────────────────────────────────────
with col_result:
    st.subheader("약품명")

    if not analyze_btn or (not image_bytes and not text_input.strip()):
        st.info("분석 완료 후 결과가 여기에 표시됩니다.")

    elif llm_result is not None:
        drug_name  = llm_result["drug_name"]
        llm_temp   = llm_result["temp_range"]
        confidence = llm_result["confidence"]
        category   = llm_result.get("category")
        image_text = llm_result.get("image_text", "")
        intuition  = llm_result.get("intuition", "")
        form       = llm_result.get("form", "other")
        color      = llm_result.get("color", "")

        onto_temp, onto_desc, onto_scores = classify_drug(
            drug_name,
            category=category,
            ocr_text=ocr_text,
            image_text=image_text,
            intuition=intuition,
            form=form,
            color=color,
        )

        if confidence == "HIGH":
            final_temp   = llm_temp
            final_source = "LLM (HIGH 신뢰도)"
        else:
            final_temp   = onto_temp
            final_source = "OWL 온톨로지 점수"

        if llm_result.get("error"):
            st.error(f"⚠️ {llm_result['error']}")

        st.markdown(f"**{drug_name}**")

        # 계열
        onto_source_label = f"LLM: `{category}`" if category and category != "unknown" else "키워드 매칭"
        st.markdown(f"계열 &nbsp; **{onto_desc}**")
        st.caption(onto_source_label)

        # OCR·신호 요약
        signals = []
        if ocr_text:
            signals.append(f"OCR: {ocr_text[:50]}")
        if image_text and image_text != ocr_text:
            signals.append(f"LLM글자: {image_text[:40]}")
        if intuition:
            signals.append(f"직관: {intuition[:30]}")
        if form and form != "other":
            signals.append(f"형태: {form}")
        if color:
            signals.append(f"색상: {color}")
        if signals:
            st.caption("  \n".join(signals))

        # 온톨로지 점수 바 차트
        if onto_scores:
            top = sorted(onto_scores.items(), key=lambda x: x[1], reverse=True)[:4]
            max_score = top[0][1]
            score_lines = []
            for key, score in top:
                bar = "█" * score + "░" * (max_score - score)
                score_lines.append(f"`{key}` {bar} {score}")
            st.caption("OWL 점수\n" + "  \n".join(score_lines))

        # 신뢰도
        if confidence == "LOW":
            st.error("🔴 신뢰도: LOW — 직접 확인 필요")
        elif confidence == "MID":
            st.warning("🟡 신뢰도: MID")
        else:
            st.success("🟢 신뢰도: HIGH")

        st.divider()

        # 온도 비교
        r1, r2 = st.columns(2)
        r1.metric("LLM 온도", f"{llm_temp[0]}~{llm_temp[1]}°C")
        r2.metric("온톨로지", f"{onto_temp[0]}~{onto_temp[1]}°C")

        if llm_temp != onto_temp:
            st.info(f"불일치 → **{final_source}** 채택")

        st.divider()

        st.metric("최종 목표 온도", f"{final_temp[0]}~{final_temp[1]}°C")
        st.success(f"✅ {final_temp[0]}~{final_temp[1]}°C ({final_source})")

        log_path = save_log(
            image_filename=image_filename,
            drug_name=drug_name,
            llm_temp_range=llm_temp,
            ontology_result={"temp_range": onto_temp, "description": onto_desc},
            final_temp_range=final_temp,
            confidence=confidence,
        )
        st.caption(f"로그: {log_path}")
        save_owl()
