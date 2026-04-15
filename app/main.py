from __future__ import annotations

import uuid
from functools import lru_cache
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File

from app.agent.dto import AgentResponse, AgentRequest
from app.agent.service import AgentService
from app.llm.factory import create_embedder, create_llm_client
from app.repository.factory import create_chunk_repository
from app.storage.factory import create_image_storage

if TYPE_CHECKING:
    from app.llm.embedder import Embedder

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB

load_dotenv()
app = FastAPI()


@lru_cache
def get_image_storage():
    return create_image_storage()


@lru_cache
def get_embedder() -> Embedder:
    return create_embedder()


@lru_cache
def get_chunk_repository():
    repository = create_chunk_repository()
    if repository.count() == 0:
        raise Exception('there is no vector store.')
    return repository


@lru_cache
def get_llm_client():
    return create_llm_client()


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService(
        repository=get_chunk_repository(),
        embed=get_embedder().embed,
        query_to_llm=get_llm_client().query_to_llm
    )


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/agent", response_model=AgentResponse, summary="질문 한 개만 받아서 에이전트 처리")
async def agent(
        req: AgentRequest,
        service: AgentService = Depends(get_agent_service),
):
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    api_response = service.answer(question)
    return api_response


@app.post("/images", summary="이미지 업로드 -> object key 반환")
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
