from django.shortcuts import get_object_or_404
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
        question = get_object_or_404(models.Question, pk=question_id)
        if self.__get_history_user_by_question(question):  # docs none
            return Response({"details": "you have already answered this question"})

        request_list_answers = question.answers.filter(pk__in=request.data.get("ids"))
        request_answers_count = self.__get_count_by_correct_answers(
            correct_answers=request_list_answers
        )
        self.__create_answers_user(request_list_answers, question)

        if request_answers_count == len(request.data.get("ids")):
            return Response({"answer": True})

        try:
            comment = question.comment
        except models.Comment.DoesNotExist:
            return Response({"details": "no coments"})
        serializer = serializers.CommentSerializer(comment)
        return Response({"answer": False, "comment": serializer.data})

    def __get_count_by_correct_answers(self, correct_answers):
        return correct_answers.filter(correct=True).count()

    def __get_history_user_by_question(self, question):
        return models.ResponseHistory.objects.filter(
            question=question,
            user=self.request.user,
        )

    def __create_answers_user(self, request_list_answers, question):
        for answer in request_list_answers:
            models.ResponseHistory(
                user=self.request.user,
                answer_choice=answer,
                question=question,
            ).save()
