from app.agent.service import AgentService
from app.llm.embedder import Embedder
from app.repository.opensearch_chunk_repository import OpenSearchChunkRepository

if __name__ == "__main__":
    host = "http://localhost:9200"
    index = "code_chunks_demo"
    repository = OpenSearchChunkRepository(host, index)
    embedder = Embedder()
    service = AgentService(
        repository=repository,
        embedder=embedder,
    )

    direct = service.answer(question="안녕 잘지내니?")
    print(direct)

    search_repo = service.answer(question="이 프로젝트에서 인증 로직은 어디에 있지?")
    print(search_repo)

    retrieve = service.answer(question="이 프로젝트에서 인증/인가 코드가 어떻게 되어 있는지 설명해줘.")
    print(retrieve)
