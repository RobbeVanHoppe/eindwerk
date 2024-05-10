"""Example test configuration for pytest."""
import pytest


# In this case only INFO messages will be sent to the ReportPortal.
def test_one(rp_logger):
    rp_logger.info("Case1. Step1")
    x = "this"
    rp_logger.info("x is: %s", x)
    assert 'h' in x

    # Message with an attachment.
    # import subprocess
    # free_memory = subprocess.check_output("free -h".split())
    # rp_logger.info(
    #     "Case1. Memory consumption",
    #     attachment={
    #         "name": "free_memory.txt",
    #         "data": free_memory,
    #         "mime": "application/octet-stream",
    #     },
    # )

    # This debug message will not be sent to the ReportPortal.
    rp_logger.debug("Case1. Debug message")


@pytest.fixture(autouse=True)
def skip_by_mark(request):
    if request.node.get_closest_marker('fixture_skip'):
        pytest.skip('skip by fixture')


@pytest.fixture(scope='session')
def rp_launch_id(request):
    if hasattr(request.config, "py_test_service"):
        return request.config.py_test_service.rp.launch_uuid


@pytest.fixture(scope='session')
def rp_endpoint(request):
    if hasattr(request.config, "py_test_service"):
        return request.config.py_test_service.rp.endpoint


@pytest.fixture(scope='session')
def rp_project(request):
    if hasattr(request.config, "py_test_service"):
        return request.config.py_test_service.rp.project

def test_simple(rp_logger):
    rp_logger.info("A simple test")
    assert True
