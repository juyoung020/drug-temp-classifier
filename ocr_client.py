import io
import numpy as np

_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        import easyocr
        _reader = easyocr.Reader(["ko", "en"], gpu=False, verbose=False)
    return _reader


def extract_text(image_bytes: bytes, min_confidence: float = 0.3) -> str:
    """이미지에서 텍스트 추출. 신뢰도 min_confidence 이상만 반환."""
    import cv2
    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    results = _get_reader().readtext(img)
    tokens = [text for (_, text, conf) in results if conf >= min_confidence]
    return " ".join(tokens).strip()
