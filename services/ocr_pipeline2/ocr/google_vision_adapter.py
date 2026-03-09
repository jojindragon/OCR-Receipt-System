from .base_adapter import OCRAdapter
import os


class GoogleVisionAdapter(OCRAdapter):

    def __init__(self):
        cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path:
            raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS not set.")

        from google.cloud import vision
        self.vision = vision
        self.client = vision.ImageAnnotatorClient()

    def run(self, image_path: str) -> dict:

        with open(image_path, "rb") as f:
            content = f.read()

        image = self.vision.Image(content=content)
        response = self.client.text_detection(image=image)

        if response.error.message:
            raise RuntimeError(response.error.message)

        texts = response.text_annotations
        raw_text = texts[0].description if texts else ""

        return {
            "adapter": "google_vision",
            "image_name": image_path,
            "full_text": raw_text
        }