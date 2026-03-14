import re
from typing import Literal

from app.agent.dto import AgentResponse, Source, BedrockResponse
from app.ingestion.loader import bedrock, search_chunks


REPO_KEYWORDS = ("어디", "파일", "함수", "클래스")
DOC_KEYWORDS = ("설명", "요약", "의미", "왜", "동작", "흐름", "정리")
STOPWORDS = {"어디", "설명", "해줘", "해주세요", "무엇", "뭐", "찾아줘", "찾아", "관련", "있는", "인가", "이거"}
DIRECT_PATTERNS = {
    "greeting": ["안녕", "하이", "hello"],
    "capability": ["뭐 할 수 있어", "무엇을 할 수 있어", "너 누구야"],
    "thanks": ["고마워", "thanks"],
}

GREETING_PREFIX_RE = re.compile(
    r"^\s*(안녕|하이|hello|hi)[!?.~\s,]*",
    re.IGNORECASE,
)

DIRECT_RULES = [
    (
        re.compile(r"^\s*(안녕|하이|hello|hi)[!?.~\s]*$", re.IGNORECASE),
        "안녕하세요. 코드 위치 탐색과 문서 설명을 도와드릴 수 있습니다.",
    ),
    (
        re.compile(r"^\s*(너\s*)?(뭐|무엇)을?\s*할\s*수\s*있어[?!.~\s]*$", re.IGNORECASE),
        "문서 설명 질문은 retrieve_docs로, 코드 위치 질문은 search_repo로 처리할 수 있습니다.",
    ),
    (
        re.compile(r"^\s*(너\s*)?누구야[?!.~\s]*$", re.IGNORECASE),
        "질문을 받아 문서 검색이나 코드 위치 탐색을 수행하는 에이전트입니다.",
    ),
    (
        re.compile(r"^\s*(고마워|감사|thanks)[!?.~\s]*$", re.IGNORECASE),
        "필요한 질문을 이어서 주시면 됩니다.",
    ),
]

greeting = '안녕하세요. 문서 설명 질문은 retrieve_docs로, 코드 위치 질문은 search_repo로 도와드릴 수 있습니다.'
capability = '문서 내용 설명, 코드 위치 탐색, 관련 파일 안내를 도와드릴 수 있습니다.'
thanks = '필요한 질문을 이어서 주시면 됩니다.'
SNIPPET_LEN = 220


class Retriever:
    def __init__(self, embedder, chunks):
        self.embedder = embedder
        self.chunks = chunks


def _normalize_question(question: str) -> str:
    return re.sub(r"\s+", " ", question).strip()


def _strip_greeting_prefix(question: str) -> str:
    return GREETING_PREFIX_RE.sub("", question, count=1).strip()


def _get_direct_answer(question) -> str | None:
    for pattern, answer in DIRECT_RULES:
        if pattern.fullmatch(question):
            return answer
    return None


def _is_repo_question(q: str) -> bool:
    return any(k in q for k in REPO_KEYWORDS)


def _is_doc_question(question: str) -> bool:
    return any(k in question for k in DOC_KEYWORDS)


def _build_answer(query_results):
    if not query_results:
        return "관련 위치를 찾지 못했습니다. 검색어를 더 구체적으로 바꿔보세요."
    if len(query_results) == 1:
        return f"가장 관련 높은 구현은 `{query_results[0]['path']}`에 있습니다."

    top_paths = [f"{i + 1}. {item['path']}" for i, item in enumerate(query_results[:3])]
    return '관련 구현 후보를 찾았습니다. 아래 파일들을 먼저 확인해보세요. \n' + '\n'.join(top_paths)


def _extract_terms(question: str) -> list[str]:
    terms = re.findall(r"[a-zA-Z0-9_]+|[가-힣]+", question.lower())
    return [t for t in terms if len(t) >= 2 and t not in STOPWORDS]


class AgentService:
    def __init__(self, retriever):
        self.retriever = retriever

    def answer(self, question: str) -> AgentResponse:
        used_tool, routed_question, reason, direct_answer = self._route(question)
        if used_tool == "direct":
            return AgentResponse(
                used_tool=used_tool,
                reason=reason,
                sources=[],
                answer=direct_answer
            )

        if used_tool == "search_repo":
            query_results = self.search_repo(routed_question)
            return AgentResponse(
                used_tool=used_tool,
                reason=reason,
                sources=query_results,
                answer=_build_answer(query_results)
            )

        bedrock_response = self.retrieve_docs(routed_question)
        if not bedrock_response.chunks:
            return AgentResponse(
                used_tool=used_tool,
                reason=reason,
                sources=[],
                answer="지금 가지고 있는 자료에서는 마땅한게 없네요."
            )

        top = bedrock_response.chunks[:3]
        sources = [
            Source(
                path=chunk.source_path,
                snippet=(chunk.text[:SNIPPET_LEN] + " ...").replace("\n", " "),
                line=chunk.start,
                score=float(score)
            )
            for score, chunk in top
        ]

        api_response = AgentResponse(
            used_tool="retrieve_docs",
            reason="문서 임베딩 검색 기반",
            sources=sources,
            answer=bedrock_response.answer
        )
        return api_response

    def _route(self, question: str) -> tuple[Literal["direct", "search_repo", "retrieve_docs"], str, str, str | None]:
        normalized = _normalize_question(question=question)
        directed_answer = _get_direct_answer(normalized)
        if directed_answer:
            return "direct", normalized, "짧은 대화형 질문으로 판단", directed_answer

        stripped = _strip_greeting_prefix(normalized)
        if not stripped:
            return "direct", normalized, "인사만 포함된 질문으로 판단", "안녕하세요. 질문을 주시면 바로 찾아보겠습니다."

        if _is_repo_question(stripped):
            return "search_repo", stripped, "코드 위치/파일 탐색 질문으로 판단", None

        if _is_doc_question(stripped):
            return "retrieve_docs", stripped, "설명/요약 질문으로 판단", None

        return "retrieve_docs", stripped, "애매해서 retrieval 기본값 사용", None

    # loader.load_vector_store, loader.search_chunks를 감싸서
    # retrieve_docs(question)를 만들고,
    # 반환값에 chunk_id/source_path/start/end/score를 붙여줘.
    def retrieve_docs(self, question):
        vectors = self.retriever.chunks
        query_embed = bedrock.embed(question)
        search_list = search_chunks(query_embed, vectors)

        if search_list[0][0] < 0.4:
            print()
            response = BedrockResponse(answer='지금 가지고 있는 자료에서는 마땅한 데이터가 없네요.... 잘 모르겠어요....', chunks=[])
            return response

        else:
            doc_text = ''
            for doc in search_list:
                doc_text += doc[1].text
            query_result = bedrock.query_embed(doc_text, question)
            print(query_result[0]["text"])
            response = BedrockResponse(answer=query_result[0]["text"], chunks=search_list)
            return response

    def search_repo(self, question):
        terms = _extract_terms(question)
        results = []
        chunks = self.retriever.chunks

        for chunk in chunks:
            score = 0
            path = chunk.source_path.lower()
            text = chunk.text.lower()

            for term in terms:
                if term in path:
                    score += 10
                if term in text:
                    score += 5

            if score > 0:
                results.append({
                    "path": chunk.source_path,
                    "score": score,
                    "line": chunk.start,
                    "snippet": chunk.text[: 120]
                })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]
