def validate_receipt(parsed: dict) -> dict:
    """
    파싱 결과 자동 검증
    success / review_required / error 판정
    """

    issues = []

    store = parsed.get("store_name", "")
    total = parsed.get("total", 0)
    date = parsed.get("transaction_date", "")
    category = parsed.get("category", "기타")

    # 1️⃣ 필수값 검사
    if not store or len(store) < 2:
        issues.append("store_name_invalid")

    if total <= 0:
        issues.append("total_invalid")

    if not date:
        issues.append("date_missing")

    # 2️⃣ 의심 케이스
    if category == "기타":
        issues.append("category_uncertain")

    # 판정
    if "total_invalid" in issues or "store_name_invalid" in issues:
        status = "error"
    elif issues:
        status = "review_required"
    else:
        status = "success"

    return {
        "validation_status": status,
        "issues": issues
    }