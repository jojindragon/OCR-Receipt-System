class OCRAdapter:
    """
    Base interface for OCR adapters.
    """

    def run(self, image_path: str) -> dict:
        """
        Returns:
        {
            "adapter": str,
            "raw": str,
            "words": list,   # optional structured word-level data
            "lines": list    # optional structured line-level data
        }

        NOTE:
        - Minimal adapters may return only 'raw'.
        - Advanced adapters (e.g., Google Vision) should return
          layout-aware structure for downstream parsing.
        """
        raise NotImplementedError
