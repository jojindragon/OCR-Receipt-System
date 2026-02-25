import re


def parse_text(ocr_result: dict) -> dict:
    """
    Layout-aware parser.
    Supports:
    - Google Vision structured lines
    - Fallback to raw text if lines not present
    """

    # -------------------------
    # 1️⃣ 라인 확보
    # -------------------------
    if "lines" in ocr_result and ocr_result["lines"]:
        # layout 기반 라인 사용
        lines = [line["text"].strip() for line in ocr_result["lines"] if line["text"].strip()]
    else:
        raw_text = ocr_result.get("raw", "")
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        lines = _merge_split_numbers(lines)

    # -------------------------
    # 2️⃣ 아이템 추출
    # -------------------------
    items = _extract_items(lines)

    # -------------------------
    # 3️⃣ total 후보 추출
    # -------------------------
    total_candidates = _extract_total_candidates(lines)

    return {
        "items": items,
        "total_candidates": total_candidates
    }


# ---------------------------------------------
# 숫자 분리 보정 (fallback raw 전용)
# ---------------------------------------------
def _merge_split_numbers(lines: list) -> list:
    merged = []
    i = 0

    while i < len(lines):
        current = lines[i]

        if (
            current.isdigit()
            and i + 1 < len(lines)
            and lines[i + 1].isdigit()
        ):
            merged.append(current + lines[i + 1])
            i += 2
        else:
            merged.append(current)
            i += 1

    return merged


# ---------------------------------------------
# Layout-aware 아이템 추출
# ---------------------------------------------
# TODO:
# Replace heuristic name recovery with column clustering (next phase)
def _extract_items(lines: list) -> list:
    items = []

    HEADER_KEYWORDS = ["단가", "수량", "금액", "상품코드", "합계"]

    for idx, line in enumerate(lines):
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*', line)

        if len(numbers) < 3:
            continue

        try:
            nums = [int(n.replace(",", "")) for n in numbers]
            amount = nums[-1]

            for i in range(len(nums) - 2):
                price = nums[i]
                quantity = nums[i + 1]

                if price * quantity == amount:

                    name_candidate = ""

                    # 🔍 위쪽 최대 4줄 탐색
                    for back in range(1, 5):
                        if idx - back < 0:
                            break

                        candidate_line = lines[idx - back].strip()

                        # 숫자 위주 줄 제외
                        if re.fullmatch(r'[\d\*,\s]+', candidate_line):
                            continue

                        # 바코드 제외
                        if candidate_line.startswith("*"):
                            continue

                        # 헤더 제외
                        if any(h in candidate_line for h in HEADER_KEYWORDS):
                            continue

                        # 너무 짧은 줄 제외
                        if len(candidate_line) < 3:
                            continue

                        name_candidate = candidate_line
                        break

                    if not name_candidate:
                        name_candidate = "UNKNOWN"

                    items.append({
                        "name": name_candidate,
                        "quantity": quantity,
                        "price": price
                    })
                    break

        except Exception:
            continue

    return items


# ---------------------------------------------
# Total 후보 추출
# ---------------------------------------------
def _extract_total_candidates(lines: list) -> list:
    candidates = []

    total_keywords = ["합계", "합", "계", "TOTAL", "총액"]

    for idx, line in enumerate(lines):

        cleaned = line.replace(",", "")
        numbers = re.findall(r'\d{4,}', cleaned)

        if not numbers:
            continue

        value = int(numbers[-1])

        score = 0

        # 키워드 가중치
        if any(k in line for k in total_keywords):
            score += 3

        # 하단 위치 가중치
        if idx > len(lines) * 0.7:
            score += 2

        # 값 크기 가중치
        score += min(value // 10000, 3)

        candidates.append({
            "label": line.strip(),
            "value": value,
            "score": score,
            "source": "heuristic_line"
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)

    return candidates[:3]
