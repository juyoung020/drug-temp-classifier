# 💊 Drug Storage Temperature Classifier

> **2026학년도 ICT(항공드론) 창업메이커톤** 시연용 코드 — 팀 쿨항대  
> 드론을 활용한 의약품 배송 시스템에서 **약품별 적정 보관 온도를 자동 판별**하는 AI 모듈입니다.  
> 이미지 또는 약품명만으로 냉장·상온 여부를 분류하고, 드론 탑재 냉온장 컨테이너의 온도 설정값을 자동 산출합니다.  
> 📋 [팀 노션](https://plausible-hallway-e4f.notion.site/081454b08de282e2b47d81c98ff5e3e8?source=copy_link)

[![시연 영상](https://img.youtube.com/vi/6dkbLbDoTno/maxresdefault.jpg)](https://youtu.be/6dkbLbDoTno)

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red)
![Ollama](https://img.shields.io/badge/Ollama-Gemma4-green)
![OWL](https://img.shields.io/badge/Ontology-OWL%2FowlReady2-orange)

---

## 시스템 구조

![시스템 구성도](assets/architecture.png)

---

## 동작 방식

이 시스템은 **LLM**과 **OWL 온톨로지**가 역할을 나눠 작동합니다.

| 구성요소 | 역할 |
|---|---|
| EasyOCR | 이미지에서 텍스트 추출 → LLM 참고 정보 제공 |
| Gemma4 LLM | 이미지·약품명을 보고 약품 계열 판단 |
| OWL 온톨로지 | 계열을 받아 보관 온도 자동 추론 |

약품 이미지를 입력하면 EasyOCR이 글자를 읽고, Gemma4가 이미지와 텍스트를 함께 분석해 약품 계열을 판별합니다.
그 결과를 온톨로지에 넘기면, 지식 규칙에 따라 적정 보관 온도가 자동으로 결정됩니다.
LLM이 온도를 직접 출력하지 않기 때문에, 온도 규칙은 온톨로지에서 일괄 관리합니다.

---

## 온톨로지의 3가지 역할

단순한 딕셔너리 대신 OWL 온톨로지를 사용하는 이유는, 하나의 온톨로지가 세 가지 역할을 동시에 수행하기 때문입니다.

### 1. 보관 온도 DB

냉장·상온·혈액·기기 등 보관 조건별 온도 범위를 온톨로지 안에 저장합니다.
온도를 수정할 때 코드를 뒤질 필요 없이 온톨로지만 바꾸면 됩니다.

| 보관 조건 | 온도 범위 |
|---|---|
| 냉장 (Refrigerated) | 2°C \~ 8°C |
| 혈액 (BloodStorage) | 2°C \~ 6°C |
| 상온 (RoomTemp) | 15°C \~ 25°C |
| 기기 (DeviceTemp) | 15°C \~ 30°C |

### 2. 약품 분류기

AI가 출력한 계열명을 받아 "이 약이 어떤 종류인지"를 추론기가 스스로 결론 내립니다.
인슐린이라고 들어오면 → 인슐린 약품 → 냉장 보관 약품 순서로 자동 분류됩니다.
개발자가 매핑 테이블을 직접 관리하지 않아도 됩니다.

### 3. 규칙 추론기 (확장성)

"인슐린은 2°C \~ 8°C"처럼 약품마다 온도를 일일이 지정하지 않아도 됩니다.
냉장 보관 약품이라는 클래스에 속하는 순간, 2°C \~ 8°C 규칙이 자동으로 상속됩니다.
새 계열을 추가할 때도 어떤 그룹에 속하는지만 선언하면 온도는 따라옵니다.

---

## OWL 온톨로지 구조

```
Thing
├── StorageCondition          ← 보관 온도 DB
│    ├── Refrigerated  (2~8°C)
│    ├── BloodStorage  (2~6°C)
│    ├── RoomTemp      (15~25°C)
│    └── DeviceTemp    (15~30°C)
│
├── DrugCategory              ← LLM 출력을 OWL 개체로 변환
│    └── cat_insulin, cat_vaccine_biologic, cat_blood_product,
│        cat_chemo_hormone, cat_antibiotic, cat_analgesic,
│        cat_vitamin, cat_general_oral, cat_medical_device
│
└── Drug
     ├── ColdChainDrug  → requiresStorage = Refrigerated
     │    ├── InsulinDrug     ≡ Drug & hasCategoryInd = cat_insulin
     │    ├── VaccineBiologic ≡ Drug & hasCategoryInd = cat_vaccine_biologic
     │    └── ChemoHormone    ≡ Drug & hasCategoryInd = cat_chemo_hormone
     ├── RoomTempDrug   → requiresStorage = RoomTemp
     │    ├── Antibiotic  ≡ Drug & hasCategoryInd = cat_antibiotic
     │    ├── Analgesic   ≡ Drug & hasCategoryInd = cat_analgesic
     │    ├── Vitamin     ≡ Drug & hasCategoryInd = cat_vitamin
     │    └── GeneralOral ≡ Drug & hasCategoryInd = cat_general_oral
     ├── BloodProduct   → requiresStorage = BloodStorage
     │    └── ≡ Drug & hasCategoryInd = cat_blood_product
     └── MedicalDevice  → requiresStorage = DeviceTemp
          └── ≡ Drug & hasCategoryInd = cat_medical_device
```

**`≡` (equivalent_to)** 는 OWL 필요충분조건입니다.  
`InsulinDrug ≡ Drug & hasCategoryInd = cat_insulin` 의 의미:  
→ `cat_insulin` 신호가 주입된 Drug 개체를 추론기가 자동으로 `InsulinDrug`으로 분류합니다.  
→ 개발자가 온도를 직접 지정하지 않아도, 클래스 계층(`InsulinDrug → ColdChainDrug → Refrigerated`)을 따라 자동 도출됩니다.

**새 냉장 계열 약품을 추가할 때**는 `ColdChainDrug`의 자식 클래스로 선언하기만 하면 온도 규칙은 자동 상속됩니다.

분석 완료 시 `drug_ontology.owl` (RDF/XML)로 저장됩니다. Protégé에서 열람 가능합니다.

---

## 지원 계열 (9개)

| 계열 | 보관 온도 |
|---|---|
| `insulin` | 2°C \~ 8°C |
| `vaccine_biologic` | 2°C \~ 8°C |
| `chemo_hormone` | 2°C \~ 8°C |
| `blood_product` | 2°C \~ 6°C |
| `antibiotic` | 15°C \~ 25°C |
| `analgesic` | 15°C \~ 25°C |
| `vitamin` | 15°C \~ 25°C |
| `general_oral` | 15°C \~ 25°C |
| `medical_device` | 15°C \~ 30°C |

미분류 기본값: **2°C \~ 8°C** (안전 우선)

---

## 처리 시간

| 단계 | 소요 시간 |
|---|---|
| EasyOCR (최초 1회 모델 로드 포함) | 약 10초 |
| EasyOCR (이후) | 약 1\~2초 |
| **Gemma4 LLM** ← 병목 | **약 5\~15초** |
| OWL 추론 (HermiT) | 약 0.5\~1초 |
| **총합** | **약 7\~17초** |

EasyOCR는 이미지 업로드 즉시 실행 → LLM 분석과 병렬 처리됩니다.

LLM 출력을 자유 형식 텍스트 대신 **enum으로 고정**했기 때문에 모델이 생성해야 할 토큰 수가 줄어 이전 대비 처리 속도가 빨라졌습니다.

---

## 설치 및 실행

```bash
ollama pull gemma4:e4b
pip install -r requirements.txt
streamlit run app.py
```

> Ollama 서버(`localhost:11434`)가 먼저 실행 중이어야 합니다.  
> Gemma4 모델 용량: 약 9.6GB / 최소 RAM 6.7GiB  
> Java 17 필요 (HermiT 추론기 실행용)

---

## 주의사항

- 본 시스템은 **참고용**이며 실제 의약품 보관은 반드시 공식 지침을 따르세요
- LLM이 잘못된 계열을 출력하면 온톨로지 추론 결과도 틀릴 수 있습니다 — 신뢰도 LOW 시 직접 확인하세요
