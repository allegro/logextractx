""" tests for logger.py part of code """
# pylint: disable=no-self-use
from . import logger as logger_mod


def test_getlogger(log_capture):
    """ test if you can just log something with getLogger as drop-in replacement of
    logging.getLogger """

    logger = logger_mod.getLogger("foo.bar")
    logger.info("FOO")
    logger.debug("BAR")
    logger.warning("I warn you", extra={"evar1": "data"})

    recs = log_capture.records
    assert recs[0].msg == 'FOO'
    assert recs[1].msg == 'BAR'
    assert recs[2].msg == 'I warn you'
    assert recs[2].evar1 == 'data'


def test_context_propagate(log_capture):
    """ check if extra variables propagate properly in variouls local()
    levels """
    logger = logger_mod.getLogger("foo.bar2", extra={"evar1": "initial"})

    logger.info("this is message from first logger")
    assert log_capture.records[-1].evar1 == "initial"

    loclogger = logger.local(extra={"evar1": "inlocal()", "evar2": "inlocal()"})
    loclogger.error("BOOO")
    assert log_capture.records[-1].evar1 == "inlocal()"
    assert log_capture.records[-1].evar2 == "inlocal()"

    loclogger.warning("This should override evar2", extra={"evar2": "overrided"})
    assert log_capture.records[-1].evar1 == "inlocal()"
    assert log_capture.records[-1].evar2 == "overrided"

    loclogger.extra["evar1"] = "modified by extradict"

    loclogger.debug("This should have evar1 modified in extradict")
    assert log_capture.records[-1].evar1 == "modified by extradict"
    assert log_capture.records[-1].evar2 == "inlocal()"


def test_parent_propagate(log_capture):
    """ check how logs from parent to child propagates """
    logger = logger_mod.getLogger("parent_log", extra={"parent": "logger"})
    loclog = logger.local(child="also logger")

    loclog.info("just msg")

    assert log_capture.records[-1].msg == "just msg"
    assert log_capture.records[-1].parent == "logger"
    assert log_capture.records[-1].child == "also logger"
