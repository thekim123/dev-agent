from functools import lru_cache

from fastapi import FastAPI, Depends, HTTPException

from app.agent.dto import AgentResponse, AgentRequest
from app.agent.service import Retriever, AgentService
from app.ingestion.embedder import Embedder
from app.ingestion.loader import load_vector_store

app = FastAPI()


@lru_cache
def get_retriever() -> Retriever:
    embedder = Embedder()
    chunks = load_vector_store()
    if not chunks:
        raise Exception('there is no vector store.')
    return Retriever(embedder=embedder, chunks=chunks)


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService(retriever=get_retriever())


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
