# [변경] import 경로를 ocr_pipeline2 기준으로 변경 (원본 ocr_pipeline 모듈과 분리)
from services.ocr_pipeline2.logging.logger import PipelineLogger
from services.ocr_pipeline2.ocr.google_vision_adapter import GoogleVisionAdapter
from services.ocr_pipeline2.parsing.parser import parse_text
from services.ocr_pipeline2.pipeline.draft_builder import build_draft
from services.ocr_pipeline2.validation.validator import validate_receipt
from services.ocr_pipeline2.persistence.db_mapper import map_to_db_schema
# [변경] create_receipt import 제거 - 프론트엔드에서 저장 버튼 클릭 시 직접 호출하도록 변경
# from backend.api.receipts import create_receipt
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

        draft["validation_status"] = validation["validation_status"]
        draft["issues"] = validation["issues"]

        # [변경] DB Insert를 파이프라인에서 자동 실행하지 않고, db_payload만 준비
        # 프론트엔드에서 사용자가 "저장" 버튼을 클릭할 때 직접 DB에 저장함
        if validation["validation_status"] == "success":
            db_schema = map_to_db_schema(image_path, parsed)
            draft["db_insert_ready"] = True
            draft["db_payload"] = db_schema

            # [변경] 아래 자동 DB 저장 로직 제거
            # try:
            #     db_result = create_receipt(
            #         user_id=db_schema["user_id"],
            #         category_id=db_schema["category_id"],
            #         payment_method_id=db_schema["payment_method_id"],
            #         date=db_schema["date"],
            #         total_amount=db_schema["total_amount"],
            #         store_name=db_schema["store_name"],
            #         image_path=db_schema["image_path"],
            #         details=db_schema["details"]
            #     )
            #
            #     draft["db_inserted"] = True
            #     draft["db_response"] = db_result
            #
            # except Exception as e:
            #     draft["db_inserted"] = False
            #     draft["db_error"] = str(e)

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