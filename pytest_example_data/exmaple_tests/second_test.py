import pytest


def test_should_success():
    assert 1

def test_should_also_succes():
    assert 1

@pytest.mark.skip(reason="test is supposed to skip")
def test_should_skip():
    assert 1

@pytest.mark.xfail
def test_should_fail():
    assert 0
