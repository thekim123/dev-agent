• 네 판단이 맞습니다. base.py:22의 반환 구조는 좋지 않습니다.
  정확히 말하면 parse_*를 억지로 현재 계약에 맞추는 것보다, 계약 자체
  를 다시 잡는 게 맞습니다.

  문제는 세 가지입니다.

  1. tuple[float, DocumentChunk]는 의미가 숨겨집니다.
      - 0이 점수인지, 1이 chunk인지 매번 기억해야 합니다.
      - 이런 건 로컬 헬퍼에나 잠깐 쓰는 형태지, 계층 간 계약으로 쓰면
        안 됩니다.
  2. DocumentChunk가 검색 결과 타입으로 새고 있습니다.
      - chunker.py:4의 DocumentChunk는 원래 적재용 데이터입니다.
      - 여기엔 embedding이 들어 있습니다.
      - 그런데 검색 결과에서 embedding은 필요 없습니다.
      - 즉 쓰기 모델과 읽기 모델이 섞였습니다.
  3. line이라는 이름이 틀렸습니다.
      - chunker.py:13 기준 start, end는 라인 번호가 아니라 문자 오프
        셋입니다.
      - 그런데 base.py:10과 dto.py:14는 이걸 line으로 부릅니다.
      - 이건 용어가 잘못된 겁니다. 지금 바로 잡아야 합니다.

  내 권장은 이겁니다. search_similar()는 이런 타입을 반환해야 합니다.

  from dataclasses import dataclass

  @dataclass(frozen=True)
  class ChunkSearchHit:
      chunk_id: str
      source_path: str
      text: str
      start_offset: int
      end_offset: int
      score: float

  그리고 base.py는 이렇게 가는 게 맞습니다.

  class ChunkRepository(ABC):
      @abstractmethod
      def search_similar(
          self,
          query_embedding: Sequence[float],
          top_k: int = 3,
      ) -> list[ChunkSearchHit]:
          ...

      @abstractmethod
      def search_by_term(
          self,
          terms: list[str],
          top_k: int = 5,
      ) -> list[ChunkSearchHit]:
          ...

  왜 search_by_term()도 같은 타입이냐면, 지금 저장소는 결국 “chunk를
  검색”하고 있기 때문입니다.
  현재의 RepoSearchResult는 사실 저장소의 본질적인 데이터가 아니라,
  서비스/UI용 projection입니다. 특히 snippet=chunk.text[:120] 같은 건
  repository 책임이 아닙니다. 그건 서비스 계층에서 만들어야 합니다.

  즉 정리하면:

  - repository는 chunk hit를 반환
  - service는 그걸 Source나 답변용 snippet으로 변환
  - API는 마지막 표현만 담당

  이게 더 파이썬답고, 더 정확합니다. Java식으로 ResultFactory,
  AbstractSearchResult 같은 계층을 추가하라는 뜻이 아닙니다.
  반환 타입 하나를 명확하게 만들고, 그걸 끝까지 일관되게 쓰라는 뜻입
  니다.

  추가로, 이 작업할 때 같이 고쳐야 할 것:

  - dto.py:25의 BedrockResponse.chunks
      - List[Tuple[float, DocumentChunk]]도 같이 버려야 합니다.
  - service.py:170
      - search_list[0][0], doc[1].text 같은 위치 접근도 없어져야 합니
        다.
  - opensearch_chunk_repository.py:15
      - search_by_terms 이름도 base.py:30의 search_by_term과 맞춰야
        합니다.

  결론은 명확합니다.
  네, 프로토콜을 재정립하는 게 맞고, 특히 tuple 반환은 버려야 합니다.
  그리고 그 재정립의 기준은 “검색 결과를 명시적 dataclass로 만든다”입
  니다.

  원하면 다음 답변에서 제가 base.py, dto.py, service.py를 어떻게 바꿔
  야 하는지 변경 순서만 딱 5단계로 잡아드리겠습니다