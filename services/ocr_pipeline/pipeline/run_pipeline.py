from services.ocr_pipeline.logging.logger import PipelineLogger
from services.ocr_pipeline.validation.rule_engine import validate
from services.ocr_pipeline.ocr.google_vision_adapter import GoogleVisionAdapter
from services.ocr_pipeline.parsing.parser import parse_text
from services.ocr_pipeline.pipeline.draft_builder import build_draft

from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


def run_pipeline(image_path: str, verbose: bool = True) -> dict:
    logger = PipelineLogger(verbose=verbose)

    # 1️⃣ OCR Adapter
    adapter = GoogleVisionAdapter()
    ocr_result = adapter.run(image_path)

    if verbose:
        logger.log_event("OCR", "Google Vision extraction completed.")

    # 2️⃣ Parsing (layout-aware)
    parsed = parse_text(ocr_result)
    logger.log_event("PARSING", "Parsing completed.")

    # 3️⃣ Draft Building
    draft = build_draft(image_path, parsed)

    # 4️⃣ Validation
    draft = validate(draft)
    logger.log_event(
        "VALIDATION",
        f"After first validate: {draft['validation_status']}"
    )

    return draft


if __name__ == "__main__":
    result = run_pipeline(
        r"data/receipts/sample_receipt.jpg",
        verbose=True
    )
    print(result)
