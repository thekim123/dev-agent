# dev-agent

코드/문서 검색 기반 에이전트 프로젝트입니다.

질문을 받아 다음 두 경로 중 하나로 처리합니다.

- `search_repo`: 코드 위치/파일 탐색
- `retrieve_docs`: 임베딩 기반 문서 검색 후 답변
  생성

OpenSearch를 사용하는 경우, 문서 chunk를 벡터 인
덱스로 적재한 뒤 조회합니다.

## 주요 구성

- `app/agent`
    - 질문 라우팅과 응답 생성
- `app/repository`
    - 검색용 read-side adapter
    - `JsonChunkRepository`,
      `OpenSearchChunkRepository`
- `app/ingestion`
    - chunk 생성과 OpenSearch 적재
    - `OpenSearchIndexer`
- `app/llm`
    - 임베딩 생성과 답변 생성

## 아키텍처 요약

이 프로젝트는 read/write 책임을 분리합니다.

- `ChunkRepository`
    - 조회 전용 포트
    - `count`, `search_by_term`, `search_similar`
- `OpenSearchIndexer`
    - 적재 전용 write-side adapter
    - 인덱스 생성, bulk insert 담당

즉 OpenSearch 적재와 조회를 같은 repository 책임
으로 섞지 않습니다.

## 환경 변수

`.env` 또는 OS 환경변수로 아래 값을 설정합니다.

- `CHUNK_REPOSITORY_BACKEND`
    - `json` 또는 `opensearch`
- `OPENSEARCH_HOST`
    - 예: `http://localhost:9200`
- `OPENSEARCH_INDEX`
    - 예: `code_chunks_demo`
- `BEDROCK_EMBEDDING_MODEL_ID`
- `BEDROCK_QUERY_MODEL_ID`

AWS 인증 정보는 표준 AWS 환경변수/프로파일 방식을
사용합니다.

## 실행

### FastAPI 실행

```bash
uvicorn app.main:app --reload
```

### API 호출

POST /agent

예시 요청:

```
{
  "question": "refresh token 코드는 어디에 있어?"
}
```

예시 응답:

```
  - used_tool
  - reason
  - sources
  - answer
```

## OpenSearch 적재

OpenSearch를 사용할 경우, 먼저 chunk 데이터를 인
덱스에 적재해야 합니다.

권장 흐름:

1. 문서 chunk 생성
2. embedding 생성
3. OpenSearch 인덱스 생성
4. bulk insert
5. repository 조회 검증

vector_store.json이 있으면 이를 seed 데이터로 사
용해 적재/조회 검증을 먼저 할 수 있습니다.

## 개발 순서

권장 개발 순서는 아래와 같습니다.

1. ingestion/indexer 검증
2. repository 조회 검증
3. service 연결
4. API 확인
5. 테스트 추가
6. 검색 품질 개선

## 테스트

우선순위는 아래와 같습니다.

- service 테스트
- repository 통합 테스트
- API 테스트

## 주의사항

- Source.line 같은 실제로 보장하지 않는 필드는
  API에 노출하지 않습니다.
- OpenSearch mapping은 dynamic: "strict"를 사용하
  므로, 적재 문서 shape와 mapping은 반드시 일치해
  야 합니다.
- .env 로딩은 앱 시작 시 한 번만 명시적으로 처리
  해야 합니다.

## 현재 상태

현재 구현 범위:

- OpenSearch indexer 추가
- OpenSearch repository 조회 구현
- AgentService 연결
- service 단위 수동 검증 완료

남은 작업:

- 테스트 추가
- 결과 dedupe
- 라우팅/threshold 튜닝
- 검색 품질 개선