""" flask part of request processing / "middleware" """

import flask  # noqa

from logextractx.middleware import LogCtxData, uniqid


def _set_logctx_data():
    """ function called before flask request. Equivalent of Diango's middleware """
    session = flask.session
    # unlike django session, flask session doesn't seem to have exposed session id,
    # so let's create one if doesn't exist
    if not session.get("x-logextractx-sessid"):
        session_key = uniqid()
        session["x-logextractx-sessid"] = session_key
    else:
        session_key = session["x-logextractx-sessid"]
    LogCtxData.reset(session_id=session_key, do_hash=False)


def init_logctx(flask_app: flask.Flask):
    """ install @before_request on our "middleware" function """
    flask_app.before_request(_set_logctx_data)
