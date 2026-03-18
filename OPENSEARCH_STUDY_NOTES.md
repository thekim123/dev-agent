# OpenSearch Study Notes

## 이번 세션에서 정리된 핵심

### 1. 지금 만든 것은 agent라기보다 retrieval 시스템이다
- 현재 구조는 `rule-based router + OpenSearch retrieval + answer generation`에 가깝다.
- 아직 진짜 agent라고 부르려면 부족하다.
- 부족한 요소:
  - tool 선택
  - 다단계 실행
  - 중간 결과를 보고 다음 행동을 바꾸는 loop
  - 상태 관리

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
  - 라우팅
  - Source 매핑
  - answer 조합

## 현재 남은 개선 포인트
- `search_repo` 결과 path dedupe
- 코드 질문에서 문서(`.md`)를 얼마나 보여줄지 정책 정리
- retrieval threshold 튜닝
- FastAPI import 구조에서 eager dependency 정리
- 진짜 agent스럽게 가려면 tool-calling loop 도입

## 다음 단계
1. 테스트 정리 및 보강
2. 결과 품질 개선
3. retrieval assistant에서 mini agent로 확장
   - tool abstraction
   - tool result
   - 1~2 step loop
