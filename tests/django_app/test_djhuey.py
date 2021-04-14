""" tests for djhuey module """
# pylint: disable=redefined-outer-name,unused-argument,import-outside-toplevel
# pylint: disable=unexpected-keyword-arg
import pytest
from decorator import decorator

from logextractx import logger as logger_mod
from logextractx.middleware import LogCtxData


@pytest.fixture
def django_configuration(django_configuration):
    """ override default django configuration - add HUEY variable """
    django_configuration['HUEY'] = {'always_eager': True}
    return django_configuration


def test_logger_to_ctx(configure_django):
    """ check if logger parameter become logextra under decorator """
    # django settings must be configured when importing djhuey
    from logextractx.djhuey import logger_to_ctx

    # GIVEN: function decorated with logger_to_ctx
    @logger_to_ctx
    def _fn(posarg, kwarg=None, logextra=None):
        assert posarg == "foo"
        assert kwarg == "bar"
        assert logextra == {"foo": "barbar"}

    # GIVEN: logger with extra
    logger = logger_mod.getLogger("myname", extra={"foo": "barbar"})

    # WHEN: called _fn with logger, THEN _fn receive it as logextra param
    _fn("foo", "bar", logger=logger)  # pylint: disable=unexpected-keyword-arg


def test_logger_to_ctx_noparam(configure_django, monkeypatch, logctxm_extra):
    """ check if logger parameter will be filled from LogCtxData.extra
    when explicite logger param is not present """
    # django settings must be configured when importing djhuey
    from logextractx.djhuey import logger_to_ctx

    # GIVEN: extra gets 'barbar': 'fofo' param
    monkeypatch.setitem(LogCtxData.extra, 'barbar', 'fofo')

    # GIVEN: function decorated with logger_to_ctx
    @logger_to_ctx
    def _fn(posarg, kwarg=None, logextra=None):
        assert posarg == "foo"
        assert kwarg == "bar"
        assert logextra['barbar'] == "fofo"

    # WHEN: called _fn with logger, THEN _fn receive it as logextra param
    _fn("foo", "bar")  # pylint: disable=unexpected-keyword-arg


@pytest.fixture
def logctxm_extra():
    """ fixture which reverts LogCtxData.extra to old values after test end """
    old_extra = LogCtxData.extra.copy()

    yield LogCtxData.extra

    LogCtxData.extra.clear()
    LogCtxData.extra.update(old_extra)


def test_ctx_to_logger(configure_django, logctxm_extra):
    """ check if logextra dict will be converted to LogCtxData.extra
    in underlying function """
    # pylint: disable=unexpected-keyword-arg
    from logextractx.djhuey import ctx_to_logger

    error = None

    # GIVEN: function decorated with ctx_to_logger
    @ctx_to_logger
    def _fn_(fooo, barr):
        nonlocal error
        try:
            assert fooo == "baR"
            assert barr == "foO"
            assert LogCtxData.extra["extrafoo"] == "extrabar"
        except AssertionError as e:
            error = e

    # WHEN caled _fn_ with logextra params
    _fn_("baR", barr="foO", logextra={'extrafoo': 'extrabar'})
    # THEN _fn_ receive them in LogCtxData.extra (no assertion failed called)
    assert error is None


def test_ctx_to_logger_noparam(configure_django, logctxm_extra):
    """ check if  will be converted to LogCtxData.extra
    in underlying function """
    # pylint: disable=unexpected-keyword-arg
    from logextractx.djhuey import ctx_to_logger

    error = None

    # GIVEN: function decorated with ctx_to_logger
    @ctx_to_logger
    def _fn_(fooo, barr):
        nonlocal error
        try:
            assert fooo == "baR"
            assert barr == "foO"
            assert LogCtxData.extra["extrafoo"] == "extrabar"
        except AssertionError as e:
            error = e

    # WHEN caled _fn_ with logextra params
    _fn_("baR", barr="foO", logextra={'extrafoo': 'extrabar'})

    # THEN _fn_ receive them in LogCtxData.extra (no assertion failed in _fn_)
    assert error is None


@pytest.mark.tmp
def test_ctx2l_task_failed(configure_django, logctxm_extra, log_capture):
    """ check if uncaught exception is caught in @ctx_to_logger """
    # django settings must be configured when importing djhuey
    from logextractx.djhuey import ctx_to_logger

    # GIVEN: function decorated with ctx_to_loger, which raises exception
    @ctx_to_logger
    def _fnwith_error(logextra=None):
        raise RuntimeError("foo err")

    # WHEN: called _fnwith_error with logger
    _fnwith_error(logextra={'some': 'context'})

    # THEN: expected error message in logs
    record = log_capture.records[-1]
    assert "Uncaught exception in " in record.message


@pytest.mark.tmp
def test_real_djhuey_task(configure_django):
    """ check if task decorated by djhuey.task pass through the logger arg"""
    from logextractx.djhuey import task

    error = None

    @task()
    def myfunnn(ofo, obar):
        nonlocal error
        try:
            assert ofo == "ofofo"
            assert obar == "obaba"
            assert LogCtxData.extra["extraofo"] == "extraoba"
        except AssertionError as e:
            error = e

    logger = logger_mod.getLogger("myname", extra={"extraofo": "extraoba"})
    # WHEN called myfun with logger
    myfunnn("ofofo", "obaba", logger=logger)

    # THEN myfun will receive it in LogCtxDataExtra (no assertion failed in myfunnn)
    assert error is None


def test_composite_decorator(configure_django, logctxm_extra):
    """ check if ctx2nthru_decorator will compose three decorators together """
    # pylint: disable=unexpected-keyword-arg
    from logextractx.djhuey import ctx2nthru_decorator

    # GIVEN: some decorator, does roughly nothing. Decorator should be able to call as
    # @decorator() not @decorator
    def mydecorator():
        @decorator
        def _wrapped(fn, *args, **kwargs):
            return fn(*args, **kwargs)

        return _wrapped

    error = None
    # GIVEN: composite decorator from mydecorator
    compodecorator = ctx2nthru_decorator(mydecorator)

    # GIVEN: function decorated with composite decorator
    @compodecorator()
    def fn(ofo, oba):
        nonlocal error
        try:
            assert ofo == "ofofo"
            assert oba == "obaba"
            assert LogCtxData.extra["extraofo"] == "extraoba"
        except AssertionError as e:
            error = e

    # GIVEN: logger with extra
    logger = logger_mod.getLogger("myname", extra={"extraofo": "extraoba"})

    # WHEN called fn with logger
    fn("ofofo", "obaba", logger=logger)

    # THEN fn will receive it in LogCtxData.extra (no assertion failed in fn)
    assert error is None
