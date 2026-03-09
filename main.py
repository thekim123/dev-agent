from fastapi import FastAPI

from dto import AgentResponse, AgentRequest, Source

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


@app.post("/agent", response_model=AgentResponse, summary="질문 한 개만 받아서 에이전트 처리")
async def agent(req: AgentRequest):
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

    return AgentResponse(
        used_tool="retrieve_docs",
        reason="일반 설명형 질문으로 판단되어 문서 기반 검색 사용",
        sources=[Source(path="zxcvasdf", line=42, score=0.92)],
        answer="요약: 토큰은 만료 전 리프레시 토큰으로 갱신됩니다."
    )
