import re
from collections.abc import Callable

from app.agent.dto import AgentResponse, Source, BedrockResponse
from app.agent.models import RouteDecision
from app.repository.base import ChunkRepository
from app.repository.models import ChunkSearchHit

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


def _build_snippet(text: str, limit: int = 220) -> str:
    normalized = text.replace("\n", " ").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit] + " ..."


def _to_source(hit: ChunkSearchHit) -> Source:
    return Source(
        path=hit.source_path,
        snippet=_build_snippet(hit.text),
        score=hit.score,
    )


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
        return f"가장 관련 높은 구현은 `{query_results[0].source_path}`에 있습니다."

    top_paths = [f"{i + 1}. {item.source_path}" for i, item in enumerate(query_results[:3])]
    return '관련 구현 후보를 찾았습니다. 아래 파일들을 먼저 확인해보세요. \n' + '\n'.join(top_paths)


def _extract_terms(question: str) -> list[str]:
    terms = re.findall(r"[a-zA-Z0-9_]+|[가-힣]+", question.lower())
    return [t for t in terms if len(t) >= 2 and t not in STOPWORDS]


class AgentService:
    def __init__(
            self,
            repository: ChunkRepository,
            embed: Callable[[str], list[float]],
            query_to_llm: Callable[[str, str], str]
    ):
        self.repository = repository
        self.embed = embed
        self.query_to_llm = query_to_llm

    def answer(self, question: str) -> AgentResponse:
        route_decision = self._route(question)
        if route_decision.tool == "direct":
            return AgentResponse(
                used_tool=route_decision.tool,
                reason=route_decision.reason,
                sources=[],
                answer=route_decision.direct_answer
            )

        if route_decision.tool == "search_repo":
            terms = _extract_terms(route_decision.routed_question)
            query_results = self.repository.search_by_term(terms)
            sources = [_to_source(result) for result in query_results]
            return AgentResponse(
                used_tool=route_decision.tool,
                reason=route_decision.reason,
                sources=sources,
                answer=_build_answer(query_results)
            )

        bedrock_response = self.retrieve_docs(route_decision.routed_question)
        if not bedrock_response.chunks:
            return AgentResponse(
                used_tool=route_decision.tool,
                reason=route_decision.reason,
                sources=[],
                answer="지금 가지고 있는 자료에서는 마땅한게 없네요."
            )

        top = bedrock_response.chunks[:3]
        remove_duplicates = [top[0]]
        exist_path = [top[0].source_path]
        for t in top:
            if t.source_path not in exist_path:
                exist_path.append(t.source_path)
                remove_duplicates.append(t)

        sources = [_to_source(chunk) for chunk in remove_duplicates]
        api_response = AgentResponse(
            used_tool="retrieve_docs",
            reason="문서 임베딩 검색 기반",
            sources=sources,
            answer=bedrock_response.answer
        )
        return api_response

    def _route(self, question: str) -> RouteDecision:
        normalized = _normalize_question(question=question)
        directed_answer = _get_direct_answer(normalized)
        if directed_answer:
            return RouteDecision(
                tool="direct",
                routed_question=normalized,
                reason="짧은 대화형 질문으로 판단",
                direct_answer=directed_answer
            )

        stripped = _strip_greeting_prefix(normalized)
        if not stripped:
            return RouteDecision(
                tool="direct",
                routed_question=normalized,
                reason="인사만 포함된 질문으로 판단",
                direct_answer="안녕하세요. 질문을 주시면 바로 찾아보겠습니다."
            )

        if _is_repo_question(stripped):
            return RouteDecision(
                tool="search_repo",
                routed_question=stripped,
                reason="코드 위치/파일 탐색 질문으로 판단",
                direct_answer=None
            )

        if _is_doc_question(stripped):
            return RouteDecision(
                tool="retrieve_docs",
                routed_question=stripped,
                reason="설명/요약 질문으로 판단",
                direct_answer=None
            )

        return RouteDecision(
            tool="retrieve_docs",
            routed_question=stripped,
            reason="애매해서 retrieval 기본값 사용",
            direct_answer=None
        )

    # loader.load_vector_store, loader.search_chunks를 감싸서
    # retrieve_docs(question)를 만들고,
    # 반환값에 chunk_id/source_path/start/end/score를 붙여줘.
    def retrieve_docs(self, question: str) -> BedrockResponse:
        query_emb = self.embed(question)
        search_list = self.repository.search_similar(query_emb)
        if not search_list:
            return BedrockResponse(
                answer="검색된 자료가 없습니다.",
                chunks=[]
            )

        if search_list[0].score < 0.4:
            response = BedrockResponse(
                answer='지금 가지고 있는 자료에서는 마땅한 데이터가 없네요.... 잘 모르겠어요....',
                chunks=[]
            )
            return response

        else:
            doc_text = ''
            for doc in search_list:
                doc_text += doc.text
            query_result = self.query_to_llm(doc_text, question)
            # print(query_result[0]["text"])
            response = BedrockResponse(answer=query_result, chunks=search_list)
            return response
