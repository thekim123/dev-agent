from pathlib import Path
from unittest.mock import patch

from eval.run_eval import load_golden_set

patch("eval.run_eval.yaml.safe_load")


def test_load_golden_set_success(monkeypatch):
    # 1. 가짜 데이터 준비
    fake_data = [
        {"id": "Q1", "answer_files": ["Alice"]},
        {"id": "Q2", "answer_files": ["doc/b.md"]},
    ]

    # 2. read_text를 가짜로 바꿔치기
    #    어떤 문자열을 리턴하든 상관없음 — 어차피 json.loads도 모킹할 거니까
    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    # 3. json.loads를 가짜로 바꿔치기
    #    주의: "json.loads"가 아니라 "app.users.json.loads"
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: fake_data)

    # 4. 실행 — path 인자는 아무거나
    result = load_golden_set(Path("dummy.json"))

    # 5. 계약 검증
    assert isinstance(result, list)
    assert result == fake_data
    assert len(result) == 2
    assert result[0]["id"] == "Q1"
    assert result[1]["answer_files"] == ["doc/b.md"]


def test_load_golden_set_file_not_found():
    ...


def test_load_golden_set_yaml_parsing_error():
    ...


def test_load_golden_set_not_list():
    ...


def test_load_golden_set_not_dict():
    ...


def test_load_golden_set_no_keys():
    ...


def test_load_golden_set_empty_answer_files():
    ...


def test_load_golden_set_duplicate_id():
    ...


def test_load_golden_set_empty_array():
    ...


def test_load_golden_set_answer_files_not_list():
    ...
