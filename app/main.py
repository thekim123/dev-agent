from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.agent.service import AgentService
from app.api import agent, images, health
from app.api.exception_handler import generic_exception_handler
from app.config import settings
from app.llm.factory import create_embedder, create_llm_client
from app.middleware.request_id import RequestIdMiddleware
from app.repository.factory import create_chunk_repository
from app.storage.factory import create_image_storage


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    image_storage = create_image_storage()
    embedder = create_embedder()
    chunk_repository = create_chunk_repository()
    llm_client = create_llm_client()

    agent_service = AgentService(
        repository=chunk_repository,
        embed=embedder.embed,
        query_to_llm=llm_client.query_to_llm,
    )

    app.state.image_storage = image_storage
    app.state.embedder = embedder
    app.state.chunk_repository = chunk_repository
    app.state.llm_client = llm_client
    app.state.agent_service = agent_service
    yield
    if hasattr(chunk_repository, "close"):
        await chunk_repository.close()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(health.router)
app.include_router(agent.router)
app.include_router(images.router)
