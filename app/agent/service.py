import json
import re
from collections.abc import Callable

from app.agent.dto import AgentResponse, Source, BedrockResponse
from app.agent.models import RouteDecision
from app.repository.base import ChunkRepository
from app.repository.models import ChunkSearchHit

STOPWORDS = {"어디", "설명", "해줘", "해주세요", "무엇", "뭐", "찾아줘", "찾아", "관련", "있는", "인가", "이거"}
MAX_ITERATIONS = 10


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


def _build_confirm_prompt(
        question: str,
        agent_response: AgentResponse,
        route_decision: RouteDecision
) -> str:
    if agent_response is None:
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
                \"direct_answer\": \"\",
                \"is_final\": \"답변이 완료된지 여부\",
            }}
            
            당신이 사용할 수 있는 도구는 아래와 같다.
            direct: 현재 가지고 있는 프로젝트에 대한 질문이 아닌 경우
            search_repo: 현재 가지고 있는 프로젝트 중에서 코드의 위치를 파악하는 도구
            retrieve_docs: 현재 가지고 있는 프로젝트에 대해서 질의를 하고자 하는경우
            
            질문: {question}
        """

    confirm_prompt = f"""
        원래 질문은 '{question}'이었고, 거기에 대해서 '{route_decision.routed_question}'라고 물어봤어.
        그리고 답변으로는 아래와 같이 나왔어. 
        
        {agent_response.answer}
        
        이 답변이 충분한지에 대해서 아래와 같은 json으로 응답해줘.
            {{
                \"tool\": \"사용해야되는 도구 이름\",
                \"routed_question\": \"완료되지 않았다면 다음에 뭐할지\",
                \"reason\": \"그렇게 생각한 이유\",
                \"direct_answer\": \"tool이 direct일 경우에는 답변\",
                \"is_final\": \"답변이 완료된지 여부\",
            }}
            
            당신이 사용할 수 있는 도구는 아래와 같다.
            direct: 현재 가지고 있는 프로젝트에 대한 질문이 아닌 경우
            search_repo: 현재 가지고 있는 프로젝트 중에서 코드의 위치를 파악하는 도구
            retrieve_docs: 현재 가지고 있는 프로젝트에 대해서 질의를 하고자 하는경우
    """
    return confirm_prompt


def _json_to_route_decision(routed_json: dict) -> RouteDecision:
    return RouteDecision(
        tool=routed_json["tool"],
        routed_question=routed_json["routed_question"],
        reason=routed_json["reason"],
        direct_answer=routed_json["direct_answer"],
        is_final=routed_json["is_final"]
    )


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
        agent_response = None
        route_decision = None

        for _ in range(MAX_ITERATIONS):
            route_decision = self._route(question, agent_response, route_decision)
            if route_decision.is_final and agent_response is not None:
                return agent_response
            if route_decision.tool == "direct":
                return AgentResponse(
                    used_tool=route_decision.tool,
                    reason=route_decision.reason,
                    sources=[],
                    answer=route_decision.direct_answer,
                )
            agent_response = self.execute_tools(route_decision)

        # 일단은 마지막 답변 반환
        return agent_response

    def execute_tools(self, route_decision: RouteDecision) -> AgentResponse:
        if route_decision.tool == "search_repo":
            terms = _extract_terms(route_decision.routed_question)
            query_results = self.repository.search_by_term(terms)
            sources = [_to_source(result) for result in query_results]
            return AgentResponse(
                used_tool=route_decision.tool,
                reason=route_decision.reason,
                sources=sources,
                answer=_build_answer(query_results),
            )

        bedrock_response = self.retrieve_docs(route_decision.routed_question)
        if not bedrock_response.chunks:
            return AgentResponse(
                used_tool=route_decision.tool,
                reason=route_decision.reason,
                sources=[],
                answer="지금 가지고 있는 자료에서는 마땅한게 없네요.",
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
            answer=bedrock_response.answer,
        )
        return api_response

    def _route(
            self,
            question: str,
            agent_response: AgentResponse | None = None,
            route_decision: RouteDecision | None = None
    ) -> RouteDecision:
        prompt = _build_confirm_prompt(question, agent_response, route_decision)
        query_result = self.query_to_llm(prompt)
        routed = _extract_markdown(query_result)
        return _json_to_route_decision(json.loads(routed))

    def retrieve_docs(self, question: str) -> BedrockResponse:
        query_emb = self.embed(question)
        search_list = self.repository.search_similar(query_emb)
        if not search_list:
            return BedrockResponse(
                answer="검색된 자료가 없습니다.",
                chunks=[]
            )

        if search_list[0].score < 0.55:
            response = BedrockResponse(
                answer='지금 가지고 있는 자료에서는 마땅한 데이터가 없네요.... 잘 모르겠어요....',
                chunks=[]
            )
            return response

        else:
            search_list = [item for item in search_list if item.score > 0.55]
            prompt = _build_retrieve_prompt(search_list, question)
            query_result = self.query_to_llm(prompt)
            response = BedrockResponse(answer=query_result, chunks=search_list)
            return response
