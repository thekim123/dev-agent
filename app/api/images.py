import uuid

from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.params import Depends
from fastapi.responses import Response

from app.deps import get_image_storage

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB

EXT_TO_MIME = {
    "jpeg": "image/jpeg",
    "jpg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
}

router = APIRouter()


@router.post("/images", summary="이미지 업로드 -> object key 반환")
async def upload_image(
        file: UploadFile = File(...),
        storage=Depends(get_image_storage),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=415, detail=f"unsupported file type: {file.content_type}")

    data = await file.read()
    if len(data) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="file too large")

    ext = file.content_type.split("/")[1]
    key = f"{uuid.uuid4().hex}.{ext}"
    await storage.put(key, data, content_type=file.content_type)
    return {"key": key}


@router.get("/images/{key:path}", summary="이미지 조회")
async def get_image(
        key: str,
        storage=Depends(get_image_storage),
):
    try:
        data = await storage.get(key)
    except Exception:
        raise HTTPException(status_code=404, detail="image not found")

    ext = key.rsplit(".", 1)[-1].lower() if "." in key else "png"
    content_type = EXT_TO_MIME.get(ext, "image/png")

    return Response(content=data, media_type=content_type)
