import httpx

from app.config import settings

timeout = 300


def blur(
        image_key,
        conf=0.25,
        iou=0.45,
        classes=None,
        blur_kernel=121,
        blur_sigma=0.0
) -> dict:
    data = {
        "image_key": image_key,
        "conf": conf,
        "iou": iou,
        "classes": classes,
        "blur_kernel": blur_kernel,
        "blur_sigma": blur_sigma,
    }

    with httpx.Client(base_url=settings.vision_server_url, timeout=timeout) as client:
        response = client.post("/v1/blur", json=data)
        response.raise_for_status()
    return response.json()
