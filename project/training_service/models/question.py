from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404

from training_service.models import AnswerChoice, response_history


class Question(models.Model):
    text = models.CharField(max_length=500)
    test = models.ForeignKey(
        "training_service.Test",
        on_delete=models.CASCADE,
        related_name="questions",
    )

    def __str__(self) -> str:
        return self.text

    @classmethod
    def get_by_id(cls, id: int) -> "Question":
        return get_object_or_404(cls, pk=id)

    def check_correct_answers(self) -> bool:
        if self.answers.filter(correct=True).count() == 0:
            return False
        return True

    def is_valid_question(self):
        return self.answers.filter(correct=True).count() != 0

    @classmethod
    def get_valid_questions(cls, queryset) -> tuple["Question"]:
        return tuple(filter(lambda x: x.check_correct_answers(), queryset))

    def get_answers_by_ids(self, ids: list[int]) -> models.QuerySet[AnswerChoice]:
        return self.answers.filter(pk__in=ids)

    def create_history(
        self,
        answer: "AnswerChoice",
        user: settings.AUTH_USER_MODEL,
    ):
        response_history.ResponseHistory(  # fix circular import
            user=user,
            answer_choice=answer,
            question=self,
        ).save()

    def get_user_responses(
        self,
        user: settings.AUTH_USER_MODEL,
    ) -> models.QuerySet[response_history.ResponseHistory]:
        return self.response_history.filter(user=user)

    def get_answers(self) -> models.QuerySet[AnswerChoice]:
        return self.answers.all()

    def is_correct(
        self,
        request_answers: models.QuerySet[AnswerChoice] | None = None,
    ) -> bool:
        request_answers_correct_count = (
            request_answers.filter(correct=True).count()
            if request_answers
            else self.response_history.filter(answer_choice__correct=True).count()
        )
        request_answers_count = (
            len(request_answers) if request_answers else self.response_history.count()
        )
        db_answers_correct_count = self.answers.filter(correct=True).count()

        if (
            request_answers_correct_count,
            request_answers_count - request_answers_correct_count,
        ) == (db_answers_correct_count, 0):
            return True
        return False
