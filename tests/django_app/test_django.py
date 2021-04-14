""" test django which run almost entirely in code, without project
file structure """
# pylint: disable=import-outside-toplevel,unused-argument,redefined-outer-name,no-self-use
import hashlib

from django.http import HttpResponse
import pytest


@pytest.mark.tmp
def test_foobar(configure_django, django_test_client):
    """ test if django runs at all """

    request = django_test_client.get("/")
    assert request.status_code == 200

    assert request.json() == {"foo": "bar"}


@pytest.mark.tmp
class TestNoSession:
    """ test if application won't explode, if session middleware is not loaded """

    @pytest.fixture
    def django_middlewares(self):
        """ return middlewares used in this test """
        return ["logextractx.middleware.LogCtxDjangoMiddleware"]

    @pytest.fixture(autouse=True)
    def capture_logs(self, log_capture):
        """ store log_capture in class attributes """
        self.log_capture = log_capture  # noqa: PLW0201

    def test_get_no_session(self, django_test_client):
        """if middleware is used, but there is no session, nothing should explode"""
        django_test_client.get("/")  # and it won't explode


class TestSessionLogged:   # pylint: disable=attribute-defined-outside-init
    """ test if session is logged """

    @pytest.fixture(autouse=True)
    def setup(self):
        """ setup initial data """
        self.request_id = None
        self.session_hash = None

    @pytest.fixture(autouse=True)
    def capture_logs(self, log_capture):
        """ store log_capture in class attributes """
        self.log_capture = log_capture

    @pytest.fixture
    def view_mappers(self):
        """ override default url:view mappers """
        return [("", self.root_view)]

    def some_function(self):
        """ some function which will be called from root_view """
        from logextractx.middleware import getLogger
        logger = getLogger("root_view")
        logger.debug("msg from function")

    def root_view(self, request, *a, **kwa):
        """ root view for this django instance """
        from logextractx.middleware import getLogger
        logger = getLogger("root_view")
        logger.debug("msg from root view")

        session_key = request.session.session_key
        assert session_key is not None
        session_hash = hashlib.sha1(session_key.encode("UTF-8")).hexdigest()
        # sanity check - check if session id didn't change between calls
        assert self.session_hash in (None, session_hash)

        self.session_hash = session_hash

        self.some_function()

        return HttpResponse('{"from": "TestSessionLogged.root_view"}',
                            content_type='application/json')

    def test_session_is_captured(self, django_test_client):
        """ test if session_id is captured in logs """
        request = django_test_client.get("/")
        assert request.status_code == 200

        assert getattr(self.log_capture.records[-1], "session-id") == self.session_hash
        # check if it's still the same session-id
        assert getattr(self.log_capture.records[-1], "session-id") == self.session_hash

    def test_request_id(self, django_test_client):
        """ check if tracking id populates itself during request, but changes in
        another request """
        request = django_test_client.get("/")
        assert request.status_code == 200

        # THEN: message from root_view and message from function has the same tracking id
        first_call_trid = getattr(self.log_capture.records[-2], "request-id")
        assert self.log_capture.records[-2].message == "msg from root view"

        assert self.log_capture.records[-1].message == "msg from function"
        assert getattr(self.log_capture.records[-1], "request-id") == first_call_trid

        # WHEN called again,
        django_test_client.get("/")
        second_call_trid = self.request_id
        # THEN: root_view and function has the same tracking id, but
        # different than first
        second_call_trid = getattr(self.log_capture.records[-2], "request-id")
        assert getattr(self.log_capture.records[-1], "request-id") == second_call_trid
        assert first_call_trid != second_call_trid
