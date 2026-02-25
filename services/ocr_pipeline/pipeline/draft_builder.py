def build_draft(image_path: str, parsed: dict) -> dict:
    """
    Build initial receipt draft from parsed OCR output.

    This function defines the domain boundary between:
    - Parsing layer
    - Validation layer
    - Downstream consumers (API / frontend)
    """

    draft = {
        "image_path": image_path,

        # Core parsed data
        "items": parsed.get("items", []),
        "total_candidates": parsed.get("total_candidates", []),

        # Optional future fields (kept explicit for schema stability)
        "store_name": parsed.get("store_name"),
        "transaction_date": parsed.get("transaction_date"),

        # Validation state (updated by rule_engine)
        "validation_status": "INIT",

        # Structured event log (audit trace)
        "events": []
    }

    return draft
