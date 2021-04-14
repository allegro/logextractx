""" useful fixtures for testing """
# pylint: disable=redefined-outer-name
import logging

import pytest


@pytest.fixture
def log_capture(caplog):
    """ if you use this fixture, logs will be captures
    in log_capture object """
    caplog.set_level(logging.DEBUG)
    return caplog
