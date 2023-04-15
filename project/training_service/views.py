from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from training_service.models.test import NoPassedTestError

from . import models, serializers
from .controllers import question_controller


class TopicView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: serializers.TopicListSerializer},
    )
    def list(self, request):
        topics = models.Topic.objects.all()
        return Response(serializers.TopicListSerializer(topics, many=True).data)

    @extend_schema(
        responses={200: serializers.TopicSerializer},
        parameters=[
            OpenApiParameter(
                "id",
                description="Topic id",
                required=True,
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
            )
        ],
    )
    def retrieve(self, request, pk: int):
        topic = models.Topic.get_by_id(id=pk)
        return Response(serializers.TopicSerializer(topic).data)


class TestView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: serializers.StatisticsSerializer, 302: None},
        parameters=[
            OpenApiParameter(
                name="Location",
                type=OpenApiTypes.URI,
                location=OpenApiParameter.HEADER,
                description=r"/api/topics/{id}/",
                response=[302],
            ),
            OpenApiParameter(
                "id",
                description="Test id",
                required=True,
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
            ),
        ],
    )
    def retrieve(self, request, pk: int):
        test = models.Test.get_by_id(id=pk)
        try:
            return Response(
                serializers.StatisticsSerializer(test.get_statistics(request.user)).data
            )
        except NoPassedTestError:
            return redirect("topic-detail", pk=test.topic.id)


class QuestionView(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={200: serializers.QuestionSerializer},
        parameters=[
            OpenApiParameter(
                "id",
                description="Question id",
                required=True,
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
            )
        ],
    )
    def retrieve(self, request, pk: int):
        question = models.Question.get_by_id(id=pk)
        return Response(serializers.QuestionSerializer(question).data)

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample("True answer", {"answer": True}),
                    OpenApiExample(
                        "False answer",
                        {
                            "answer": False,
                            "comment": {"id": 0, "text": "string", "question": 0},
                        },
                    ),
                    OpenApiExample(
                        "Incorrect question",
                        {"details": "The question has no right answers"},
                    ),
                    OpenApiExample(
                        "Already answered",
                        {"details": "You have already answered this question"},
                    ),
                ],
            )
        },
        parameters=[
            OpenApiParameter(
                "id",
                description="Question id",
                required=True,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                description="Array of response ids",
                required=True,
                name="ids",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        "Example 1",
                        summary="short optional summary",
                        value={"ids": [1, 2, 3]},
                    ),
                ],
            ),
        ],
        description="Send an answer to the question",
    )
    @action(detail=True, methods=["post"])
    def set_answer(self, request, pk: int):
        if not request.data.get("ids"):
            raise ValidationError("there is no data in ids")
        return Response(question_controller(request.data, request.user, pk))
