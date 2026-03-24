# LEVEL

## 2026-03-24 평가 업데이트

### 테스트 설계 감각 변화

- 컨트롤러와 서비스의 테스트 책임이 다르다는 것을 스스로 판단했다.
  - "컨트롤러는 서비스를 호출할 뿐이고, 멀티루프를 돌든 말든 그건 서비스 책임"이라는 결론을 직접 도출했다.
- fake에서 하드코딩한 값이 그대로 나오는 것을 검증하는 건 무의미하다는 것을 인식했다.
  - "LLM이 결정하는 값을 테스트에서 고정해놓고 그걸 assert하는 건 앱의 책임을 검증하는 게 아니다"
- `call_count`로 루프가 의도한 횟수만큼 돌았는지 검증해야 한다는 판단을 할 수 있게 되었다.

### Python 감각 변화

- Java식 getter 대신 Python은 필드 직접 접근이 관례라는 점을 이해했다.
  - `@property`로 나중에 투명하게 전환 가능하므로 미리 getter를 만들 필요가 없다 (YAGNI).
- 리스트 `*` 연산자로 반복 패턴을 생성하는 방법을 배웠다 (`[a, b] * N`).

### 남은 교육 포인트

- LangChain/LangGraph 같은 프레임워크의 내부 구조와 지금 만든 것의 대응 관계 이해
- retrieval threshold 튜닝과 검색 품질 판단 감각
- FastAPI import 구조에서 eager dependency 문제 이해

## 2026-03-22 평가 업데이트

### Python 수준 변화

- `str`이 immutable이라는 점, 변수 재바인딩과 객체 변경의 차이를 이해했다.
- `json.dumps`의 결과가 `str`이라는 점을 활용해 테스트 비교값을 구성할 수 있게 되었다.
- 죽은 코드(주석, 미사용 상수/함수/import)를 식별하고 정리하는 작업을 직접 수행했다.
- `print` 디버그 코드를 제거해야 한다는 점을 인식하고 있다.

### 테스트 감각 변화

- fake 객체가 여러 호출 시점에 다른 값을 반환해야 하는 상황을 직접 경험했다.
- prompt 내용 기반 분기로 fake를 구성하는 방법을 스스로 선택했다.
- 테스트에서 비교 대상의 타입이 일치해야 한다는 점을 체감했다 (dict vs str).
- `LLMClient` 테스트의 관심사를 "str 반환 여부"로 한정하는 판단을 할 수 있게 되었다.

### 설계 감각 변화

- 함수의 책임 범위를 질문할 수 있게 되었다 (`_extract_markdown`이 `LLMClient`에 있어야 하는가).
- LLM 응답의 마크다운 감싸기 문제를 이해하고, 후처리 위치를 호출 쪽으로 판단했다.
- private 메서드(`_route`)를 직접 테스트하는 대신 public 메서드(`answer`)를 통해 간접 검증하는 방식을 이해했다.

### agent loop 설계 감각 변화

- 1회 호출 구조에서 `while True` + `is_final` 기반 루프 구조로 직접 전환했다.
- "도구 실행 결과를 LLM이 판단해서 다음 행동을 결정한다"는 agent 핵심 흐름을 구현했다.
- 첫 호출과 이후 호출을 하나의 프롬프트 함수로 통합하는 판단을 스스로 했다 (`agent_response: None` 분기).
- "모델을 분리해야 하나?"에서 출발해서 "필드가 같으면 합치는 게 낫다"는 결론을 직접 도출했다.
- confirm 프롬프트에 "뭘 해달라는 건지" 지시가 빠져있다는 피드백을 받고 수정했다.
- `is_final` 판단 주체가 두 곳(`RouteDecision`, `AgentResponse`)에 있는 문제를 인식하고 `RouteDecision`으로 통일했다.
- confirm에서 이전 결과가 버려지는 버그를 발견하고, `agent_response is not None` 체크로 해결했다.
- `for range(MAX_ITERATIONS)`로 무한루프 방지를 직접 구현했다.
- fake가 의도와 다르게 MAX_ITERATIONS까지 루프를 돌고 우연히 통과하는 케이스를 경험했다.

### 테스트 감각 변화 (추가)

- 구조 변경 시 fake도 함께 갱신해야 한다는 것을 체감했다 (`is_final` 필드 누락, confirm 분기 누락).
- 테스트가 통과해도 "왜 통과하는지"를 추적해야 한다는 감각이 생겼다 (우연히 통과 vs 의도대로 통과).
- fake에 호출 횟수 추적을 넣으면 루프 관련 버그를 잡을 수 있다는 점을 인지했다.

### 남은 교육 포인트 (3/22 기준)

- fake 구조에서 불필요한 래핑 (`[{"text": ...}][0]["text"]`) 을 단순화하는 습관
- ~~멀티스텝 시나리오 (루프 2회 이상) 테스트 작성~~ → 3/24 완료
- LangChain/LangGraph 같은 프레임워크의 내부 구조와 지금 만든 것의 대응 관계 이해

## 2026-03-18 평가 업데이트

### Python 수준 변화

- Python에서 데이터 계약을 계층별로 나누는 감각이 생겼다.
    - ingestion model
    - repository read model
    - API DTO
- `ChunkSearchHit -> Source` 같은 변환을 service 경계에 두는 판단을 이해했다.
- context manager, `close()`, `Path(__file__)`, `.env` 로딩 시점 같은 Python 운영 감각이 올라왔다.
- 다만 `import`를 선언이 아니라 모듈 실행으로 보는 감각은 아직 약하다.
    - Java의 class import 감각으로 top-level import를 가볍게 보고 있다.
    - Python에서는 import가 런타임 의존성 전파와 테스트 격리에 직접 영향을 준다는 점을 현재 학습 중이다.
- 의존성 주입을 클래스 이름이 아니라 행동 단위로 재구성하려는 질문이 나오기 시작했다.
    - `Embedder` 구현 객체를 받을지보다 `embed`, `query_embed` 같은 callables를 직접 주입할 수 있는지 묻고 있다.
    - 이는 Java식 구현 클래스 중심 사고에서 Python식 행동 중심 사고로 이동하는 중요한 신호다.
- FastAPI dependency override를 "인자 주입 함수"가 아니라 "인자 없는 테스트용 provider"로 이해하고 closure로 수정했다.
    - 함수 시그니처 자체가 DI 계약이라는 점을 실제 테스트 실패를 통해 학습했다.
    - Python/FastAPI에서 lexical scope와 closure를 테스트 격리에 활용하는 감각이 올라왔다.
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
