from django.conf import settings
from django.utils.translation import gettext_lazy as _

from . import models, serializers


class QuestionController:
    def __call__(self, data, user: settings.AUTH_USER_MODEL, question_id: int):
        question: models.Question = models.Question.get_by_id(question_id)

        if self.__get_history_user_by_question(user, question):  # docs none
            return {"details": "you have already answered this question"}

        if not question.check_correct_answers():
            return {"answers": _("The question has no right answers")}

        request_answers = question.get_answers_by_ids(data.get("ids"))
        request_answers_count = self.__get_count_by_correct_answers(request_answers)
        self.__create_answers_user(user, request_answers, question)

        if request_answers_count == len(data.get("ids")):
            return {"answer": True}

        try:
            comment = question.comment
        except models.Comment.DoesNotExist:
            return {"details": "no coments"}
        serializer = serializers.CommentSerializer(comment)
        return {"answer": False, "comment": serializer.data}

    def __get_count_by_correct_answers(self, answers):
        return answers.filter(correct=True).count()

    def __get_history_user_by_question(
        self, user: settings.AUTH_USER_MODEL, question: models.Question
    ):
        return models.ResponseHistory.get_history_user_by_question(
            question=question,
            user=user,
        )

    def __create_answers_user(
        self,
        user: settings.AUTH_USER_MODEL,
        request_answers: list[models.AnswerChoice],
        question: models.Question,
    ):
        for answer in request_answers:
            question.create_history(answer, user)


question_controller = QuestionController()
