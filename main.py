from functools import lru_cache

from fastapi import FastAPI, Depends

from dto import AgentResponse, AgentRequest, Source
from embedder import Embedder
from loader import load_vector_store
from service.agent_service import Retriever, AgentService

app = FastAPI()


@lru_cache
def get_retriever(self) -> Retriever:
    embedder = Embedder()
    chunks = load_vector_store()
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

    if len(question) <= 12:
        return AgentResponse(
            used_tool="direct",
            reason="짧은 일반 질문이라 즉시 응답",
            sources=[Source(path="system", snippet="no source", line=None, score=None)],
            answer=f"'{question}'에 대한 즉시 답변입니다."
        )

    if "어디" in question or "파일" in question or "함수" in question or "클래스" in question:
        return AgentResponse(
            used_tool="search_repo",
            reason="질문에 코드 위치/탐색 키워드가 포함됨",
            sources=[
                Source(
                    path="app/service/user_service.py",
                    snippet="def get_user_by_id(...):",
                    line=84,
                    score=0.97
                )
            ],
            answer="해당 구현은 `app/service/user_service.py` 84번째 줄 부근을 확인하면 됩니다."
        )

    return service.run_retrieve(question)
