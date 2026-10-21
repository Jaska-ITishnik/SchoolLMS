from django.test import SimpleTestCase
from django.urls.resolvers import URLPattern
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate

from root.urls import build_urlpatterns
from .views import LearningGoalDemoView


class LearningGoalDemoTests(SimpleTestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = LearningGoalDemoView.as_view()
        self.user = type('AuthenticatedUser', (), {'is_authenticated': True})()

    def request_as_user(self, request):
        force_authenticate(request, user=self.user)
        return self.view(request)

    def test_get_returns_synthetic_learning_goal_json(self):
        request = self.factory.get('/api/v1/demo/learning-goal/')

        response = self.request_as_user(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'title': 'Kasrlarni o‘rganish',
            'goal': 'Kasrlarni umumiy maxrajga keltirishni mashq qilish',
        })

    def test_post_validates_required_fields(self):
        request = self.factory.post(
            '/api/v1/demo/learning-goal/',
            {'title': 'Kasrlar', 'goal': 'Umumiy maxrajni topish'},
            format='json',
        )

        response = self.request_as_user(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {
            'title': 'Kasrlar',
            'goal': 'Umumiy maxrajni topish',
        })

    def test_post_with_missing_field_returns_400(self):
        request = self.factory.post(
            '/api/v1/demo/learning-goal/', {'title': 'Kasrlar'}, format='json'
        )

        response = self.request_as_user(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('goal', response.data)

    def test_malformed_json_returns_400(self):
        request = self.factory.generic(
            'POST',
            '/api/v1/demo/learning-goal/',
            data='{"title":',
            content_type='application/json',
        )

        response = self.request_as_user(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_method_returns_405_for_authenticated_user(self):
        request = self.factory.delete('/api/v1/demo/learning-goal/')

        response = self.request_as_user(request)

        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_global_permission_requires_authentication(self):
        request = self.factory.get('/api/v1/demo/learning-goal/')

        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_demo_route_is_excluded_when_debug_is_off(self):
        production_patterns = build_urlpatterns(debug=False, enable_demo_api=True)

        self.assertFalse(any(
            isinstance(pattern, URLPattern)
            and pattern.name == 'demo-learning-goal'
            for pattern in production_patterns
        ))

    def test_demo_route_needs_explicit_flag_in_development(self):
        development_patterns = build_urlpatterns(debug=True, enable_demo_api=True)
        default_patterns = build_urlpatterns(debug=True, enable_demo_api=False)

        self.assertTrue(any(
            isinstance(pattern, URLPattern)
            and pattern.name == 'demo-learning-goal'
            for pattern in development_patterns
        ))
        self.assertFalse(any(
            isinstance(pattern, URLPattern)
            and pattern.name == 'demo-learning-goal'
            for pattern in default_patterns
        ))
