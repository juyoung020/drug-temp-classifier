from owlready2 import (
    DataProperty, FunctionalProperty, Thing, get_ontology,
)

# ── OWL 온톨로지 정의 ──────────────────────────────────────────────────────────
ONTO_IRI = "http://drug-temp-classifier.local/ontology#"
onto = get_ontology(ONTO_IRI)

with onto:
    class Drug(Thing):
        pass

    class min_temp(DataProperty, FunctionalProperty):
        domain = [Drug]
        range  = [int]

    class max_temp(DataProperty, FunctionalProperty):
        domain = [Drug]
        range  = [int]

    class drug_description(DataProperty, FunctionalProperty):
        domain = [Drug]
        range  = [str]

    # ── 계열 서브클래스 ──────────────────────────────────────────────────────
    class InsulinDrug(Drug):      pass
    class VaccineBiologic(Drug):  pass
    class BloodProduct(Drug):     pass
    class ChemoHormone(Drug):     pass
    class Antibiotic(Drug):       pass
    class Analgesic(Drug):        pass
    class Vitamin(Drug):          pass
    class GeneralOral(Drug):      pass
    class MedicalDevice(Drug):    pass


# ── 계열별 지식 (키워드·색상·온도) ────────────────────────────────────────────
_DRUG_CONFIG: dict[str, dict] = {
    "insulin": {
        "cls":         onto.InsulinDrug,
        "keywords":    ["인슐린", "insulin", "휴마로그", "노보로그", "레버미어",
                        "란투스", "트레시바", "투제오"],
        "colors":      [],
        "min_temp":    2,
        "max_temp":    8,
        "description": "인슐린 계열",
    },
    "vaccine_biologic": {
        "cls":         onto.VaccineBiologic,
        "keywords":    ["백신", "vaccine", "예방접종", "인플루엔자", "독감",
                        "코로나", "항체", "biologic", "허셉틴", "아바스틴",
                        "레미케이드", "휴미라"],
        "colors":      [],
        "min_temp":    2,
        "max_temp":    8,
        "description": "백신·생물의약품 계열",
    },
    "blood_product": {
        "cls":         onto.BloodProduct,
        "keywords":    ["혈액", "혈장", "혈액팩", "알부민", "혈청",
                        "혈소판", "plasma", "albumin"],
        "colors":      ["maroon", "dark red", "burgundy", "암적색", "적갈색", "red"],
        "min_temp":    2,
        "max_temp":    6,
        "description": "혈액제제 계열",
    },
    "chemo_hormone": {
        "cls":         onto.ChemoHormone,
        "keywords":    ["항암", "성장호르몬", "에스트로겐", "프로게스테론",
                        "갑상선호르몬", "chemo", "사이클로포스파미드",
                        "파클리탁셀", "시스플라틴"],
        "colors":      [],
        "min_temp":    2,
        "max_temp":    8,
        "description": "항암·호르몬제 계열",
    },
    "antibiotic": {
        "cls":         onto.Antibiotic,
        "keywords":    ["항생제", "페니실린", "amoxicillin", "아목시실린",
                        "세팔로스포린", "아지스로마이신", "테트라사이클린", "항균"],
        "colors":      [],
        "min_temp":    15,
        "max_temp":    25,
        "description": "항생제 계열",
    },
    "analgesic": {
        "cls":         onto.Analgesic,
        "keywords":    ["진통제", "해열제", "타이레놀", "이부프로펜", "아스피린",
                        "아세트아미노펜", "나프록센"],
        "colors":      [],
        "min_temp":    15,
        "max_temp":    25,
        "description": "진통·해열제 계열",
    },
    "vitamin": {
        "cls":         onto.Vitamin,
        "keywords":    ["비타민", "vitamin", "영양제", "보충제", "미네랄"],
        "colors":      [],
        "min_temp":    15,
        "max_temp":    25,
        "description": "비타민 계열",
    },
    "general_oral": {
        "cls":         onto.GeneralOral,
        "keywords":    ["혈압약", "암로디핀", "로사르탄", "메트포민", "metformin",
                        "당뇨약", "오메프라졸", "판토프라졸", "위장약", "제산제"],
        "colors":      [],
        "min_temp":    15,
        "max_temp":    25,
        "description": "일반 경구약 계열",
    },
    "medical_device": {
        "cls":         onto.MedicalDevice,
        "keywords":    ["pen needle", "펜니들", "주사침", "주사바늘", "needle",
                        "니들", "syringe", "주사기", "lancet", "란셋", "채혈침",
                        "sol-m", "솔-엠", "솔엠", "infusion set", "카테터"],
        "colors":      [],
        "min_temp":    15,
        "max_temp":    30,
        "description": "의료기기 계열",
    },
}

