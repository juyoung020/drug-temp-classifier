import numpy as np


def extract_dominant_color(image_bytes: bytes) -> str:
    import cv2

    arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        return "other"

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 채도·명도가 있는 픽셀만 사용 (흰 배경·어두운 영역 제외)
    mask = cv2.inRange(hsv, np.array([0, 40, 40]), np.array([180, 255, 255]))

    if cv2.countNonZero(mask) < 200:
        avg_v = float(np.mean(hsv[:, :, 2]))
        return "white" if avg_v > 180 else "transparent"

    hist = cv2.calcHist([hsv], [0], mask, [18], [0, 180])
    hue = int(np.argmax(hist)) * 10  # bin 중앙 hue 값 (0~170)

    if hue <= 10 or hue >= 170:
        return "red"
    elif hue <= 25:
        return "orange"
    elif hue <= 35:
        return "yellow"
    elif hue <= 85:
        return "green"
    elif hue <= 130:
        return "blue"
    elif hue <= 150:
        return "purple"
    else:
        return "pink"


_clip_model = None
_clip_processor = None

_FORM_LABELS = [
    "an elongated pen-shaped insulin injection device",
    "a small glass ampoule or medicine vial",
    "a hypodermic syringe with needle",
    "a round flat tablet or capsule pill",
    "a plastic medicine bottle with cap",
    "a flexible transparent blood bag or IV bag with tubes",
    "a blister pack or cardboard medicine box",
]


def _get_clip():
    global _clip_model, _clip_processor
    if _clip_model is None:
        from transformers import CLIPModel, CLIPProcessor
        _clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return _clip_model, _clip_processor


def detect_form(image_bytes: bytes) -> str:
    try:
        import cv2
        import torch
        from PIL import Image

        arr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            return "other"

        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        image   = Image.fromarray(img_rgb)

        model, processor = _get_clip()
        inputs = processor(text=_FORM_LABELS, images=image, return_tensors="pt", padding=True)

        with torch.no_grad():
            probs = model(**inputs).logits_per_image.softmax(dim=1)

        return _FORM_LABELS[probs.argmax().item()]

    except Exception:
        return "other"
