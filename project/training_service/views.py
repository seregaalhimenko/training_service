from django.shortcuts import redirect
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers
from .controllers import question_controller


class TopicView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        topics = models.Topic.objects.all()
        return Response(serializers.TopicListSerializer(topics, many=True).data)

    def retrieve(self, request, pk=None):
        topic = models.Topic.objects.get(pk=pk)
        return Response(serializers.TopicSerializer(topic).data)


class TestView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        test = models.Test.get_by_id(id=pk)
        if test.is_passed(request.user):
            return Response(
                serializers.StatisticsSerializer(test.get_statistics(request.user)).data
            )
        return redirect("topic-detail", pk=test.topic.id)


class QuestionView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, pk=None):
        question = models.Question.get_by_id(id=pk)
        return Response(serializers.QuestionSerializer(question).data)

    @action(detail=True, methods=["post"])
    def set_answer(self, request, pk=None):
        return Response(question_controller(request.data, request.user, pk))