DEFAULT_TEMP_RANGE  = (2, 8)
DEFAULT_DESCRIPTION = "미분류 (냉장 기본값 적용)"

# ── OWL 개체(Individual) 생성 — 레퍼런스 직접 보관 ──────────────────────────
_DRUG_INDIVIDUALS: dict[str, object] = {}
with onto:
    for _key, _cfg in _DRUG_CONFIG.items():
        _ind = _cfg["cls"](_key)
        _ind.min_temp         = _cfg["min_temp"]
        _ind.max_temp         = _cfg["max_temp"]
        _ind.drug_description = _cfg["description"]
        _DRUG_INDIVIDUALS[_key] = _ind

# ── 가중치 ──────────────────────────────────────────────────────────────────
_W_OCR        = 4   # 독립 OCR — 가장 신뢰
_W_IMAGE_TEXT = 3   # LLM이 읽은 텍스트
_W_INTUITION  = 2   # LLM 직관
_W_DRUG_NAME  = 2   # LLM 최종 약품명
_W_COLOR      = 1   # 색상

_DEVICE_FORMS = {"syringe", "needle", "lancet"}


def _is_device_form(form: str) -> bool:
    f = form.lower()
    return f in _DEVICE_FORMS or any(kw in f for kw in _DEVICE_FORMS)


def _score_text(text: str, weight: int) -> dict[str, int]:
    text_lower = text.lower()
    scores: dict[str, int] = {}
    for key, cfg in _DRUG_CONFIG.items():
        count = sum(1 for kw in cfg["keywords"] if kw.lower() in text_lower)
        if count:
            scores[key] = count * weight
    return scores


def _score_color(color: str, weight: int) -> dict[str, int]:
    color_lower = color.lower()
    scores: dict[str, int] = {}
    for key, cfg in _DRUG_CONFIG.items():
        count = sum(
            1 for c in cfg["colors"]
            if c.lower() in color_lower or color_lower in c.lower()
        )
        if count:
            scores[key] = count * weight
    return scores


def _read_owl(key: str) -> tuple[tuple[int, int], str]:
    """OWL 개체에서 온도·설명 읽기."""
    ind = _DRUG_INDIVIDUALS.get(key)
    if ind:
        mn   = ind.min_temp         if ind.min_temp is not None else DEFAULT_TEMP_RANGE[0]
        mx   = ind.max_temp         if ind.max_temp is not None else DEFAULT_TEMP_RANGE[1]
        desc = ind.drug_description if ind.drug_description    else DEFAULT_DESCRIPTION
        return (mn, mx), desc
    return DEFAULT_TEMP_RANGE, DEFAULT_DESCRIPTION


def classify_drug(
    drug_name:  str,
    category:   str | None = None,
    ocr_text:   str = "",
    image_text: str = "",
    intuition:  str = "",
    form:       str = "other",
    color:      str = "",
) -> tuple[tuple[int, int], str, dict[str, int]]:
    scores: dict[str, int] = {}

    def add(new: dict[str, int]) -> None:
        for k, v in new.items():
            scores[k] = scores.get(k, 0) + v

    if ocr_text:
        add(_score_text(ocr_text, _W_OCR))
    if image_text:
        add(_score_text(image_text, _W_IMAGE_TEXT))
    if intuition:
        add(_score_text(intuition, _W_INTUITION))
    if color:
        add(_score_color(color, _W_COLOR))
    if drug_name:
        add(_score_text(drug_name, _W_DRUG_NAME))

    # form이 기기류 + 다른 약품 점수 있으면 medical_device 제거
    if _is_device_form(form) and "medical_device" in scores:
        if sum(v for k, v in scores.items() if k != "medical_device") > 0:
            del scores["medical_device"]

    if scores:
        best = max(scores, key=lambda k: scores[k])
        temp_range, desc = _read_owl(best)
        return temp_range, desc, scores

    # 점수 없으면 LLM category fallback → OWL에서 읽기
    if category and category != "unknown" and category in _DRUG_CONFIG:
        temp_range, desc = _read_owl(category)
        return temp_range, desc, {}

    return DEFAULT_TEMP_RANGE, DEFAULT_DESCRIPTION, {}


def save_owl(path: str = "drug_ontology.owl") -> None:
    onto.save(file=path, format="rdfxml")
