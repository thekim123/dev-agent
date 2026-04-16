import uuid

from fastapi import UploadFile, File, HTTPException, APIRouter
from fastapi.params import Depends

from app.deps import get_image_storage

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB
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
    storage.put(key, data, content_type=file.content_type)
    return {"key": key}
