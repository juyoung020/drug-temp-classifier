import owlready2
from owlready2 import (
    AnnotationProperty, DataProperty, FunctionalProperty, ObjectProperty,
    Thing, destroy_entity, get_ontology, sync_reasoner,
)

owlready2.JAVA_EXE = "C:/Program Files/Eclipse Adoptium/jdk-17.0.19.10-hotspot/bin/java.exe"

ONTO_IRI = "http://drug-temp-classifier.local/ontology#"
onto = get_ontology(ONTO_IRI)

with onto:
    # ── StorageCondition ────────────────────────────────────────────────────────
    class StorageCondition(Thing):
        pass

    class sc_min_temp(DataProperty, FunctionalProperty):
        domain = [StorageCondition]
        range  = [int]

    class sc_max_temp(DataProperty, FunctionalProperty):
        domain = [StorageCondition]
        range  = [int]

    Refrigerated = StorageCondition("Refrigerated")
    Refrigerated.sc_min_temp = 2
    Refrigerated.sc_max_temp = 8

    BloodStorage = StorageCondition("BloodStorage")
    BloodStorage.sc_min_temp = 2
    BloodStorage.sc_max_temp = 6

    RoomTemp = StorageCondition("RoomTemp")
    RoomTemp.sc_min_temp = 15
    RoomTemp.sc_max_temp = 25

    DeviceTemp = StorageCondition("DeviceTemp")
    DeviceTemp.sc_min_temp = 15
    DeviceTemp.sc_max_temp = 30

    # ── DrugCategory ────────────────────────────────────────────────────────────
    class DrugCategory(Thing):
        pass

    cat_insulin          = DrugCategory("cat_insulin")
    cat_vaccine_biologic = DrugCategory("cat_vaccine_biologic")
    cat_blood_product    = DrugCategory("cat_blood_product")
    cat_chemo_hormone    = DrugCategory("cat_chemo_hormone")
    cat_antibiotic       = DrugCategory("cat_antibiotic")
    cat_analgesic        = DrugCategory("cat_analgesic")
    cat_vitamin          = DrugCategory("cat_vitamin")
    cat_general_oral     = DrugCategory("cat_general_oral")
    cat_medical_device   = DrugCategory("cat_medical_device")

    # ── Drug 계층 ────────────────────────────────────────────────────────────────
    class Drug(Thing):
        pass

    class requiresStorage(ObjectProperty, FunctionalProperty):
        domain = [Drug]
        range  = [StorageCondition]

    class hasCategoryInd(ObjectProperty, FunctionalProperty):
        domain = [Drug]
        range  = [DrugCategory]

    # ── Annotation Properties (이중검증용 — Protégé에서 열람 가능) ───────────────
    class typical_colors(AnnotationProperty):
        pass

    class typical_forms(AnnotationProperty):
        pass

    class category_keywords(AnnotationProperty):
        pass

    # ── Drug 서브클래스 ──────────────────────────────────────────────────────────
    class ColdChainDrug(Drug):
        is_a = [requiresStorage.value(Refrigerated)]

    class RoomTempDrug(Drug):
        is_a = [requiresStorage.value(RoomTemp)]

    class BloodProduct(Drug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_blood_product)]
        is_a          = [requiresStorage.value(BloodStorage)]

    class MedicalDevice(Drug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_medical_device)]
        is_a          = [requiresStorage.value(DeviceTemp)]

    class InsulinDrug(ColdChainDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_insulin)]

    class VaccineBiologic(ColdChainDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_vaccine_biologic)]

    class ChemoHormone(ColdChainDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_chemo_hormone)]

    class Antibiotic(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_antibiotic)]

    class Analgesic(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_analgesic)]

    class Vitamin(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_vitamin)]

    class GeneralOral(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_general_oral)]

    # ── 클래스별 특성 정보 ────────────────────────────────────────────────────────
    InsulinDrug.typical_colors    = ["white", "transparent", "orange"]
    InsulinDrug.typical_forms     = ["pen", "vial", "syringe"]
    InsulinDrug.category_keywords = ["인슐린", "insulin", "노보", "란투스", "레버미어", "휴마로그", "트레시바"]

    VaccineBiologic.typical_colors    = ["transparent", "white"]
    VaccineBiologic.typical_forms     = ["vial", "syringe"]
    VaccineBiologic.category_keywords = ["백신", "vaccine", "항체", "biologic", "독감", "코로나"]

    BloodProduct.typical_colors    = ["red", "amber"]
    BloodProduct.typical_forms     = ["bottle", "package"]
    BloodProduct.category_keywords = ["혈액", "blood", "혈장", "plasma", "혈소판", "알부민", "albumin"]

    ChemoHormone.typical_colors    = ["transparent", "white", "yellow"]
    ChemoHormone.typical_forms     = ["vial", "bottle", "syringe"]
    ChemoHormone.category_keywords = ["항암", "chemo", "호르몬", "hormone", "에스트로겐", "타목시펜"]

    Antibiotic.typical_colors    = ["white", "yellow", "orange"]
    Antibiotic.typical_forms     = ["tablet", "bottle", "vial"]
    Antibiotic.category_keywords = ["항생제", "antibiotic", "아목시실린", "amoxicillin", "세파", "페니실린"]

    Analgesic.typical_colors    = ["white", "yellow", "orange", "pink"]
    Analgesic.typical_forms     = ["tablet", "bottle"]
    Analgesic.category_keywords = ["진통제", "analgesic", "타이레놀", "tylenol", "이부프로펜", "ibuprofen", "아스피린", "해열"]

    Vitamin.typical_colors    = ["yellow", "orange", "white"]
    Vitamin.typical_forms     = ["tablet", "bottle"]
    Vitamin.category_keywords = ["비타민", "vitamin", "비타C", "영양제", "엽산", "zinc", "오메가"]

    GeneralOral.typical_colors    = ["white", "yellow", "pink", "blue"]
    GeneralOral.typical_forms     = ["tablet", "bottle"]
    GeneralOral.category_keywords = ["경구", "oral", "알약", "캡슐", "capsule"]

    MedicalDevice.typical_colors    = ["white", "transparent", "blue"]
    MedicalDevice.typical_forms     = ["package", "other"]
    MedicalDevice.category_keywords = ["란셋", "lancet", "혈당측정", "glucometer", "혈압계", "체온계", "thermometer"]


