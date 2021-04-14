"""
This module gives you ability to add context informations to data *once*, and this data
will be repeated in each log entry of given context.
So instead of doing this:
```
logger = logging.getLogger(__name__)
```

use

```
from logextractx.logger import getLogger
logger = getLogger(__name__)
```

then you can add extra data to it by:

```
logger.extra["request-id"] = "12345"
```

and all subsequent ```logger.info("foo bar")``` will be called as
logging.Logger is called with
```.info("foo bar", extra={'request-id': '12345'})```

# LOCAL CONTEXT

if you do:
```
logger = logextractx.logger.getLogger()
logger.extra["request-id"] = "123456"

llog = logger.local(extra={'db_type': 'POSTGRES'})
#OR
llog = logger.local(db_type='POSTGRES')
#OR
llog = logger.local()
llog.extra["db_type"] = "POSTGRES"
```

then ```llog.info("db modified")``` will log record with
extra={'request-id': '12345', 'db_type': 'POSTGRES'}

In meantime, if you modify parent logger (logger.extra), changes will
be reflected by local context too

"""
import logging

from collections.abc import Mapping
from functools import reduce
from typing import List, Optional


class LogExtraCtxAdapter(logging.LoggerAdapter):
    """ logger adapter which holds extra context (added to each log record) and combines
        it with context parent adapter """
    def __init__(self, logger, extra, parent: 'LogExtraCtxAdapter' = None):
        super().__init__(logger, extra)
        self.extras = []  # type: List[dict]
        if parent:
            self.extras = parent.extras.copy()
        self.extras.append(extra)

    def local(self, extra=None, **kwargs):
        """ spawn local context """
        assert not kwargs or not extra, "You shouldn't specify both extra and kwargs"
        extra = extra or kwargs or {}
        return LogExtraCtxAdapter(self.logger, extra=extra, parent=self)

    def flat_extra(self, kwargs=None):
        """ return all extras flattened to one dict
        (eg. to serialize or display in logs) """
        if kwargs is None:
            kwargs = {}
        return reduce(lambda x, y: dict(x, **y), self.extras + [kwargs.get("extra", {})])

    def process(self, msg, kwargs):
        # is it nasty hack?
        # recalculate extra based on (maybe changed) extra parameters of
        # this logger and parent loggers
        if "extra" in kwargs:
            # in case if someone pass non-dictionary to extra, this assert will produce
            # more understandable error than that one coming from reduce
            assert kwargs["extra"] is not None
            assert isinstance(kwargs["extra"], Mapping)

        kwargs["extra"] = self.flat_extra(kwargs)
        return msg, kwargs


def getLogger(name: str, extra: Optional[dict] = None):
    """
        returns logger adapted to extra context passing.
        :param name:str - name of logger (just like in logging.getLogger()
        :param extra:dict - optional dictionary with extra
    """
    extra = extra or {}
    return LogExtraCtxAdapter(logging.getLogger(name), extra)
