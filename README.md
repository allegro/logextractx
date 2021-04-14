# LogExtraCtx

This small humble library is for making logging extra 
parameters in logging a bit easier. 


## Rationale

I have [blognote] about it (not published yet, stay tuned!)

## Usage

(look also into docstrings of modules and classes)

### Pure python

Use `getLogger` from `logextractx.logger`, and then create local logger with local
context:

```python
from logextractx.logger import getLogger
logger = getLogger(__name__)
[...]
loclogger = logger.local(extra={'DATA_IN': 'CURRENT_CONTEXT})
```

Eg:


```python
from logextractx.logger import getLogger
logger = getLogger(__name__)


def send_message(environment: str, requester: str, recipient: str, text: str) -> bool:
    """ Function send_message sends MSG to the specified recipient.  """

    # extra data to be indexed
    loclogger = logger.local(extra={'ACTION_TYPE': 'SEND_MSG',
                                    'requester': requester,
                                    'recipient': recipient,
                                    'user': str(request.user),
                                    'environment': env_type})

    try:
        r = requests.post(settings.MSG_PROVIDER, json={'recipient': recipient, 'content': text},
                          ... < other params > ....)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        loclogger.error('Sending MSG failed. Response text: "%s"', e)
        loclogger.debug("headers=%r", r.result.headers)
        return False
    loclogger.info('Sending MSG success.')
    return True
```

### Django

To tie all log records with common `request-id` and `session-id`, do the following:

* append `logextractx.middleware.LogCtxDjangoMiddleware` to your `MIDDLEWARE` in settings: 
```python
MIDDLEWARE = [
    [...]
     'django.contrib.sessions.middleware.SessionMiddleware',
    [...]
    'logextractx.middleware.LogCtxDjangoMiddleware',
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

And that's all. Now every log entry will contain `request_id` and `session_id` fields.

#### Django + DjHuey

If you want to also pass `request/session-id` to working
[Huey/DjHuey](https://huey.readthedocs.io/en/latest/django.html) by such modifications:

Instead

```python
from huey.contrib.djhuey import db_periodic_task, db_task, task
```

you should use 

```python
from logextractx.djhuey import db_periodic_task, db_task, task
```

If you do so, then all extra context, including `request-id` and `session-id` will be
passed to logger on the Djhuey side.

### Flask

LogExtraCtx in Flask is quite similar to usage in Django:

```python
from logextractx.flask import init_logctx
from logextractx.middleware import getLogger
[...]

app = flask.Flask(__name__)
app.secret_key = "don't tell anyone"
init_logctx(app)

[...]

logger = getLogger(__name__)
```


### Extra Formatter
If you use plain logging format, you may be interested in using
`logextractx.formatter.ExtraFormatter`.  Just add following in your formatter definition (DictConfig):

```python
        'formatters': {
            'simple': {
                '()': 'logextractx.formatter.ExtraFormatter',
                'fmt': '%(levelname)s %(asctime)s %(name)s: %(message)s [%(extras)s]'
            }
        }
```

And then you will have all extra in single log line.

# License:
Licensed under the Apache License, Version 2.0

[blognote]: https://blog.allegro.tech/
