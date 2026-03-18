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
