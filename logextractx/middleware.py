"""
It's desirable to add tracking id to log records, which belongs to the same HTTP request.
So far such tracking id is made only for Django.

In your DJANGO project, you should use the following:

* append `logextractx.middleware.LogCtxMiddleware` to your `MIDDLEWARE` in settings:
```python
MIDDLEWARE = [
    [...]
     'django.contrib.sessions.middleware.SessionMiddleware',
    [...]
    'logextractx.middleware.LogCtxMiddleware',
 ]
```

And instead of `logextractx.logger` use `logextractx.middleware` so:

```python
from logextractx.logger import getLogger
logger = getLogger(__name__)
[...]
```

Also, you need to add filter into logging
```python
    'filters': {
        'RidFilter': {
            '()': 'logextractx.middleware.RidFilter'
        }
    }
```
"""

import logging
import os
import uuid
import threading
from typing import Dict

from logextractx import logger as ctxlogger


def uniqid() -> str:
    """ uniquid - alias for str(uuid.uuid4()) however, for easier debugging, it will
    return subsequent numbers, if LOGCTX_USE_INT is set in your environment variables """
    if os.environ.get("LOGCTX_USE_INT", "").lower() in ("1", "yes", "tak", "y", "t"):
        next_id = getattr(uniqid, "_cnter", 0) + 1
        uniqid._cnter = next_id  # type: ignore  # noqa
        return str(next_id)
    return str(uuid.uuid4())


class TLDict(threading.local):
    """
    Dictionary-like object which holds it's data in threadlocal.
    """

    def __init__(self, data: dict):
        super().__init__()
        self.data = data.copy()

    def __contains__(self, k):
        return k in self.data

    def __getitem__(self, k):
        return self.data[k]

    def __delitem__(self, k):
        del self.data[k]

    def __setitem__(self, k, v):
        self.data[k] = v

    def get(self, *a, **kwa):
        """ wwrapper around inner dict get() """
        return self.data.get(*a, **kwa)

    def copy(self):
        """ wrapper around inner dict copy() """
        return self.data.copy()

    def clear(self):
        """ wrapper around inner dict clear() """
        return self.data.clear()

    def keys(self):
        """ wrapper around inner dict keys() """
        return self.data.keys()

    def reset(self):
        """
        clear data and set request-id and session-id to None
        """
        self.clear()
        self.data["request-id"] = self.data["session-id"] = None

    def update(self, *a, **kwa):
        """ wrapper around inner dict update() method """
        self.data.update(*a, **kwa)


class LogCtxData:
    """ class which stores threadlocal and logic common for Django and Flask

        tracks requests and sessions, and helps LogExtraCtxAdapter to add
            request-id and session-id to context of logging.

        Flask has no session id exposed, and session-id in Django can change (depending on session
        engine used), so we cannot rely on it, so it's better to just generate some uniqid
        and store it in session data.
    """
    extra = TLDict({"request-id": None, "session-id": None})

    @classmethod
    def init_request_data(cls, session: Dict[str, str]):
        """
        - generate and set request id
        - get or create session_id
        - store them both in session dict
        - store it in threadlocal
        """
        if not session.get("x-logextractx-sessid"):
            session_id = uniqid()
            session["x-logextractx-sessid"] = session_id
        else:
            session_id = session["x-logextractx-sessid"]

        request_id = uniqid()

        cls.extra.reset()
        cls.extra["request-id"] = request_id
        cls.extra["session-id"] = session_id


class LogCtxDjangoMiddleware:
    """
    django middleware
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            LogCtxData.init_request_data(session=request.session)
        except AttributeError:
            # when there is no session
            pass

        return self.get_response(request)


class RidFilter(logging.Filter):
    """
    logging filter neccessary to add request-id and session-id to logging records.
    """
    def filter(self, record):
        """ append request-id and session-id to logging record """
        extra = LogCtxData.extra
        setattr(record, "request-id", extra['request-id'])
        setattr(record, "session-id", extra['session-id'])

        return True


def getLogger(name: str) -> ctxlogger.LogExtraCtxAdapter:
    """ drop in replacement for logging.getLogger()
        returns logger adapter with context from LogCtxMiddleware
        (request-id and session-id are stored there)
    """
    lgr = logging.getLogger(name)
    return ctxlogger.LogExtraCtxAdapter(lgr, LogCtxData.extra)
