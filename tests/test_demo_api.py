from django.urls.resolvers import URLPattern
from django.test import Client, override_settings
from rest_framework import status

from root.urls import build_urlpatterns


def test_learning_goal_get_returns_sample_contract(authenticated_api_client):
    response = authenticated_api_client.get('/api/v1/demo/learning-goal/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'title': 'Kasrlarni o‘rganish',
        'goal': 'Kasrlarni umumiy maxrajga keltirishni mashq qilish',
    }


def test_learning_goal_post_accepts_required_fields(authenticated_api_client):
    response = authenticated_api_client.post(
        '/api/v1/demo/learning-goal/',
        {'title': 'Kasrlar', 'goal': 'Umumiy maxrajni topish'},
        format='json',
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'title': 'Kasrlar',
        'goal': 'Umumiy maxrajni topish',
    }


def test_learning_goal_post_missing_goal_returns_400(authenticated_api_client):
    response = authenticated_api_client.post(
        '/api/v1/demo/learning-goal/',
        {'title': 'Kasrlar'},
        format='json',
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'goal' in response.json()


def test_schema_and_docs_urls_are_development_only():
    development_patterns = build_urlpatterns(
        debug=True,
        enable_demo_api=True,
        enable_api_docs=True,
    )
    production_patterns = build_urlpatterns(
        debug=False,
        enable_demo_api=True,
        enable_api_docs=True,
    )

    development_names = {
        pattern.name
        for pattern in development_patterns
        if isinstance(pattern, URLPattern)
    }
    production_names = {
        pattern.name
        for pattern in production_patterns
        if isinstance(pattern, URLPattern)
    }

    assert {'schema', 'api-docs', 'redoc'} <= development_names
    assert not {'schema', 'api-docs', 'redoc'} & production_names


@override_settings(ROOT_URLCONF='tests.swagger_urls')
def test_development_root_opens_swagger():
    response = Client().get('/')

    assert response.status_code == status.HTTP_200_OK
    assert b'swagger-ui' in response.content.lower()
