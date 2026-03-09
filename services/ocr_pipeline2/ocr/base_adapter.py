class OCRAdapter:
    """
    OCR 어댑터 기본 인터페이스
    모든 OCR 구현체는 아래 구조를 반환해야 함
    """

    def run(self, image_path: str) -> dict:
        """
        반환 구조:

        {
            "adapter": str,        # OCR 엔진 이름
            "image_name": str,     # 입력 이미지 경로 또는 파일명
            "full_text": str       # OCR 전체 텍스트
        }

        ※ 구조 정보(words, lines 등)는 현재 파이프라인에서 사용하지 않음.
        ※ 향후 확장 시 별도 계층에서 처리.
        """
        raise NotImplementedError
