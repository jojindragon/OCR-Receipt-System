"""
Supabase receipts 테이블 기준 DB 매핑

주의:
- created_at은 DB default now() 사용 → Python에서 보내지 않음
- ocr_confidence 컬럼 없음 → 제거
- category / payment는 FK id로 변환 필요
"""

# 카테고리 매핑 (DB categories 테이블 기준으로 맞춰야 함)
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

# 결제수단 매핑 (payment_methods 테이블 기준으로 맞춰야 함)
PAYMENT_MAP = {
    "card": 1,
    "cash": 2,
    "app": 3
}


def map_to_db_schema(image_path: str, parsed: dict) -> dict:
    """
    Supabase receipts 테이블 insert용 payload 생성
    """

    return {
        "user_id": 1,  # 현재 고정 (추후 로그인 사용자로 변경)

        # FK
        "category_id": CATEGORY_MAP.get(parsed.get("category")),
        "payment_method_id": PAYMENT_MAP.get(parsed.get("payment")),

        # 기본 필드
        "date": parsed.get("transaction_date"),
        "total_amount": parsed.get("total"),
        "store_name": parsed.get("store_name"),
        "image_path": image_path,

        # JSONB
        "details": parsed.get("items", [])
    }