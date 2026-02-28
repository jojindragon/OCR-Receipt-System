import re
from datetime import datetime


# --------------------------------------------------
# 1️⃣ Store Name 강화
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
                        
    BLOCK_KEYWORDS = [
        "사업자", "TEL", "전화", "합계", "총액",
        "카드", "단가", "수량", "금액", "상품",
        "고객용", "주문", "요청", "주소",
        "대한민국", "고객", "APP", "메뉴"
    ]

    candidates = lines[:5]  # 상단 5줄에서 후보 추출

    best_score = -999
    best_text = ""

    for text in candidates:
        score = 0

        if re.search(r"[가-힣A-Za-z]", text): score += 2
        if not re.search(r"\d", text): score += 2
        if 2 <= len(text) <= 25: score += 1

        # 영어 브랜드 가산점
        if re.match(r"^[A-Za-z&\-\s]+$", text):
            score += 3

        # 숫자 다수 포함 감점
        if re.search(r"\d{2,}", text):
            score -= 3

        if any(k in text for k in BLOCK_KEYWORDS):
            score -= 5

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
# 3️⃣ Total 계층형 구조로 교체
# --------------------------------------------------
def extract_total(lines):

    EXCLUDE_KEYWORDS = ["받은금액", "상품권", "거스름", "내신금액", "면세", "과세", "부가세", "세액",
        "단가", "수량", "상품코드", "상품명", "품목", "가격", "할인", "할인액", "총할인*", "적립", "포인트", "쿠폰", "잔액",
        "예금", "계좌", "카드번호", "승인번호", "사업자등록번호", "전화번호", "주소", "대표자", "사업자", 
        "상호", "매장", "가맹점", "주문", "요청", "APP", "고객", "고객용", "대한민국", "영수증", "영수증용",
        "세금계산서", "계산서", "청구서", "명세서"]

    PRIORITY_KEYWORDS = [
        "카드청구액",
        "결제대상금액",
        "결제금액",
        "결제액",
        "결제금",
        "합계",
        "총액",
        "총합계",
        "총금액",
        "총",
        "총합",
        "계",
        "총계",
        "금액",
        "청구금액",
        "청구액",
        "지불금액",
        "지불액",
        "실결제금액",
        "실결제액",
        "실제결제금액",
        "실제결제액"
    ]    

    # 1️⃣ 우선순위 기반 탐색
    for keyword in PRIORITY_KEYWORDS:
        for i, text in enumerate(lines):
            if keyword in text:

                # 같은 줄 숫자
                nums = re.findall(r"\d{1,3}(?:,\d{3})+", text)
                if nums:
                    return int(nums[-1].replace(",", ""))

                # 다음 줄 탐색
                if i + 1 < len(lines):
                    nums = re.findall(r"\d{1,3}(?:,\d{3})+", lines[i+1])
                    if nums:
                        return int(nums[-1].replace(",", ""))

    # 2️⃣ fallback 후보 수집
    candidates = []

    for text in lines:
        clean = text.replace(" ", "")

        # 할인(-) 제외
        if "-" in text:
            continue

        # 세금/단가 제외
        if any(k in clean for k in EXCLUDE_KEYWORDS):
            continue

        nums = re.findall(r"\d{1,3}(?:,\d{3})+", text)

        for n in nums:
            val = int(n.replace(",", ""))
            if val >= 500:
                candidates.append(val)

    return max(candidates) if candidates else 0


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