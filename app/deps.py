from __future__ import annotations


from functools import lru_cache
from typing import TYPE_CHECKING

from app.agent.service import AgentService
from app.llm.factory import create_embedder, create_llm_client
from app.repository.factory import create_chunk_repository
from app.storage.factory import create_image_storage

if TYPE_CHECKING:
    from app.llm.embedder import Embedder


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
