import re
from datetime import datetime

from .dict.store_dict import STORE_CATEGORY_RULES
from .dict.item_dict import ITEM_CATEGORY_RULES

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

    EXCLUDE_KEYWORDS = [
        "받은금액", "상품권", "거스름", "내신금액", "면세", "과세", "부가세", "세액",
        "단가", "수량", "상품코드", "상품명", "품목", "가격", "할인", "할인액", "총할인*", "적립", "포인트", "쿠폰", "잔액",
        "예금", "계좌", "카드번호", "승인번호", "사업자등록번호", "전화번호", "주소", "대표자", "사업자", 
        "상호", "매장", "가맹점", "주문", "요청", "APP", "고객", "고객용", "대한민국", "영수증", "영수증용",
        "세금계산서", "계산서", "청구서", "명세서"
        ]

    PRIORITY_KEYWORDS = [
        "카드청구액", "결제대상금액", "결제금액", "결제액", "결제금", "합계", "총액", "총합계", "총금액", "총",
        "총합", "계", "총계", "금액", "청구금액", "청구액", "지불금액", "지불액", "실결제금액", "실결제액"
        "실제결제금액", "실제결제액"
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

    # 하단 15줄만 탐색 (결제 영역)
    target_lines = lines[-15:]

    PAYMENT_PRIORITY = [
        ("페이", "app"),
        ("현금", "cash"),
        ("카드", "card"),
    ]

    for keyword, label in PAYMENT_PRIORITY:
        for text in target_lines:

            # 환불 안내 문구 제외
            if "환불" in text or "지참" in text or "영수증" in text:
                continue

            if keyword in text:
                return label

    return ""


# --------------------------------------------------
# 5️⃣ Category
# --------------------------------------------------
def classify_category(store_name, full_text):

    store_upper = store_name.upper()
    text_upper = full_text.upper()

    # 1️⃣ store 기반 분류
    for category, keywords in STORE_CATEGORY_RULES.items():
        for kw in keywords:
            if kw.upper() in store_upper:
                return category

    # 2️⃣ 품목 기반 분류
    for category, keywords in ITEM_CATEGORY_RULES.items():
        for kw in keywords:
            if kw.upper() in text_upper:
                return category

    return "기타"


# --------------------------------------------------
# 최종 파이프라인 entry
# --------------------------------------------------
def parse_text(ocr_result: dict) -> dict:

    lines = [l.strip() for l in ocr_result["full_text"].split("\n") if l.strip()]

    store = extract_store_name(lines)
    date = extract_date(lines)
    total = extract_total(lines)
    payment = extract_payment(lines)
    category = classify_category(store, ocr_result["full_text"])

    full_text = ocr_result["full_text"]

    # 배달/포장 fallback
    if (not store or len(store) < 2) and (
        "배달" in full_text or
        "포장" in full_text or
        "픽업" in full_text
    ):
        store = "배달/포장"
        category = "식비"

    return {
        "store_name": store,
        "transaction_date": date,
        "total": total,
        "payment": payment,
        "category": category,
        "items": []
    }