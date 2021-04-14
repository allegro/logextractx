# pylint: disable=missing-module-docstring
import logging

from .formatter import ExtraFormatter


def test_extra_formatter(log_capture):
    """ check if ExtraFormatter will render extra into log record """
    log_capture.handler.setFormatter(ExtraFormatter("%(message)s [%(extras)s]"))

    logging.info("msg with extras", extra={'e1': '1e', 'e2': '2e', 'e3': 123})

    assert log_capture.text == "msg with extras [{'e1': '1e', 'e2': '2e', 'e3': 123}]\n"
