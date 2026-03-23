# OpenSearch Study Notes

## 2026-03-19 완료한 작업
- [x] `test/test_service.py` 깨진 assert 수정 (`==` + `in` 연산자 우선순위 문제)
- [x] `test/agent_test.py`에서 `print()` 제거
- [x] API 테스트에 계약 검증 추가 (`used_tool`, `answer`, 응답 키)
- [x] `search_repo` / `retrieve_docs` / `direct` 케이스 분리
- [x] 검색 결과 없음 케이스 추가
- [x] `FakeEmbedder` 중복 제거 → `conftest.py`로 통합
- [x] `FakeRepository`에 `hits` 주입 가능하게 개선
- [x] `search_repo` path dedupe 구현 + 테스트

## 2026-03-22 완료한 작업
- [x] LLM 라우팅 전환 후 레거시 코드 정리 (주석 코드, 안 쓰는 상수/함수 제거)
- [x] `LLMClient`에서 `_extract_markdown`, `print` 제거, 미사용 import 정리
- [x] `FakeLLMClient`를 LLM 라우팅에 맞게 수정 (prompt 내용 기반 분기)
- [x] `LLMClient` 테스트: 반환값 비교 방식 개선 (json.dumps된 변수 사용)
- [x] LLM 응답의 마크다운 코드블록 문제 이해 (```json 감싸기)
- [x] `_extract_markdown` 책임 위치 판단 → `LLMClient`가 아닌 호출 쪽(`service.py`)에서 처리
- [x] `str` 불변성과 재바인딩 개념 확인
- [x] agent loop 구조 설계 및 구현 (`while True` + `is_final` 탈출)
- [x] `_build_route_prompt`와 confirm 프롬프트를 `_build_confirm_prompt`로 통합 (`agent_response: None` 분기)
- [x] `RouteDecision`에 `is_final` 추가, `AgentResponse`에 `is_final` 추가
- [x] `_json_to_route_decision` 파싱 함수 분리
- [x] 미사용 import (`typing_inspection`) 제거
- [x] 미사용 모델 (`ConfirmationResponse`) 정리
- [x] `AgentResponse`에서 `is_final` 제거 → 루프 탈출은 `RouteDecision.is_final`로 통일
- [x] `answer` 루프에서 confirm과 첫 라우팅 구분 (`agent_response is not None` 체크)
- [x] `for range(MAX_ITERATIONS)` 무한루프 방지
- [x] `FakeLLMClient`에 `is_final` 필드 추가 + confirm 분기(`'원래 질문은'`) 추가
- [x] confirm에서 `tool: 'direct'` 반환 시 이전 결과가 버려지는 버그 수정

## 지금 해야 할 일

### 다음 과제
- 루프가 2번 이상 도는 멀티스텝 테스트 작성
- retrieval threshold (`score < 0.4`) 조정 및 검색 결과 품질 확인
- FastAPI import 구조에서 eager dependency 정리

## 나중에 할 일
- retrieval threshold 조정
- `.md` 문서 노출 정책 결정
- FastAPI import 구조에서 eager dependency 정리

## 이번 세션에서 정리된 핵심

### 1. agent loop의 핵심 구조
- `_route → execute_tools → confirm → (반복 or 종료)` 사이클
- 첫 호출과 이후 호출을 하나의 프롬프트 함수로 통합할 수 있다 (`agent_response`가 `None`이면 첫 호출)
- `is_final`은 LLM이 판단한다 (도구가 하드코딩하는 게 아님)
- 역할이 다른 데이터는 모델을 분리해야 한다 — 그런데 결과적으로 같은 필드가 필요하면 하나로 합치는 게 맞을 수도 있다 (`RouteDecision` + `is_final`)

### 2. OpenSearch 적재와 조회는 책임을 분리해야 한다
- `ChunkRepository`는 조회 전용 read port다.
- 삽입/인덱싱은 repository에 억지로 넣지 않는다.
- write-side는 `OpenSearchIndexer`로 분리한다.

### 3. OpenSearchIndexer 구조
- 얇은 adapter 클래스 하나는 허용된다.
- 단, Java식 과설계는 금지한다.
- 클래스 안:
  - `create_index`
  - `bulk_insert`
  - `close`
  - `__enter__`, `__exit__`
- 클래스 밖:
  - `build_index_body`
  - `build_bulk_body`
  - `assert_bulk_succeeded`

### 4. Bulk API는 일반 JSON이 아니라 NDJSON이다
- 문서 하나당 2줄이 필요하다.
  - action line
  - document line
- `content-type`은 `application/x-ndjson`
- `json=`가 아니라 `content=`로 보낸다.

### 5. strict mapping은 귀찮은 게 아니라 보호 장치다
- `dynamic: "strict"`는 schema mismatch를 빨리 잡아준다.
- 필드명을 바꿨으면 기존 index를 재생성해야 한다.
- 코드만 바꾸고 OpenSearch에 이미 존재하는 index를 그대로 쓰면 안 된다.

### 6. `_score`와 `_source`를 구분해야 한다
- 점수는 `hit["_score"]`
- 문서 필드는 `hit["_source"]`
- `_source["score"]`처럼 읽으면 틀리다.

### 7. read model과 API DTO는 분리해야 한다
- repository는 `ChunkSearchHit`를 반환한다.
- service는 `ChunkSearchHit -> Source` 변환만 담당한다.
- `ChunkSearchHit.toSource()`처럼 아래 계층 모델이 위 계층 DTO를 알게 하면 안 된다.

### 8. `line`은 제거한 판단이 맞다
- 현재 데이터는 line number가 아니라 offset이다.
- 없는 정보를 API에 거짓으로 노출하면 안 된다.
- `Source`에는 지금 `path`, `snippet`, `score`만 두는 것이 정직하다.

### 9. `.env` 로딩은 한 번만, 앱 시작점에서 해야 한다
- `load_dotenv()`를 `Embedder` 안에 두면 안 된다.
- repository factory가 먼저 실행되면 env가 로드되기 전에 `os.getenv()`를 읽게 된다.
- 설정 로딩은 진입점 또는 config 모듈에서 한 번만 처리해야 한다.

### 10. 테스트 우선순위
- 먼저 service 테스트
- 그 다음 API 테스트
- 마지막으로 OpenSearch 통합 테스트
- 테스트에서는 흐름만 보지 말고 응답 계약도 같이 검증해야 한다.
  - `used_tool`
  - `sources`
  - `answer`

## 현재 구조 요약
- `app/ingestion`
  - chunk 생성
  - OpenSearch 적재
- `app/repository`
  - OpenSearch 조회
- `app/agent`
  - 라우팅 + confirm (agent loop)
  - tool 실행 (`execute_tools`)
  - Source 매핑
  - answer 조합

## 교훈
- Python에서 `in`, `==`, `is`, `not in` 같은 비교 연산자는 chaining된다. 괄호로 의도를 명확히 해야 한다.
- `if not []`는 `True`다. 빈 리스트는 falsy.
- 테스트용 fake 객체는 데이터를 주입받게 만들면 케이스마다 재사용할 수 있다.
- YAGNI: 지금 안 쓰이면 옮기지 않는다.
- 모델을 분리할지 합칠지는 "역할이 다른가?"로 시작하되, 필드가 동일하면 합치는 게 나을 수 있다.
- 함수 파라미터에 `None` 기본값을 주면 첫 호출/이후 호출을 하나의 함수로 처리할 수 있다.
- 테스트가 통과해도 "의도대로 통과"인지 확인해야 한다 — fake가 MAX_ITERATIONS까지 루프를 돌고 빠져나오는 식으로 우연히 통과할 수 있다.
- fake에 호출 횟수 추적을 넣으면 이런 류의 버그를 잡을 수 있다.
- `is_final` 같은 판단 주체는 한 곳으로 통일해야 한다 — 도구가 정하는 것과 LLM이 정하는 것이 섞이면 혼란.
