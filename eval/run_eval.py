from collections.abc import Callable
from pathlib import Path
from typing import TypedDict

import yaml

from eval.eval_utils import normalize_path, first_relevant_rank, recall_at_k, reciprocal_rank

Retriever = Callable[[str, int], list[str]]


class GoldenCase(TypedDict):
    id: str
    question: str
    answer_files: list[str]


def load_golden_set(path: Path) -> list[GoldenCase]:
    """
    YAML 골든셋을 읽어 검증된 케이스 리스트를 반환.

    계약:
    - 파일 없음 → FileNotFoundError (전파)
    - YAML 파싱 실패 → yaml.YAMLError (전파)
    - 최상위가 list가 아님 → ValueError
    - 원소가 dict가 아님 → ValueError (인덱스 포함 메시지)
    - id/question/answer_files 키 누락 → ValueError (인덱스 포함)
    - answer_files가 list[str]이 아니거나 비어있음 → ValueError
    - id 중복 → ValueError (중복된 id 포함 메시지)
    - 빈 리스트([])는 허용 — "비었다"의 의미 해석은 호출측 책임
    """
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("top-level must be a list")
    return data


# 검색 함수
def baseline_retriever(question: str, top_k: int) -> list[str]:
    """
      - 질문과 top_k를 받아 검색한다.
      - 결과에서 파일 경로 목록만 뽑아 list[str]로 반환한다.
      - 메트릭 계산은 절대 넣지 않는다.
    """
    ...


# 한 문제 평가 함수
def evaluate_one_case(case: dict, retriever: Retriever, top_k: int) -> dict:
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
    actual = [normalize_path(p) for p in retriever(question, top_k)]
    rank = first_relevant_rank(expected, actual)
    case_id = case["id"]

    return {
        "id": case_id,
        "question": question,
        "expected_paths": sorted(expected),
        "actual_paths": actual,
        "hit": rank is not None,
        "first_relevant_rank": rank,
        "recall_at_k": recall_at_k(expected=expected, actual_ranked=actual, k=top_k),
        "reciprocal_rank": reciprocal_rank(rank),
    }


# 전체 평가 함수
def evaluate_all(cases: list[dict], retriever: Retriever, top_k: int) -> tuple[list[dict], dict]:
    ...


def main():
    cases = load_golden_set(...)
    rows, summary = evaluate_all(cases, baseline_retriever, top_k=5)
