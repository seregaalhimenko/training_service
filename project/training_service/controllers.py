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
        db_answers_correct_count = self.__get_count_by_correct_answers(question.answers)
        request_answers_correct_count = self.__get_count_by_correct_answers(
            request_answers
        )
        self.__create_answers_user(user, request_answers, question)
        request_answers_incorrect_count = (
            len(data.get("ids")) - request_answers_correct_count
        )
        if (
            request_answers_correct_count,
            request_answers_incorrect_count,
        ) == (
            db_answers_correct_count,
            0,
        ):
            return {"answer": True}

        comment = self.__get_comment(question)
        return {"answer": False, "comment": comment}

    def __get_comment(self, question: models.Question):
        try:
            comment = question.comment
        except models.Comment.DoesNotExist:
            return {"details": "Not found."}
        return serializers.CommentSerializer(comment).data

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
