"""
Use this ExtraFormatter to show all extras in your logs.
Just add following in your formatter definition (DictConfig):

```python
        'formatters': {
            'simple': {
                '()': 'logextractx.formatter.ExtraFormatter',
                'fmt': '%(levelname)s %(asctime)s %(name)s: %(message)s [%(extras)s]'
            }
        }
```

"""

import logging


class ExtraFormatter(logging.Formatter):
    """ formatter which let see all extra passed to log record """
    def format(self, record):
        # inspired by https://stackoverflow.com/questions/39965807/python-log-formatter-that-shows-all-kwargs-in-extra/39974319  # noqa
        dummy = logging.LogRecord(None, None, None, None, None, None, None)
        extras = {}
        for k, v in record.__dict__.items():
            if k not in dummy.__dict__:
                extras[k] = v
        record.extras = extras
        return super().format(record)
