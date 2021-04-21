"""

In this module, you have two useful decorators: task and db_task

If you use them instead of `hyey.contrib.djhuey.task` and `huey.contrib.djhuey.db_task` then
Huey/DjHuey tasks will get extra context from callable, by magically hidden `logger` argument.

Also, if you use some other queue similar to Huey (like eg. Celery) then you can prepare your own
decorator by:

  my_celery_task = ctx2nthru_decorator(task) # where task is eg. Celery task decorator

"""
import logging
from typing import Callable

from huey.contrib import djhuey  # noqa

from .logger import LogExtraCtxAdapter
from .middleware import LogCtxData


def logger_to_ctx(fn: Callable):
    """ convert `logger` param , which is LogExtraCtxAdapter,
    to `logextra` params, which is dict, which, unlike logger
    object, is serializable

    usually, you don't need to use this decorator directly,
    only combined into @task/@db_task decorators"""
    def wrapper(*args: list, **kwargs):

        logger = kwargs.pop("logger", None)  # type: LogExtraCtxAdapter
        if logger:
            kwargs["logextra"] = logger.flat_extra()
        else:
            kwargs["logextra"] = dict(LogCtxData.extra)

        return fn(*args, **kwargs)
    return wrapper


def ctx_to_logger(fn):
    """
        get logextra param and set it to threadlocal of current
        logctxmiddleware call

        usually, you don't need to use this decorator directly,
        only combined into @task/@db_task decorators
    """
    def wrapper(*args, **kwargs):
        logextra = kwargs.pop("logextra", None)
        orig_extra = None
        extra = None
        assert logextra
        # fill threadlocal extra with data
        extra = LogCtxData.extra
        orig_extra = extra.copy()
        extra.clear()
        extra.update(logextra)
        try:
            return fn(*args, **kwargs)
        except Exception:  # noqa
            # Exception is caught here and is not re-raised. Withtout that, exception from
            # Huey will go through logging filters (including RidFilter) *after*
            # LogCtxData.extra is cleared and info about request-id/session-id is
            # lost
            logging.getLogger(__name__).exception("Uncaught exception in task %s", fn)
            return None
        finally:
            if orig_extra:  # pragma: no branch
                extra.clear()
                extra.update(orig_extra)
    wrapper.__name__ = fn.__name__
    return wrapper


def ctx2nthru_decorator(wrapped: Callable):
    """ wrap around decorator, decorate decorator. Metadecorator around djhuey
        task (or any other decorator with params)

        Essentially:
        ```
            x = ctx2nthru_wrapper(some_decorator)

            @x(foo="bar")
            def fn():
                ...
        ```

        is equivalent to

        ```
            @logger_to_ctx
            @some_decorator(foo="bar")
            @ctx_to_logger
        ```
    """
    def composite_decorator(*args, **kwargs):
        def wrapper(fn):
            odbtask = wrapped(*args, **kwargs)
            return logger_to_ctx(odbtask(ctx_to_logger(fn)))
        return wrapper
    return composite_decorator


db_task = ctx2nthru_decorator(djhuey.db_task)
task = ctx2nthru_decorator(djhuey.task)
