def normalize_path(path: str, anchor: str = 'backend') -> str:
    path = path.replace("\\", "/")
    parts = [part for part in path.split("/") if part]
    if anchor not in parts:
        raise ValueError(f"anchor {anchor} is not in {parts}")
    index = parts.index(anchor)
    parts = parts[index:]
    path = "/".join(parts)
    return path


def first_relevant_rank(expected: set[str], actual: list[str]) -> int | None:
    """
        1. actual을 앞에서부터 순서대로 본다.
        2. 순서가 중요하므로 list를 그대로 돈다.
        3. Python에서는 enumerate(actual, start=1)를 쓴다.
          - start=1이 중요합니다.
          - rank는 0이 아니라 1부터 세야 합니다.
        4. 각 path가 expected 안에 있으면 즉시 그 rank를 반환한다.
        5. 끝까지 없으면 None을 반환한다.
    """
    for rank, path in enumerate(actual, start=1):
        if path in expected:
            return rank
    return None


def recall_at_k(rank: int | None, k: int) -> int:
    return None


def reciprocal_rank(rank: int | None) -> float:
    return None


def summarize_metrics(rows: list[dict], k: int) -> dict:
    return None
