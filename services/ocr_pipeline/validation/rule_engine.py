def log_event(draft: dict, stage: str, message: str, meta: dict = None):
    event = {
        "stage": stage,
        "message": message,
    }

    if meta is not None:
        event["meta"] = meta

    draft.setdefault("events", []).append(event)

def validate(draft: dict) -> dict:
    items = draft.get("items", [])
    totals = draft.get("total_candidates", [])

    if not totals:
        draft["validation_status"] = "NO_TOTAL"
        log_event(draft, "VALIDATION", "No total candidate found.")
        return draft

    item_sum = sum(
        item.get("quantity", 1) * item.get("price", 0)
        for item in items
    )

    log_event(
        draft,
        "CALC_SUM",
        "Calculated item sum",
        {"item_sum": item_sum}
    )

    base_tol = 10
    ratio_tol = int(item_sum * 0.005)
    tolerance = max(base_tol, ratio_tol)

    log_event(
        draft,
        "VALIDATION",
        "Tolerance applied",
        {"tolerance": tolerance}
    )

    matching = []
    for t in totals:
        value = t.get("value")
        if value is None:
            continue

        diff = abs(item_sum - value)
        if diff <= tolerance:
            matching.append({**t, "_diff": diff})

    # -----------------------------
    # 1️⃣ 단일 매칭
    # -----------------------------
    if len(matching) == 1:
        chosen = matching[0]

        draft["total_candidates"] = [
            {k: v for k, v in chosen.items() if k != "_diff"}
        ]
        draft["validation_status"] = "OK"

        log_event(
            draft,
            "VALIDATION",
            "Validation successful",
            {
                "chosen_total": chosen.get("value"),
                "diff": chosen["_diff"],
                "score": chosen.get("score")
            }
        )

        return draft

    # -----------------------------
    # 2️⃣ 다중 매칭
    # -----------------------------
    if len(matching) > 1:
        chosen = min(
            matching,
            key=lambda x: (x["_diff"], -x.get("score", 0))
        )

        draft["total_candidates"] = [
            {k: v for k, v in chosen.items() if k != "_diff"}
        ]
        draft["validation_status"] = "OK"

        log_event(
            draft,
            "VALIDATION",
            "Validation successful",
            {
                "chosen_total": chosen.get("value"),
                "diff": chosen["_diff"],
                "score": chosen.get("score")
            }
        )

        return draft

    # -----------------------------
    # 3️⃣ 불일치
    # -----------------------------
    if len(totals) == 1:
        total_value = totals[0].get("value")
        draft["validation_status"] = "MISMATCH"

        log_event(
            draft,
            "VALIDATION",
            "Mismatch detected",
            {
                "item_sum": item_sum,
                "total": total_value,
                "diff": abs(item_sum - total_value)
            }
        )

        return draft

    draft["validation_status"] = "AMBIGUOUS"
    log_event(
        draft,
        "VALIDATION",
        "Multiple total candidates found but none matched."
    )

    return draft
