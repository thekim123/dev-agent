 네. 여기는 얇은 클래스 하나는 만드는 게 맞습니다.
  하지만 Java식으로 크게 만들면 안 됩니다.

  기준은 이겁니다.

  - host
  - index_name
  - dimension
  - HTTP 요청 방식

  이런 지속되는 상태가 있으면 클래스가 맞습니다.
  반대로 상태 없이 입력만 받아서 JSON 만드는 건 클래스에 넣지
  마세요.

  즉 구조는 이렇게 가야 합니다.

  1. 클래스가 가져야 하는 것

  - OpenSearchIndexer
  - 역할: OpenSearch 쓰기 어댑터
  - 내부 상태:
      - host
      - index_name
      - dimension

  2. 클래스 안에 있어야 하는 메서드

  - create_index()
  - bulk_insert(...)
  - count_docs()
  - 필요하면 index_chunks(...)
  - _request(...)

  3. 클래스 밖에 있어야 하는 것

  - build_index_body(...)
  - build_bulk_body(...)
  - assert_bulk_succeeded(...)

  왜냐하면 이 셋은 상태를 가진 객체 동작이 아니라 입력을 출력으
  로 바꾸는 순수 함수에 가깝기 때문입니다.

  여기서 Java 습관을 바로 잡아야 합니다.
  이 상황에서 나쁜 방식은 이런 겁니다.

  - OpenSearchIndexBodyBuilder
  - IndexCreationService

  이건 전부 과설계입니다. 파이썬에서는 이렇게 안 갑니 다.

  가장 Python다운 기준은 이겁니다.

  즉 답만 짧게 말하면:

  네, indexer는 클래스 하나 두는 게 맞다. 하지만 body builder까
  지 클래스에 넣지 말고, I/O 메서드만 가진 얇은 어댑터 클래스여
  야 한다.

  네가 지금 만들면 되는 형태를 체크리스트로 적으면 이 겁니다.

  - app/ingestion/opensearch_indexer.py
  - class OpenSearchIndexer
  - 모듈 함수 3개:
      - build_index_body
      - build_bulk_body
      - assert_bulk_succeeded
  - 클래스 메서드 4개:
      - create_index
      - bulk_insert
      - count_docs
      - index_chunks

  원하면 다음엔
  이 7개 중 각각의 입력/출력 계약을 어떻게 잡아야 하는