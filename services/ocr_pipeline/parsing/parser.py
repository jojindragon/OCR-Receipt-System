import re
from datetime import datetime


# --------------------------------------------------
# 1️⃣ Store Name
# --------------------------------------------------
def extract_store_name(lines):

    store_patterns = [
        r"주문\s*매장[:：]?\s*(.+)",
        r"상호[:：]?\s*(.+)",
        r"매장명[:：]?\s*(.+)",
        r"가맹점[:：]?\s*(.+)",
    ]

    for text in lines:
        for p in store_patterns:
            m = re.search(p, text)
            if m:
                name = m.group(1).strip()
                if len(name) > 1:
                    return name

    STORE_KEYWORDS = [
        "점", "마트", "상회", "스토어", "편의점",
        "카페", "커피", "식당", "분식", "치킨", "버거"
    ]

    BLOCK_KEYWORDS = [
        "사업자", "TEL", "전화", "합계", "총액",
        "카드", "단가", "수량", "금액", "상품",
        "고객용", "주문", "요청", "주소"
    ]

    candidates = lines[:10]

    best_score = -999
    best_text = ""

    for text in candidates:
        score = 0

        if re.search(r"[가-힣]", text): score += 2
        if not re.search(r"\d", text): score += 1
        if 2 <= len(text) <= 20: score += 1
        if any(k in text for k in STORE_KEYWORDS): score += 2
        if any(k in text for k in BLOCK_KEYWORDS): score -= 5

        if score > best_score:
            best_score = score
            best_text = text

    return best_text


# --------------------------------------------------
# 2️⃣ Date
# --------------------------------------------------
def extract_date(lines):

    full_text = "\n".join(lines)

    patterns = [
        r"(\d{4}|\d{2})[-./년\s]+(\d{1,2})[-./월\s]+(\d{1,2})",
        r"(\d{4})(\d{2})(\d{2})"
    ]

    for pattern in patterns:
        for m in re.finditer(pattern, full_text):
            y, mth, d = m.groups()

            if len(y) == 2:
                y = "20" + y

            try:
                dt = datetime(int(y), int(mth), int(d))
                if 2010 <= dt.year <= 2030:
                    return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue

    return ""


# --------------------------------------------------
# 3️⃣ Total (🔥 강화 로직)
# --------------------------------------------------
def extract_total(lines):

    SKIP_KEYWORDS = ["받은금액", "상품권", "거스름", "내신금액", "면세", "과세", "부가세"]

    TOTAL_PATTERN = r"(합\s*계|결\s*제\s*대\s*상|총\s*액|결\s*제\s*금\s*액)"

    # 1차 시도
    for i, text in enumerate(lines):

        if any(s in text.replace(" ", "") for s in SKIP_KEYWORDS):
            continue

        if re.search(TOTAL_PATTERN, text.replace(" ", "")):

            nums = re.findall(r"\d{1,3}(?:,\d{3})+", text)
            if nums:
                return int(nums[-1].replace(",", ""))

            for j in range(1, 4):
                if i + j < len(lines):
                    next_line = lines[i+j]

                    if any(s in next_line.replace(" ", "") for s in SKIP_KEYWORDS):
                        break

                    nums = re.findall(r"\d{1,3}(?:,\d{3})+", next_line)
                    if nums:
                        return int(nums[-1].replace(",", ""))

    # 2차 시도
    all_nums = []

    for text in lines:
        clean_text = text.replace(" ", "")

        if any(s in clean_text for s in SKIP_KEYWORDS): continue
        if any(char in text for char in [":", "-"]): continue

        nums = re.findall(r"\d{1,3}(?:,\d{3})+", text)

        for n in nums:
            val = int(n.replace(",", ""))
            if val >= 500:
                all_nums.append(val)

    return max(all_nums) if all_nums else 0


# --------------------------------------------------
# 4️⃣ Payment
# --------------------------------------------------
def extract_payment(lines):
    for text in lines:
        if "카드" in text:
            return "card"
        if "현금" in text:
            return "cash"
        if "페이" in text:
            return "app"
    return ""


# --------------------------------------------------
# 5️⃣ Category
# --------------------------------------------------
CATEGORY_RULES = {
    "식비": ["식당", "김밥", "국밥", "치킨", "피자", "버거", "쌀국수"],
    "카페": ["카페", "커피", "스타벅스", "이디야", "투썸", "메가커피"],
    "편의점": ["CU", "GS25", "세븐일레븐", "이마트24"],
    "교통": ["택시", "카카오T", "버스", "지하철", "KTX"],
    "주유": ["주유", "SK에너지", "GS칼텍스", "현대오일뱅크", "S-OIL"],
    "쇼핑": ["쿠팡", "11번가", "이마트", "홈플러스", "롯데마트", "백화점"],
    "의료": ["약국", "병원", "치과", "한의원"]
}


def classify_category(store_name, full_text):

    store_upper = store_name.upper()
    text_upper = full_text.upper()

    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw.upper() in store_upper:
                return category

    top_text = "\n".join(full_text.split("\n")[:10]).upper()

    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw.upper() in top_text:
                return category

    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw.upper() in text_upper:
                return category

    return "기타"


# --------------------------------------------------
# 🔥 최종 파이프라인 entry
# --------------------------------------------------
def parse_text(ocr_result: dict) -> dict:

    lines = [l.strip() for l in ocr_result["full_text"].split("\n") if l.strip()]

    store = extract_store_name(lines)
    date = extract_date(lines)
    total = extract_total(lines)
    payment = extract_payment(lines)
    category = classify_category(store, ocr_result["full_text"])

    return {
        "store_name": store,
        "transaction_date": date,
        "total": total,
        "payment": payment,
        "category": category,
        "items": []
    }