# ── 카테고리 키 → DrugCategory individual ───────────────────────────────────
_CAT_IND_MAP = {
    "insulin":          onto.cat_insulin,
    "vaccine_biologic": onto.cat_vaccine_biologic,
    "blood_product":    onto.cat_blood_product,
    "chemo_hormone":    onto.cat_chemo_hormone,
    "antibiotic":       onto.cat_antibiotic,
    "analgesic":        onto.cat_analgesic,
    "vitamin":          onto.cat_vitamin,
    "general_oral":     onto.cat_general_oral,
    "medical_device":   onto.cat_medical_device,
}

# ── 카테고리 키 → Drug 클래스 (annotation 읽기용) ────────────────────────────
_CAT_CLASS_MAP = {
    "insulin":          onto.InsulinDrug,
    "vaccine_biologic": onto.VaccineBiologic,
    "blood_product":    onto.BloodProduct,
    "chemo_hormone":    onto.ChemoHormone,
    "antibiotic":       onto.Antibiotic,
    "analgesic":        onto.Analgesic,
    "vitamin":          onto.Vitamin,
    "general_oral":     onto.GeneralOral,
    "medical_device":   onto.MedicalDevice,
}

# ── 계열별 설명 ──────────────────────────────────────────────────────────────
_DRUG_CONFIG: dict[str, dict] = {
    "insulin":          {"description": "인슐린 계열"},
    "vaccine_biologic": {"description": "백신·생물의약품 계열"},
    "blood_product":    {"description": "혈액제제 계열"},
    "chemo_hormone":    {"description": "항암·호르몬제 계열"},
    "antibiotic":       {"description": "항생제 계열"},
    "analgesic":        {"description": "진통·해열제 계열"},
    "vitamin":          {"description": "비타민 계열"},
    "general_oral":     {"description": "일반 경구약 계열"},
    "medical_device":   {"description": "의료기기 계열"},
}

DEFAULT_TEMP_RANGE  = (2, 8)
DEFAULT_DESCRIPTION = "미분류 (냉장 기본값 적용)"


def _get_list(cls, attr: str) -> list[str]:
    val = getattr(cls, attr, None)
    if val is None:
        return []
    return val if isinstance(val, list) else [str(val)]


def _reason_temp(category: str) -> tuple[int, int]:
    cat_ind = _CAT_IND_MAP.get(category)
    if cat_ind is None:
        return DEFAULT_TEMP_RANGE

    with onto:
        ind = Drug("_obs_drug")
        ind.hasCategoryInd = cat_ind

    try:
        sync_reasoner(onto, infer_property_values=True, debug=0)
        storage = ind.requiresStorage  # type: ignore[assignment]
        if storage:
            return (int(storage.sc_min_temp), int(storage.sc_max_temp))  # type: ignore[arg-type]
    except Exception:
        pass
    finally:
        destroy_entity(ind)

    return DEFAULT_TEMP_RANGE


def _score_signals(
    drug_name:  str,
    image_text: str,
    intuition:  str,
    color:      str,
    form:       str,
) -> str | None:
    text = f"{drug_name} {image_text} {intuition}".lower()

    scores: dict[str, int] = {}
    for cat, cls in _CAT_CLASS_MAP.items():
        score = sum(1 for kw in _get_list(cls, "category_keywords") if kw.lower() in text)
        if color and color in _get_list(cls, "typical_colors"):
            score += 1
        if form and form != "other" and form in _get_list(cls, "typical_forms"):
            score += 1
        scores[cat] = score

    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


