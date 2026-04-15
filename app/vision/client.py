import httpx

from app.config import VISION_SERVER_URL

_base_url = VISION_SERVER_URL
timeout = 300


def blur(
        image_bytes,
        conf=0.25,
        iou=0.45,
        classes=None,
        blur_kernel=121,
        blur_sigma=0.0
) -> tuple[bytes, dict]:
    files = {"file": ("image.jpg", image_bytes, "image/jpeg")}
    data = {
        "conf": conf,
        "iou": iou,
        "blur_kernel": blur_kernel,
        "blur_sigma": blur_sigma,
    }
    if classes is not None:
        data["classes"] = classes

    with httpx.Client(base_url=_base_url, timeout=timeout) as client:
        response = client.post("/v1/blur", files=files, data=data)
        response.raise_for_status()

    meta = {
        "detections": int(response.headers.get("X-Detections", 0)),
        "total_ms": float(response.headers.get("X-Total-MS", 0)),
    }
    return response.content, meta


if __name__ == "__main__":
    with open("test_input.jpg", "rb") as f:
        img = f.read()

    jpeg, meta = blur(img)
    print(meta)
    with open("result.jpg", "wb") as f:
        f.write(jpeg)