from functools import lru_cache

from dto import AgentResponse, Source
from loader import retrieve_docs


class AgentService:
    def __init__(self, retriever):
        self.retriever = retriever

    def run_retrieve(self, question: str) -> AgentResponse:
        print(question)
        search_list = retrieve_docs(question)
        return AgentResponse(
            used_tool="retrieve_docs",
            reason="일반 설명형 질문으로 판단되어 문서 기반 검색 사용",
            sources=[Source(path="zxcvasdf", line=42, score=0.92)],
            answer="요약: 토큰은 만료 전 리프레시 토큰으로 갱신됩니다."
        )
