import pytest

args = ["time", "positive_Ze", "filename", "header", "data"]


def pytest_addoption(parser):
    for arg in args:
        parser.addoption(f"--{arg}", action="store")


@pytest.fixture
def params(request):
    return {arg: request.config.getoption(f"--{arg}") for arg in args}
