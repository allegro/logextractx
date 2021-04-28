""" just views for testing """
import json

from django.http import HttpResponse

from logextractx.middleware import getLogger


def index(*_a, **_kwa):
    """ just some root view """
    return HttpResponse('{"foo": "bar"}', content_type='application/json')


def some_function():
    """ some function which will be called from logging_with_session """
    logger = getLogger("root_view")
    logger.debug("msg from function")


def logging_with_session(request, *_a, **_kwa):
    """ log using middleware during request """
    logger = getLogger("root_view")
    logger.debug("msg from root view")

    session_id = request.session.get("x-logextractx-sessid")
    assert session_id is not None

    some_function()

    payload = json.dumps({"from": "TestSessionLogged.root_view", "session_id": session_id})

    return HttpResponse(payload, content_type='application/json')

