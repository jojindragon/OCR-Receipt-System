# services/ocr_pipeline/run_pipeline.py

from services.ocr_pipeline.logging.logger import PipelineLogger
from services.ocr_pipeline.ocr.google_vision_adapter import GoogleVisionAdapter
from services.ocr_pipeline.parsing.parser import parse_text
from services.ocr_pipeline.pipeline.draft_builder import build_draft
from services.ocr_pipeline.validation.validator import validate_receipt
from services.ocr_pipeline.persistence.db_mapper import map_to_db_schema
from services.ocr_pipeline.domain.receipt_draft import to_receipt_draft
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def run_pipeline(image_path: str, verbose: bool = True) -> dict:

    logger = PipelineLogger(verbose=verbose)

    try:
        # OCR
        adapter = GoogleVisionAdapter()
        ocr_result = adapter.run(image_path)
        logger.log_event("OCR", "텍스트 추출 완료")

        # Parsing
        parsed = parse_text(ocr_result)
        logger.log_event("PARSING", "파싱 완료")

        # Validation
        validation = validate_receipt(parsed)
        parsed.update(validation)

        logger.log_event(
            "VALIDATION",
            validation["validation_status"],
            {"issues": validation["issues"]}
        )

        # Draft 생성
        draft = build_draft(image_path, parsed)
        draft["events"] = logger.get_events()

        # DB Insert 준비 여부 판단(validation 성공 시에만)
        if validation["validation_status"] == "success":
            db_schema = map_to_db_schema(image_path, parsed)
            draft["db_insert_ready"] = True
            draft["db_payload"] = db_schema
        else:
            draft["db_insert_ready"] = False

        return draft

    except Exception as e:
        logger.log_error("PIPELINE", e)
        return {
            "image_path": image_path,
            "validation_status": "error",
            "events": logger.get_events()
        }
    
if __name__ == "__main__":
    image_path = Path("data/receipts/v01_eval/r1.jpg")
    result = run_pipeline(str(image_path), verbose=True)
    print(result)