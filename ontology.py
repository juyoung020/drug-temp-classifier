import owlready2
from owlready2 import (
    DataProperty, FunctionalProperty, ObjectProperty,
    Thing, destroy_entity, get_ontology, sync_reasoner,
)

owlready2.JAVA_EXE = "C:/Program Files/Eclipse Adoptium/jdk-17.0.19.10-hotspot/bin/java.exe"

ONTO_IRI = "http://drug-temp-classifier.local/ontology#"
onto = get_ontology(ONTO_IRI)

with onto:
    # ── TBox: StorageCondition ───────────────────────────────────────────────
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

    # ── TBox: DrugCategory (관찰 신호 ABox 주입용) ───────────────────────────
    # LLM이 출력한 category를 OWL individual로 표현해 추론기에 전달
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

    # ── TBox: Drug 계층 ──────────────────────────────────────────────────────
    class Drug(Thing):
        pass

    class requiresStorage(ObjectProperty, FunctionalProperty):
        domain = [Drug]
        range  = [StorageCondition]

    # ABox 주입용: Drug individual에 관찰된 카테고리 신호를 붙임
    class hasCategoryInd(ObjectProperty, FunctionalProperty):
        domain = [Drug]
        range  = [DrugCategory]

    # 중간 계층 — 보관 조건 연결
    class ColdChainDrug(Drug):
        is_a = [requiresStorage.value(Refrigerated)]

    class RoomTempDrug(Drug):
        is_a = [requiresStorage.value(RoomTemp)]

    # BloodProduct·MedicalDevice: 독립 보관 조건
    class BloodProduct(Drug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_blood_product)]
        is_a          = [requiresStorage.value(BloodStorage)]

    class MedicalDevice(Drug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_medical_device)]
        is_a          = [requiresStorage.value(DeviceTemp)]

    # ColdChainDrug 계열 — equivalent_to로 추론기가 분류 결정
    class InsulinDrug(ColdChainDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_insulin)]

    class VaccineBiologic(ColdChainDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_vaccine_biologic)]

    class ChemoHormone(ColdChainDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_chemo_hormone)]

    # RoomTempDrug 계열
    class Antibiotic(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_antibiotic)]

    class Analgesic(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_analgesic)]

    class Vitamin(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_vitamin)]

    class GeneralOral(RoomTempDrug):
        equivalent_to = [Drug & hasCategoryInd.value(cat_general_oral)]


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


def classify_drug(
    category: str | None = None,
) -> tuple[tuple[int, int], str, str]:
    if category and category != "unknown" and category in _DRUG_CONFIG:
        desc       = _DRUG_CONFIG[category]["description"]
        temp_range = _reason_temp(category)
        return temp_range, desc, "MID"

    return DEFAULT_TEMP_RANGE, DEFAULT_DESCRIPTION, "LOW"


def save_owl(path: str = "drug_ontology.owl") -> None:
    onto.save(file=path, format="rdfxml")
