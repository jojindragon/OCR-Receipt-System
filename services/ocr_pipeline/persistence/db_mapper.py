from datetime import datetime

CATEGORY_MAP = {
    "식비": 1,
    "카페": 2,
    "교통": 3,
    "쇼핑": 4,
    "의료": 5,
    "편의점": 6,
    "주유": 7,
    "기타": 8
}


def calculate_confidence(parsed: dict) -> float:
    score = 0

    if parsed.get("store_name"): score += 0.3
    if parsed.get("total", 0) > 0: score += 0.3
    if parsed.get("transaction_date"): score += 0.2
    if parsed.get("category") != "기타": score += 0.2

    return round(score, 2)


def map_to_db_schema(image_path: str, parsed: dict) -> dict:

    return {
        "user_id": 1,
        "image_path": image_path,
        "category": CATEGORY_MAP.get(parsed.get("category"), 8),
        "date": parsed.get("transaction_date"),
        "total": parsed.get("total"),
        "store_name": parsed.get("store_name"),
        "payment": parsed.get("payment"),

        "details": {
            "items": parsed.get("items", []),
            "tax": "",
            "discount": 0,
            "card_number": "",
            "address": "",
            "tel": ""
        },

        "created_at": datetime.now().isoformat(),
        "ocr_confidence": calculate_confidence(parsed)
    }