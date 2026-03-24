# dev-agent

코드/문서 검색 기반 멀티스텝 에이전트 프로젝트입니다.

질문을 받으면 LLM이 도구를 선택하고, 결과를 평가해 필요하면 다른 도구를 다시 호출하는 루프를 돕니다(최대 10회).

사용 가능한 도구:

- `search_repo` — 키워드 기반 코드 위치/파일 탐색
- `retrieve_docs` — 임베딩(cosine similarity) 기반 문서 검색 후 답변 생성
- `direct` — 프로젝트와 무관한 일반 질문에 LLM이 직접 답변

## 주요 구성

- `app/agent`
    - 질문 라우팅(멀티스텝 루프)과 응답 생성
    - `AgentService`, `RouteDecision`
- `app/repository`
    - 검색용 read-side adapter
    - `JsonChunkRepository` — 로컬 JSON + cosine similarity 검색
    - `OpenSearchChunkRepository` — OpenSearch kNN 검색
- `app/ingestion`
    - chunk 생성과 OpenSearch 적재
    - `OpenSearchIndexer`
- `app/llm`
    - `Embedder` — Amazon Bedrock 임베딩
    - `LLMClient` — Amazon Bedrock 답변 생성

## 아키텍처 요약

이 프로젝트는 read/write 책임을 분리합니다.

- `ChunkRepository` (추상 포트)
    - 조회 전용: `count`, `search_by_term`, `search_similar`
- `OpenSearchIndexer`
    - 적재 전용 write-side adapter
    - 인덱스 생성, bulk insert 담당

검색 품질 관리: `retrieve_docs`는 cosine similarity 기반이며, score < 0.55인 결과는 필터링됩니다.

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

### 표준 명령

- 이 프로젝트의 모든 실행/테스트 명령은 .venv\Scripts\python.exe 기준으로 실행한다.
- bare python, bare pytest는 사용하지 않는다.
- 패키지 설치도 같은 인터프리터로 수행한다.

```shell
  .\.venv\Scripts\python.exe -m pytest
  .\.venv\Scripts\python.exe -m pip install -r requirement.txt
```

### FastAPI 실행

```bash
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
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

```json
{
  "used_tool": "retrieve_docs",
  "reason": "문서 임베딩 검색 기반",
  "sources": [
    {
      "path": "src/auth/TokenService.java",
      "snippet": "public String refreshToken(String oldToken) ...",
      "score": 0.82
    }
  ],
  "answer": "refresh token 관련 로직은 TokenService에 있습니다."
}
```