_CHAIN_TEXT: dict[str, str] = {
    "insulin":          "InsulinDrug ← hasCategoryInd = cat_insulin\n  ↓ (∈ ColdChainDrug)\n  requiresStorage = Refrigerated\n  → 예상 보관 온도: 2°C ~ 8°C",
    "vaccine_biologic": "VaccineBiologic ← hasCategoryInd = cat_vaccine_biologic\n  ↓ (∈ ColdChainDrug)\n  requiresStorage = Refrigerated\n  → 예상 보관 온도: 2°C ~ 8°C",
    "blood_product":    "BloodProduct ← hasCategoryInd = cat_blood_product\n  requiresStorage = BloodStorage\n  → 예상 보관 온도: 2°C ~ 6°C",
    "chemo_hormone":    "ChemoHormone ← hasCategoryInd = cat_chemo_hormone\n  ↓ (∈ ColdChainDrug)\n  requiresStorage = Refrigerated\n  → 예상 보관 온도: 2°C ~ 8°C",
    "antibiotic":       "Antibiotic ← hasCategoryInd = cat_antibiotic\n  ↓ (∈ RoomTempDrug)\n  requiresStorage = RoomTemp\n  → 예상 보관 온도: 15°C ~ 25°C",
    "analgesic":        "Analgesic ← hasCategoryInd = cat_analgesic\n  ↓ (∈ RoomTempDrug)\n  requiresStorage = RoomTemp\n  → 예상 보관 온도: 15°C ~ 25°C",
    "vitamin":          "Vitamin ← hasCategoryInd = cat_vitamin\n  ↓ (∈ RoomTempDrug)\n  requiresStorage = RoomTemp\n  → 예상 보관 온도: 15°C ~ 25°C",
    "general_oral":     "GeneralOral ← hasCategoryInd = cat_general_oral\n  ↓ (∈ RoomTempDrug)\n  requiresStorage = RoomTemp\n  → 예상 보관 온도: 15°C ~ 25°C",
    "medical_device":   "MedicalDevice ← hasCategoryInd = cat_medical_device\n  requiresStorage = DeviceTemp\n  → 예상 보관 온도: 15°C ~ 30°C",
}


def build_scene_repr(ocr_text: str, clip_desc: str, color: str) -> str | None:
    text = ocr_text.lower()
    clip_lower = clip_desc.lower()

    scores: dict[str, int] = {}
    for cat, cls in _CAT_CLASS_MAP.items():
        score  = sum(1 for kw in _get_list(cls, "category_keywords") if kw.lower() in text)
        score += 1 if color and color in _get_list(cls, "typical_colors") else 0
        score += sum(1 for f in _get_list(cls, "typical_forms") if f in clip_lower)
        scores[cat] = score

    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return None

    top = sorted([(c, s) for c, s in scores.items() if s > 0], key=lambda x: -x[1])[:4]
    mapping_lines = "\n".join(
        f"  {c:<18} {'●' * s:<6} {s}점{'  ← 최고점' if c == best else ''}"
        for c, s in top
    )

    ocr_display   = f'"{ocr_text[:60]}"' if ocr_text else "(없음)"
    clip_display  = clip_desc if clip_desc else "(없음)"
    color_display = color if color else "(없음)"

    return (
        "[약품 장면 표현 (Symbolic Scene Representation)]\n\n"
        "── 관측 ──────────────────────────────────────\n"
        f"텍스트 (OCR)  : {ocr_display}\n"
        f"형태 (CLIP)   : {clip_display}\n"
        f"색상 (HSV)    : {color_display}\n\n"
        "── 온톨로지 매핑 ──────────────────────────────\n"
        f"{mapping_lines}\n\n"
        "── 추론 체인 ──────────────────────────────────\n"
        f"{_CHAIN_TEXT.get(best, '')}\n\n"
        "── 가설 ───────────────────────────────────────\n"
        f"{best} ({_DRUG_CONFIG[best]['description']}) — 이미지로 직접 확인 후 최종 판단하세요."
    )


def classify_drug(
    category:   str | None = None,
    drug_name:  str = "",
    image_text: str = "",
    intuition:  str = "",
    color:      str = "",
    form:       str = "",
) -> tuple[tuple[int, int], str, str]:
    keyword_best = _score_signals(drug_name, image_text, intuition, color, form)
    valid = category and category != "unknown" and category in _DRUG_CONFIG

    if keyword_best and valid:
        confidence = "HIGH" if keyword_best == category else "LOW"
        use_cat = category
    elif valid:
        confidence = "MID"
        use_cat = category
    else:
        confidence = "LOW"
        use_cat = keyword_best

    if use_cat and use_cat in _DRUG_CONFIG:
        return _reason_temp(use_cat), _DRUG_CONFIG[use_cat]["description"], confidence

    return DEFAULT_TEMP_RANGE, DEFAULT_DESCRIPTION, "LOW"


def save_owl(path: str = "drug_ontology.owl") -> None:
    onto.save(file=path, format="rdfxml")
