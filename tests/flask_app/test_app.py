""" just dummy module to test something """
# pylint: disable=redefined-outer-name
import pytest

from app import app


@pytest.fixture
def test_client():
    """ flask test client attached to our app """
    return app.test_client()


def test_request_id(test_client, log_capture):
    """ check if /foo endpoint will log something with request-id """
    resp = test_client.get("/foo")
    assert resp.json == {"bar": "BAR"}

    last_record = log_capture.records[-1]
    assert last_record.message == "some message logged in foo_endpoint"
    assert last_record.some_extra == "1"
    assert getattr(last_record, "request-id", None) is not None


def test_session_ids(test_client, log_capture):
    """ check if two consecutive calls will have the same session id and different request ids """
    for _ in range(2):
        test_client.get("/foo")

    lr1, lr2 = log_capture.records[-2:]

    assert getattr(lr1, "request-id") != getattr(lr2, "request-id")
    assert getattr(lr1, "session-id") == getattr(lr2, "session-id")
