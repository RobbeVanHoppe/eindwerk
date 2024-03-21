import pytest
import logging
from pytest_zebrunner.zebrunner_logging import ZebrunnerHandler


logger = logging.getLogger(__name__) # It might be any logger that you created earlier
logger.addHandler(ZebrunnerHandler())

def test_should_success():
    assert 1

def test_should_also_succes():
    assert 1

@pytest.mark.skip(reason="test is supposed to skip")
def test_should_skip():
    assert 1

def test_should_fail():
    assert 0
    