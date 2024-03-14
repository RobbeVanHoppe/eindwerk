import pytest

def function_to_test(x: int) -> int:
    return x + 5

def test_func_to_test():
    assert function_to_test(5) == 10

@pytest.mark.xfail
def test_fail():
    assert 0