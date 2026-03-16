opensearch_chunk_repository.py는 이제 구현해도 됩니다. 다
  만 읽기 전용 repository adapter로만 채우세요.
  중요한 원칙은 하나입니다. [opensearch_test.py](D:\python-
  workspace\dev-agent\app\repository\opensearch_test.py)에서
  가져올 것은 query body 생성과 hit 파싱뿐입니다.
  build_index_body, build_bulk_body, assert_bulk_succeeded까
  지 옮기면 책임이 섞입니다.

  구현 순서

  1. [opensearch_chunk_repository.py](D:\python-
     workspace\dev-
     agent\app\repository\opensearch_chunk_repository.py) 맨
     위에 작은 헬퍼 3개만 두세요.

  def _build_knn_query(query_embedding: Sequence[float],
  top_k: int) -> dict: ...
  def _build_term_query(terms: list[str], top_k: int) ->
  dict: ...
  def _parse_hit(hit: dict) -> ChunkSearchHit: ...

  2. _parse_hit()는 반드시 ChunkSearchHit 하나만 반환하게 하
     세요.

  source = hit["_source"]
  return ChunkSearchHit(
      chunk_id=source["chunk_id"],
      source_path=source["source_path"],
      text=source["text"],
      start_offset=source["start"],
      end_offset=source["end"],
      score=float(hit["_score"]),
  )

  3. 클래스에는 아주 얇은 HTTP helper 하나만 두세요.

  def _request(self, method: str, path: str, json_body: dict
  | None = None) -> httpx.Response:
      with httpx.Client(base_url=self.host, timeout=5.0) as
  client:
          return client.request(method, path,
  json=json_body)

  OpenSearchClientManager 같은 건 만들지 마세요. 지금은 과설
  계입니다.

  4. __init__는 host 정리만 하세요.

  self.host = host.rstrip("/")
  self.index_name = index_name

  5. count()를 먼저 구현하세요.

  - GET /{index}/_count
  - 404면 0
  - 아니면 raise_for_status()
  - response.json()["count"] 반환

  6. search_similar()를 구현하세요.

  - POST /{index}/_search
  - body는 _build_knn_query(...)
  - 404면 []
  - 성공하면 payload["hits"]["hits"]를 _parse_hit()으로 변환
  - search_by_term()이 Source나 snippet을 만들면 안 됩니다.
    그건 service 책임입니다.

  메서드별 체크포인트

  - count()는 int
  - search_similar()는 list[ChunkSearchHit]
  - search_by_term()도 list[ChunkSearchHit]
  - OpenSearch 응답 _source.start, _source.end를 내부에서는
    start_offset, end_offset로 매핑
  - 404 정책은 일관되게:
      - count() -> 0
      - search_*() -> []

  하지 말 것

  - [opensearch_test.py](D:\python-workspace\dev-
    agent\app\repository\opensearch_test.py)를 import해서
    production 코드에서 쓰기
  - RepoSearchResult를 다시 살리기
  - repository에서 Source나 API DTO 만들기
  - base.py에 모델 다시 몰아넣기

  구현 후 검증

  1. scratch 스크립트로 인덱스 생성/적재
  2. repository 인스턴스로 직접 확인

  repo.count()
  repo.search_similar([1.0, 0.0], top_k=2)
  repo.search_by_term(["token", "refresh"], top_k=2)

  3. 기대값

  - count() == 3
  - search_similar(...)[0].chunk_id == "a"
  - search_by_term(...)[0].source_path == "app/auth/
    token_service.py"

  이 순서대로 직접 채우고 가져오세요. 그러면 다음엔 구현이
  맞는지 리뷰만 하겠습니다.
