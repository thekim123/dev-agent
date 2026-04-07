import pytest

from eval.eval_utils import normalize_path


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
