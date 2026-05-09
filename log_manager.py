import json
from datetime import datetime
from pathlib import Path

LOG_DIR = Path("logs")


def save_log(
    image_filename: str,
    drug_name: str,
    ontology_result: dict,
    final_temp_range: tuple[int, int],
    confidence: str,
) -> str:
    LOG_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now()
    filename = f"log_{timestamp.strftime('%Y-%m-%d_%H-%M')}.json"
    filepath = LOG_DIR / filename

    log_data = {
        "이미지_파일명": image_filename,
        "약품명": drug_name,
        "온톨로지_결과": {
            "계열": ontology_result["description"],
            "온도": {
                "최저": ontology_result["temp_range"][0],
                "최고": ontology_result["temp_range"][1],
            },
        },
        "최종_목표_온도": {"최저": final_temp_range[0], "최고": final_temp_range[1]},
        "신뢰도": confidence,
        "처리_시각": timestamp.isoformat(),
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    return str(filepath)
