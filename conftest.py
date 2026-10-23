from types import SimpleNamespace

import pytest
from rest_framework.test import APIClient


@pytest.fixture
def authenticated_api_client(settings):
    settings.ROOT_URLCONF = 'tests.urls'
    client = APIClient()
    client.force_authenticate(user=SimpleNamespace(is_authenticated=True))
    return client
