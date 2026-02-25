from .base_adapter import OCRAdapter
import os


class GoogleVisionAdapter(OCRAdapter):

    def __init__(self):
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path:
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set.")

        try:
            from google.cloud import vision
        except ImportError as e:
            raise RuntimeError(
                "google-cloud-vision is not installed."
            ) from e

        self.vision = vision
        self.client = vision.ImageAnnotatorClient()

    def run(self, image_path: str) -> dict:

        with open(image_path, "rb") as f:
            content = f.read()

        image = self.vision.Image(content=content)
        # TODO:
        # Switch to document_text_detection for improved layout structure extraction
        response = self.client.text_detection(image=image)

        if response.error.message:
            raise RuntimeError(response.error.message)

        # -------------------------
        # 1️⃣ raw text 유지
        # -------------------------
        texts = response.text_annotations
        raw_text = texts[0].description if texts else ""

        # -------------------------
        # 2️⃣ word-level 구조 추출
        # -------------------------
        words = []

        annotation = response.full_text_annotation
        if annotation and annotation.pages:
            for page in annotation.pages:
                for block in page.blocks:
                    for paragraph in block.paragraphs:
                        for word in paragraph.words:

                            text = "".join(
                                [symbol.text for symbol in word.symbols]
                            )

                            vertices = word.bounding_box.vertices

                            x_min = min(v.x for v in vertices)
                            y_min = min(v.y for v in vertices)
                            x_max = max(v.x for v in vertices)
                            y_max = max(v.y for v in vertices)

                            words.append({
                                "text": text,
                                "x_min": x_min,
                                "y_min": y_min,
                                "x_max": x_max,
                                "y_max": y_max,
                                "confidence": word.confidence
                            })

        # -------------------------
        # 3️⃣ y좌표 기준 line 구성
        # -------------------------
        lines = []
        Y_THRESHOLD = 10  # 같은 줄로 묶을 y 거리 허용값

        # y_min 기준 정렬
        words_sorted = sorted(words, key=lambda w: w["y_min"])

        for word in words_sorted:
            placed = False

            for line in lines:
                if abs(line["y_center"] - word["y_min"]) < Y_THRESHOLD:
                    line["words"].append(word)
                    placed = True
                    break

            if not placed:
                lines.append({
                    "y_center": word["y_min"],
                    "words": [word]
                })

        # 각 line 내부 x좌표 기준 정렬
        for line in lines:
            line["words"].sort(key=lambda w: w["x_min"])
            line["text"] = " ".join(w["text"] for w in line["words"])

        return {
            "adapter": "google_vision",
            "raw": raw_text,
            "words": words,
            "lines": lines
        }
