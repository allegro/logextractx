""" pure django related tests  """
# pylint: disable=import-outside-toplevel,unused-argument,redefined-outer-name,no-self-use
import pytest


@pytest.mark.tmp
def test_foobar(client):
    """ test if django runs at all """

    response = client.get("/")
    assert response.status_code == 200

    assert response.json() == {"foo": "bar"}


# @pytest.fixture(autouse=True)
# def log_capture(self, log_capture):
#     """ log_capture fixture, but automatic """
#     return log_capture


def test_get_no_session(client, settings):
    """ smoke test

        test if application won't explode, if session middleware is not loaded

        if middleware is used, but there is no session, nothing bad will happen"""

    # cannot modify settings.MIDDLEWARE in place, because it would affect other tests
    _middleware = list(settings.MIDDLEWARE)
    _middleware.remove('django.contrib.sessions.middleware.SessionMiddleware')
    settings.MIDDLEWARE = _middleware

    client.get("/")  # and it won't explode


def test_session_is_captured(client, log_capture, settings):
    """ test if session_id is captured in logs and if persists through the calls"""

    resp = client.get("/logging_with_session")
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    # call it again
    client.get("/logging_with_session")

    # THEN: I would expect 4 log entries
    assert len(log_capture.records) == 4

    # THEN: all session-id are the same and equal to `session_id`
    for rec in log_capture.records:
        assert getattr(rec, "session-id") == session_id


def test_request_id(client, log_capture):
    """ check if tracking id populates itself during request, but changes in
    another request """
    resp = client.get("/logging_with_session")
    assert resp.status_code == 200

    # THEN: message from root_view and message from function has the same tracking id
    first_call_rid = getattr(log_capture.records[-2], "request-id")
    assert log_capture.records[-2].message == "msg from root view"

    assert log_capture.records[-1].message == "msg from function"
    assert getattr(log_capture.records[-1], "request-id") == first_call_rid

    # WHEN called again,
    client.get("/logging_with_session")
    # THEN: /view and function has the same tracking id, but
    # different than records from first call
    second_call_rid = getattr(log_capture.records[-2], "request-id")
    assert getattr(log_capture.records[-1], "request-id") == second_call_rid
    assert first_call_rid != second_call_rid
