from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema


class LearningGoalInputSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    goal = serializers.CharField(required=True)


class LearningGoalDemoView(APIView):
    serializer_class = LearningGoalInputSerializer

    @extend_schema(responses=LearningGoalInputSerializer)
    def get(self, request):
        return Response({
            'title': 'Kasrlarni o‘rganish',
            'goal': 'Kasrlarni umumiy maxrajga keltirishni mashq qilish',
        })

    @extend_schema(
        request=LearningGoalInputSerializer,
        responses={status.HTTP_201_CREATED: LearningGoalInputSerializer},
    )
    def post(self, request):
        serializer = LearningGoalInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
