from django.urls import path

from apps.views import LearningGoalDemoView

urlpatterns = [
    path('api/v1/demo/learning-goal/', LearningGoalDemoView.as_view()),
]
