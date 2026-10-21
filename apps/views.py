from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView


class LearningGoalInputSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    goal = serializers.CharField(required=True)


class LearningGoalDemoView(APIView):
    def get(self, request):
        return Response({
            'title': 'Kasrlarni o‘rganish',
            'goal': 'Kasrlarni umumiy maxrajga keltirishni mashq qilish',
        })

    def post(self, request):
        serializer = LearningGoalInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)
