from testfixtures import LogCapture
import pytest


@pytest.fixture
def log_capture():  # TODO: use builtin pytest mechanism?
    with LogCapture() as l:
        yield l
