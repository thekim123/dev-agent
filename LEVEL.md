# LEVEL

## 2026-03-18 평가 업데이트

### Python 수준 변화

- Python에서 데이터 계약을 계층별로 나누는 감각이 생겼다.
    - ingestion model
    - repository read model
    - API DTO
- `ChunkSearchHit -> Source` 같은 변환을 service 경계에 두는 판단을 이해했다.
- context manager, `close()`, `Path(__file__)`, `.env` 로딩 시점 같은 Python 운영 감각이 올라왔다.
- 다만 테스트를 더 강하게 쓰는 습관과 죽은 import/주석을 즉시 정리하는 습관은 보강이 더 필요하다.

### 검색 / OpenSearch / RAG 수준 변화

- Dev Tools 실험 수준을 넘어서 Python 코드로 적재/조회 파이프라인을 직접 만들었다.
- `OpenSearchIndexer`와 `OpenSearchChunkRepository`를 분리해서 write/read 책임을 나눴다.
- `strict dynamic mapping`, NDJSON bulk, `_score` vs `_source`, `Source` DTO 정리까지 경험했다.
- 실제 `vector_store.json`을 읽어 OpenSearch에 적재하고, repository와 service/API 경로까지 확인했다.

### HTTP / API 설계 감각 변화

- `PUT`, `POST`, 멱등성, 상태 전이, upsert의 차이를 개념적으로 이해하기 시작했다.
- CRUD를 HTTP 메서드에 기계적으로 매핑하는 관점에서 한 단계 벗어났다.
- 생성/수정/행위 실행을 구분해서 보려는 감각이 생겼다.

### 현재 강점

- 단순 구현보다 계약과 책임을 먼저 보려는 태도가 생겼다.
- Java식 `toDto`, 과설계, service 남발을 경계해야 한다는 점을 이해했다.
- 검색 시스템을 만들 때 schema, response contract, DTO naming이 중요하다는 점을 경험으로 배웠다.

### 남은 교육 포인트

- retrieval assistant와 진짜 agent의 차이를 구조적으로 구현해보기
- 테스트를 `used_tool` 수준에서 끝내지 않고 응답 계약과 품질까지 검증하기
- API 문서와 설정 로딩 구조를 제품 수준으로 정리하기
- 작은 함수와 명시적 변환으로 끝낼 수 있는 문제를 다시 큰 구조로 키우지 않기

### 현재 단계에서 적절한 다음 과제

- service/API 테스트 보강
- search 결과 dedupe 및 품질 튜닝
- tool abstraction을 도입한 mini agent loop 설계

## 2026-03-16 현재 평가

### 배경

- Java 백엔드 경험이 있다.
- 아키텍처, 계층 분리, 인터페이스 같은 개념 자체는 낯설지 않다.
- 언어 선택을 기술 신앙이 아니라 트레이드오프로 보는 감각이 있다.

### Python 수준

- Python 문법 기초는 따라갈 수 있지만, 아직 Python의 데이터 모델과 표현식 의미가 몸에 붙지는 않았다.
- 특히 아래에서 막힌다.
    - `{...}`가 block이 아니라 `dict` 또는 `set`이라는 점
    - tuple 반환을 계약으로 써도 되는지에 대한 감각
    - 디버그용 출력과 실제 함수 책임을 분리하는 습관
    - ingestion 모델과 retrieval 모델을 분리해야 한다는 감각

### 검색 / OpenSearch / RAG 수준

- Dev Tools에서 하던 OpenSearch 요청을 Python 코드로 옮길 수 있다.
- `knn_vector`, `_bulk`, `_search`, `match`, `boost`, relevance scoring의 큰 방향은 이해하기 시작했다.
- `score += ...` 방식의 수동 점수 계산과 OpenSearch의 relevance scoring이 개념적으로 대응된다는 점을 이해했다.
- 아직 부족한 부분은 아래와 같다.
    - 검색 결과 타입 계약을 어떻게 설계해야 하는지
    - 검색 엔진 응답 JSON과 서비스 내부 DTO를 어떻게 분리해야 하는지
    - `line`과 `offset`처럼 용어를 정확히 써야 한다는 점

### 강점

- 개념이 연결되면 빠르게 받아들인다.
- 단순히 “된다/안 된다”보다 “왜 이런 구조여야 하는가”를 묻는다.
- 검색, RAG, 언어 선택을 기술 마케팅이 아니라 구조와 트레이드오프로 보려는 태도가 있다.

### 자주 나오는 위험 신호

- Java식으로 계약/계층을 크게 재설계하려는 방향으로 먼저 생각할 수 있다.
- Python에서 작은 함수로 끝낼 수 있는 문제를 인터페이스/서비스 구조로 먼저 끌고 갈 위험이 있다.
- 반대로 임시 스크립트 단계에서는 `dict`, `print`, tuple 같은 임시 구조가 남아 계약까지 새어 나갈 수 있다.

### 현재 교육 방향

- 정답 구현을 대신 제공하지 않는다.
- 체크리스트와 검토 기준을 먼저 준다.
- Python에서는 작은 순수 함수와 명시적 dataclass를 우선하도록 계속 교정한다.
- Java식 추상화 습관은 명시적으로 지적한다.
- “작동함”보다 “계약이 맞는가”, “책임이 맞는가”, “용어가 정확한가”를 우선시한다.

### 지금 단계에서 적절한 과제 난이도

- OpenSearch 요청 body를 직접 작성하고 응답 JSON을 직접 해석하는 작업
- 실험용 스크립트에서 repository 계층으로 옮기기 전, 반환 타입을 재설계하는 작업
- JSON 기반 검색 구현과 OpenSearch 기반 검색 구현을 같은 인터페이스 뒤에 맞추는 작업

### 아직 이르다

- 프레임워크 중심의 RAG 추상화 도입
- 과도한 class 분리
- 결과 타입을 충분히 정리하지 않은 상태에서 서비스 계층 확장
