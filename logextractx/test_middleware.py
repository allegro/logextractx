""" test middleware related things. Eg - threadlocal dict """
# pylint: disable=redefined-outer-name
from concurrent.futures import ThreadPoolExecutor
import logging
import logging.config

import pytest

from .middleware import TLDict, uniqid as muniqid, LogCtxData


@pytest.fixture
def threadpool():
    """ init ThreadPoolExecutor, return to test functon and cleanup after test finished """
    with ThreadPoolExecutor(max_workers=10) as tpool:
        yield tpool


def test_tldict(threadpool):
    """ check if TLDict really stores data locally per thread """
    # WHEN: there is tldict with foo and bar keys
    tldict = TLDict({"foo": "bar", "bar": "foo"})
    # GIVEN: we store local key 'barba'
    tldict["barba"] = "fofo"

    def _fn():
        # THEN: in another thread, there is no 'barba' key
        assert 'barba' not in tldict
        # THEN: tldict has original/initial data
        assert tldict['foo'] == 'bar'
        assert tldict['bar'] == 'foo'

        # WHEN: storing another value in dictionary
        tldict['key_from_thread'] = 'value_from_thread'

    # WHEN: calling _fn in thread and waiting for result
    threadpool.submit(_fn).result()

    # THEN: there is no 'key_from_thread' in dictionary
    assert 'key_from_thread' not in tldict


def test_unique_seq(monkeypatch):
    """ check if session/request identifier is unique, when using LOGCTX_USE_INT debug os env """
    monkeypatch.setenv('LOGCTX_USE_INT', 'yes')
    a = muniqid()
    b = muniqid()

    assert a.isdigit()
    assert b.isdigit()

    assert int(a) + 1 == int(b)


def test_ridfilter():
    """ test if RidFilter will pass request-id and session-id fro threadlocal dictionary
        to log entries
    """
    LogCtxData.extra['session-id'] = 'foosess'
    LogCtxData.extra['request-id'] = 'fooreq'
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'RidFilter': {
                '()': 'logextractx.middleware.RidFilter'
            }
        },
        'handlers': {
            'tfi': {
                'level': 'DEBUG',
                'class': 'testfixtures.logcapture.LogCapture',
                'install': False,
            },
        },
        'root': {
                'handlers': ['tfi'],
                'level': 'DEBUG',
                'filters': ['RidFilter']
        },
        'loggers': {
            'some_logger': {
                'handlers': ['tfi'],
                'level': 'DEBUG',
                'filters': ['RidFilter']
            }
        }
    })

    logging.getLogger('some_logger').info("some msg")
    logging.getLogger('some_other_logger').info("some msg should be received by root logger")

    records = logging.getLogger().handlers[0].records
    for r in records[-2:-1]:
        assert getattr(r, "session-id") == 'foosess'
        assert getattr(r, "request-id") == 'fooreq'
