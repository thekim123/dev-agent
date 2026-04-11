from pathlib import Path
from unittest.mock import patch

import pytest

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


# 파일 없음 → FileNotFoundError (전파)
def test_load_golden_set_file_not_found(monkeypatch):
    def fake_read_text(self, *args, **kwargs):
        raise FileNotFoundError(f"no such file: {self}")

    monkeypatch.setattr(Path, "read_text", fake_read_text)
    with pytest.raises(FileNotFoundError):
        load_golden_set(Path("dummy.json"))


# YAML 파싱 실패 → yaml.YAMLError (전파)
def test_load_golden_set_yaml_parsing_error(monkeypatch):
    from yaml import YAMLError
    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    def fake_safe_load(self, *args, **kwargs):
        raise YAMLError(f"no yaml file: {self}")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", fake_safe_load)

    with pytest.raises(YAMLError):
        load_golden_set(Path("dummy.json"))


# 최상위가 list가 아님 → ValueError
def test_load_golden_set_not_list(monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: {"not": "a list"})
    with pytest.raises(ValueError, match=r"^top-level must be a list$"):
        load_golden_set(Path("dummy.json"))


# 원소가 dict가 아님 → ValueError (인덱스 포함 메시지)
def test_load_golden_set_not_dict(monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: ["not a dict", {"id": "ul"}])
    with pytest.raises(ValueError, match=r"item at index 0: top-level must be a dict"):
        load_golden_set(Path("dummy.json"))


# id/question/answer_files 키 누락 → ValueError (인덱스 포함)
def test_load_golden_set_no_keys(monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: [{"asdf": "asdf", "zxcv": "zxcv"}, {"id": "ul"}])
    with pytest.raises(ValueError, match=r"item at index 0: missing key - id"):
        load_golden_set(Path("dummy.json"))


# answer_files가 list[str]이 아니거나 비어있음 → ValueError
def test_load_golden_set_empty_answer_files(monkeypatch):
    fake_data = [
        {"id": "Q1", "answer_files": []},
        {"id": "Q2", "answer_files": ["doc/b.md"]},
    ]

    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: fake_data)
    with pytest.raises(ValueError, match=r"item at index 0: answer_files must not be empty"):
        load_golden_set(Path("dummy.json"))


# id 중복 → ValueError (중복된 id 포함 메시지)
def test_load_golden_set_duplicate_id(monkeypatch):
    fake_data = [
        {"id": "Q1", "answer_files": ["doc/b.mdasdf"]},
        {"id": "Q1", "answer_files": ["doc/b.md"]},
    ]

    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: fake_data)
    with pytest.raises(ValueError, match=r"items have duplicate id: Q1"):
        load_golden_set(Path("dummy.json"))


# 빈 리스트([])는 허용 — "비었다"의 의미 해석은 호출측 책임
def test_load_golden_set_empty_array(monkeypatch):
    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: [])
    result = load_golden_set(Path("dummy.json"))
    assert isinstance(result, list)
    assert result == []


def test_load_golden_set_answer_files_not_list(monkeypatch):
    fake_data = [
        {"id": "Q1", "answer_files": {"doc/b.mdasdf": "azxcd"}},
        {"id": "Q2", "answer_files": ["doc/b.md"]},
    ]

    monkeypatch.setattr(Path, "read_text", lambda self, *args, **kwargs: "unused")
    monkeypatch.setattr("eval.run_eval.yaml.safe_load", lambda s: fake_data)
    with pytest.raises(ValueError, match=r"item at index 0: answer_files must be a list"):
        load_golden_set(Path("dummy.json"))
