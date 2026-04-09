import pytest

from eval.eval_utils import normalize_path, first_relevant_rank, recall_at_k, reciprocal_rank, summarize_metrics


def test_success_normalize_path():
    input1 = "D:\\workspace\\\\backend\\src\\main\\java\\com\\example\\UserService.java"
    result = normalize_path(input1)
    assert result == 'backend/src/main/java/com/example/UserService.java'


def test_success_idempotent_normalize_path():
    path = "backend/src/main/java/com/example/UserService.java"
    assert normalize_path(path) == path


# anchor에 해당하는거 없을 때 실패함
def test_raise_when_anchor_missing_normalize_path():
    input2 = "D:\\workspace\\\\doc\\src\\main\\java\\com\\example\\UserService.java"
    with pytest.raises(ValueError):
        normalize_path(input2)


def test_success_first_relevant_rank_1():
    expected = {'a.py', 'b.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    rank = first_relevant_rank(expected, actual)
    assert rank == 1


def test_success_first_relevant_rank_2():
    expected = {'b.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    rank = first_relevant_rank(expected, actual)
    assert rank == 2


# 정답 개수 (1개 / 여러 개)
def test_success_recall_at_k_all_relevant_in_1():
    top_k = 3
    expected = {'a.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    result = recall_at_k(expected, actual, top_k)
    assert result == 1 / 1


# top-k 안에 정답이 전부 들어온 경우
def test_success_recall_at_k_all_relevant_in_top_k():
    top_k = 3
    expected = {'a.py', 'b.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    result = recall_at_k(expected, actual, top_k)
    assert result == 2 / 2


# top-k 안에 정답이 일부만 들어온 경우
def test_success_recall_at_k_portion():
    top_k = 3
    expected = {'a.py', 'b.py', 'z.py', 'x.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    result = recall_at_k(expected, actual, top_k)
    assert result == 2 / 4


# top-k 안에 정답이 하나도 없는 경우
def test_success_recall_at_k_no_answer():
    top_k = 3
    expected = {'z.py', 'x.py', 's.py', 'v.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    result = recall_at_k(expected, actual, top_k)
    assert result == 0 / 4


# k 경계 — 정답이 정확히 k번째 / k+1번째에 있을 때
def test_recall_at_k_k_boundary_relevant():
    top_k = 3
    expected = {'c.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    result = recall_at_k(expected, actual, top_k)
    assert result == 1 / 1


# actual의 길이가 k보다 짧을 때 (검색 결과가 5개밖에 없는데 k=10)
def test_recall_at_k_actual_shorter_than_k():
    top_k = 10
    expected = {'a.py', 'b.py', 'e.py', 'd.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    result = recall_at_k(expected, actual, top_k)
    assert result == 4 / 4


def test_recall_at_k_smaller_than_one():
    top_k = 0
    expected = {'a.py', 'b.py', 'c.py', 'd.py', 'e.py'}
    actual = ['a.py', 'b.py', 'c.py', 'd.py', 'e.py']
    with pytest.raises(ValueError):
        recall_at_k(expected, actual, top_k)


def test_reciprocal_rank_none():
    rr = reciprocal_rank(None)
    assert rr == 0.0


def test_reciprocal_rank_success():
    rr = reciprocal_rank(2)
    assert rr == 1 / 2


def test_reciprocal_rank_zero():
    with pytest.raises(ValueError):
        reciprocal_rank(0)


def test_reciprocal_rank_negative_raises():
    with pytest.raises(ValueError):
        reciprocal_rank(-1)


def test_reciprocal_rank_perfect():
    rr = reciprocal_rank(1)
    assert rr == 1


# 평균 계산이 정확한가? (예: [0.5, 1.0] → 0.75)
# dict 키 이름이 정확히 mean_recall_at_k, mrr인가?
# 단일 row도 제대로 동작하나?
def test_summarize_metrics_multiple_rows():
    test_rows = [
        {
            "recall_at_k": 0.5,
            "reciprocal_rank": 1
        },
        {
            "recall_at_k": 1.0,
            "reciprocal_rank": 0.5
        }
    ]
    result_dict = summarize_metrics(test_rows)
    assert result_dict["mean_recall_at_k"] == pytest.approx(0.75)
    assert result_dict["mrr"] == pytest.approx(0.75)


def test_summarize_metrics_single_row():
    test_rows = [
        {
            "recall_at_k": 0.5,
            "reciprocal_rank": 1
        },
    ]
    result_dict = summarize_metrics(test_rows)
    assert result_dict["mean_recall_at_k"] == pytest.approx(0.5)
    assert result_dict["mrr"] == pytest.approx(1)


def test_summarize_metrics_empty_row():
    expected_errors: tuple[type[Exception], ...] = (ZeroDivisionError, ValueError)
    with pytest.raises(expected_errors):
        summarize_metrics([])