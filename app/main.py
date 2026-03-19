from functools import lru_cache

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException

from app.agent.dto import AgentResponse, AgentRequest
from app.agent.service import AgentService
from app.llm.embedder import Embedder
from app.llm.factory import create_embedder, create_llm_client
from app.repository.factory import create_chunk_repository

load_dotenv()
app = FastAPI()


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
