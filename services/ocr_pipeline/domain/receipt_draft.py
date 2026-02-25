def to_receipt_draft(pipeline_result: dict) -> dict:
    """
    Convert pipeline output into a human-reviewable draft.
    This draft is NOT persisted directly.

    NOTE:
    - This layer isolates downstream systems (API / frontend)
      from internal pipeline structure changes.
    """

    return {
        "image_path": pipeline_result.get("image_path"),

        # Parsed items
        "items": pipeline_result.get("items", []),

        # Deterministic total candidates
        "total_candidates": pipeline_result.get("total_candidates", []),

        # Final validation result
        "validation_status": pipeline_result.get("validation_status"),

        # Structured event log for review / audit
        "events": pipeline_result.get("events", [])
    }
