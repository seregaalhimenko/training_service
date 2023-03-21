from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from . import models, serializers


class TopicController(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        queryset = models.Topic.objects.all()
        serializer = serializers.TopicListSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = models.Topic.objects.get(pk=pk)
        serializer = serializers.TopicSerializer(queryset)
        return Response(serializer.data)


class QuestionController(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, question_id):
        # можно убрать логику в отдельную сушьность
        question = models.Question.get_by_id(question_id)

        if self.__get_history_user_by_question(question):  # docs none
            return Response({"details": "you have already answered this question"})

        if question.check_correct_answers():
            return Response({"answers": _("The question has no right answers")})

        request_answers = question.get_answers_by_ids(request.data.get("ids"))
        request_answers_count = self.__get_count_by_correct_answers(request_answers)
        self.__create_answers_user(request_answers, question)

        if request_answers_count == len(request.data.get("ids")):
            return Response({"answer": True})

        try:
            comment = question.comment
        except models.Comment.DoesNotExist:
            return Response({"details": "no coments"})
        serializer = serializers.CommentSerializer(comment)
        return Response({"answer": False, "comment": serializer.data})

    def __get_count_by_correct_answers(self, answers):
        return answers.filter(correct=True).count()

    def __get_history_user_by_question(self, question: models.Question):
        return models.ResponseHistory.get_history_user_by_question(
            question=question,
            user=self.request.user,
        )

    def __create_answers_user(
        self,
        request_answers: list[models.AnswerChoice],
        question: models.Question,
    ):
        for answer in request_answers:
            question.create_history(answer, self.request.user)
