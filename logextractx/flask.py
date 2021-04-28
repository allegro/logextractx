""" flask part of request processing / "middleware" """

import flask  # noqa

from logextractx.middleware import LogCtxData


def _set_logctx_data():
    """ function called before flask request. Equivalent of Diango's middleware """
    session = flask.session
    LogCtxData.init_request_data(session=session)


def init_logctx(flask_app: flask.Flask):
    """ install @before_request on our "middleware" function """
    flask_app.before_request(_set_logctx_data)
