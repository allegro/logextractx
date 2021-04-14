from typing import List
from django.http import HttpResponse
from django.urls import path
from django.test import Client
from django.utils.functional import empty
import pytest


@pytest.fixture(scope='function')
def view_mappers():
    """ just default, foobar root response """

    def rootview(*_a, **_kwa):
        """ just some rootview """
        return HttpResponse('{"foo": "bar"}', content_type='application/json')

    return [("", rootview)]


@pytest.fixture(scope='function')
def urls(view_mappers: List[tuple]):
    """ fixture which provide urls pseudo module, with urlpatterns and embedded simple view """
    class UrlsPseudoModule:  # pylint: disable=too-few-public-methods
        """ class which emulates URLS of django """

        urlpatterns = [path(k, v) for k, v in view_mappers]

    return UrlsPseudoModule


@pytest.fixture(scope='function')
def django_middlewares():
    return ['django.contrib.sessions.middleware.SessionMiddleware',
            'logextractx.middleware.LogCtxDjangoMiddleware']


@pytest.fixture(scope='function')
def django_configuration(django_middlewares):
    return {'DEBUG': True,
            'MIDDLEWARE': django_middlewares,
            'SESSION_ENGINE': 'django.contrib.sessions.backends.signed_cookies'}

@pytest.fixture(scope='function')
def configure_django(urls, django_configuration):
    """ configure django engine """
    from django.conf import settings

    settings._wrapped = empty  # if configured, unconfigure it
    settings.configure(**django_configuration)

    settings.ROOT_URLCONF = urls

    import django.apps

    if not django.apps.apps.ready:
        django.setup()


@pytest.fixture(scope='function')
def django_test_client(configure_django):
    """ just django test client """
    return Client()



