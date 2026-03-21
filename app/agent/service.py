import json
import re
from collections.abc import Callable

from app.agent.dto import AgentResponse, Source, BedrockResponse
from app.agent.models import RouteDecision
from app.repository.base import ChunkRepository
from app.repository.models import ChunkSearchHit

STOPWORDS = {"어디", "설명", "해줘", "해주세요", "무엇", "뭐", "찾아줘", "찾아", "관련", "있는", "인가", "이거"}


def _build_snippet(text: str, limit: int = 220) -> str:
    normalized = text.replace("\n", " ").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[:limit] + " ..."


def _extract_markdown(text: str) -> str:
    match = re.search(r'\{.*}', text, re.DOTALL)
    if match:
        return match.group()
    return text


def _to_source(hit: ChunkSearchHit) -> Source:
    return Source(
        path=hit.source_path,
        snippet=_build_snippet(hit.text),
        score=hit.score,
    )


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


def _build_retrieve_prompt(search_list, question):
    query_text = f'아래의 문서를 참고하여 답하라. {question}\n'
    doc_text = ''
    for doc in search_list:
        doc_text += doc.text
    query_text += doc_text
    return query_text


def _build_route_prompt(question: str) -> str:
    return f"""
            아래의 도구중 질문에 가장 알맞는 도구를 골라서 json으로 반환하라.
            고른 도구의 이름은 tool에 적는다.
            도구를 고른 이유는 reason항목에 적는다.
            tool이 direct일 경우에는 direct answer에 그 답을 적어서 반환한다.
            
            유저의 질문의 의도가 명시되도록 안녕?이라거나 아 근데와 같은 불필요한 
            말을 잘라내고 routed_question에 적는다.
            
            응답 프로토콜은 아래와 같다.
            {{
                \"tool\": \"\",
                \"routed_question\": \"\",
                \"reason\": \"\",
                \"direct_answer\": \"\"
            }}
            
            당신이 사용할 수 있는 도구는 아래와 같다.
            direct: 현재 가지고 있는 프로젝트에 대한 질문이 아닌 경우
            search_repo: 현재 가지고 있는 프로젝트 중에서 코드의 위치를 파악하는 도구
            retrieve_docs: 현재 가지고 있는 프로젝트에 대해서 질의를 하고자 하는경우
            
            질문: {question}
        """


class AgentService:
    def __init__(
            self,
            repository: ChunkRepository,
            embed: Callable[[str], list[float]],
            query_to_llm: Callable[[str], str]
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
        prompt = _build_route_prompt(question)
        routed = self.query_to_llm(prompt)
        routed = _extract_markdown(routed)
        routed_json = json.loads(routed)
        return RouteDecision(
            tool=routed_json["tool"],
            routed_question=routed_json["routed_question"],
            reason=routed_json["reason"],
            direct_answer=routed_json["direct_answer"]
        )

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
            prompt = _build_retrieve_prompt(search_list, question)
            query_result = self.query_to_llm(prompt)
            response = BedrockResponse(answer=query_result, chunks=search_list)
            return response
