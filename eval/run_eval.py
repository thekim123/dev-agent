import json
from collections.abc import Callable
from pathlib import Path
from typing import TypedDict

import yaml
from dotenv import load_dotenv

from app.llm.factory import create_embedder
from app.repository.base import ChunkRepository
from app.repository.factory import create_chunk_repository
from eval.eval_utils import normalize_path, first_relevant_rank, recall_at_k, reciprocal_rank, summarize_metrics

Retriever = Callable[[str, int], list[str]]


def create_baseline_retriever(embedder, repository: ChunkRepository) -> Retriever:
    """
      - 질문과 top_k를 받아 검색한다.
      - 결과에서 파일 경로 목록만 뽑아 list[str]로 반환한다.
      - 메트릭 계산은 절대 넣지 않는다.
    """

    def retriever(question: str, top_k: int) -> list[str]:
        embedding = embedder.embed(question)
        hits = repository.search_similar(query_embedding=embedding, top_k=top_k)
        return [hit.source_path for hit in hits]

    return retriever


class GoldenCase(TypedDict):
    id: str
    question: str
    answer_files: list[str]


def _validate_helper(index, item, seen_ids):
    if not isinstance(item, dict):
        raise ValueError(f"item at index {index}: top-level must be a dict")

    for key in ("id", "answer_files"):
        if key not in item:
            raise ValueError(f"item at index {index}: missing key - {key}")

    if not isinstance(item.get("answer_files"), list):
        raise ValueError(f"item at index {index}: answer_files must be a list")

    if len(item.get("answer_files")) == 0:
        raise ValueError(f"item at index {index}: answer_files must not be empty")

    if item["id"] in seen_ids:
        raise ValueError(f"items have duplicate id: {item['id']}")


def load_golden_set(path: Path) -> list[GoldenCase]:
    """
    YAML 골든셋을 읽어 검증된 케이스 리스트를 반환.
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("top-level must be a list")

    seen_ids: set[str] = set()
    for i, item in enumerate(data):
        _validate_helper(i, item, seen_ids)
        seen_ids.add(item["id"])
    return data


# 한 문제 평가 함수
def evaluate_one_case(case: GoldenCase, retriever: Retriever, top_k: int) -> dict:
    """
      - case["question"] 꺼낸다.
      - case["answer_files"]를 정규화한다.
      - retriever(question, top_k)를 호출한다.
      - 실제 결과 경로도 정규화한다.
      - first_relevant_rank()를 구한다.
      - hit, recall, rr를 계산한다.
      - 디버깅 가능한 row 하나를 반환한다.
    """
    question = case["question"]
    expected = {normalize_path(p) for p in case["answer_files"]}
    case_id = case["id"]
    actual = []
    seen = set()
    for p in retriever(question, top_k):
        np = normalize_path(p)
        if np not in seen:
            seen.add(np)
            actual.append(np)
    rank = first_relevant_rank(expected, actual)

    return {
        "id": case_id,
        "question": question,
        "expected_paths": sorted(expected),
        "actual_paths": actual,
        "hit": rank is not None,
        "first_relevant_rank": rank,
        "recall_at_k": recall_at_k(expected=expected, ranked_actual=actual, k=top_k),
        "reciprocal_rank": reciprocal_rank(rank),
    }


# 전체 평가 함수
def evaluate_all(cases: list[GoldenCase], retriever: Retriever, top_k: int) -> tuple[list[dict], dict]:
    """
    1. cases를 돌면서 evaluate_one_case를 호출 -> rows 수집
    2. summarize_metrics(rows) -> summary 생성
    3. (rows, summary) 반환
    """
    if len(cases) == 0:
        raise ValueError("cases must not be empty")
    rows = [evaluate_one_case(case, retriever, top_k) for case in cases]
    summary = summarize_metrics(rows)
    # test_case = cases[0]
    # raw_actual = retriever(test_case["question"], 5)
    # print("expected raw:", test_case["answer_files"])
    # print("actual raw:", raw_actual)
    # print("expected normalized:", [normalize_path(p) for p in test_case["answer_files"]])
    # print("actual normalized:", [normalize_path(p) for p in raw_actual])
    return rows, summary


def main():
    embedder = create_embedder()
    repository = create_chunk_repository()
    retriever = create_baseline_retriever(repository=repository, embedder=embedder)

    path = Path('./golden_draft.yaml')
    cases = load_golden_set(path)
    rows, summary = evaluate_all(cases, retriever, top_k=5)

    # 콘솔 출력
    for row in rows:
        mark = "HIT" if row["hit"] else "MISS"
        print(f"[{mark}] {row['id']} — {row['question'][:40]}")
        print(f"       recall@k={row['recall_at_k']:.2f}  rr={row['reciprocal_rank']:.2f}")
    print("---")
    print(f"mean_recall@k = {summary['mean_recall_at_k']:.3f}")
    print(f"MRR           = {summary['mrr']:.3f}")
    print(f"total: {len(rows)} cases")

    # JSON 저장
    output = {"rows": rows, "summary": summary}
    out_path = Path('./eval_result.json')
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nresult saved to {out_path}")


if __name__ == "__main__":
    load_dotenv()
    main()
