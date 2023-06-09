from django.db import models
from django.shortcuts import get_object_or_404
from users.models import User

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
        return get_object_or_404(cls.objects.prefetch_related("answers"), pk=id)

    def is_valid(self):
        return self.answers.filter(correct=True).count() != 0

    @classmethod
    def get_valid_questions(cls, queryset) -> tuple["Question"]:
        return tuple(filter(lambda x: x.is_valid(), queryset))

    @classmethod
    def get_count_valid_questions(cls, queryset: models.QuerySet) -> tuple["Question"]:
        return (
            queryset.annotate(
                coont_correct_answers=models.Count(
                    "answers", filter=models.Q(answers__correct=True)
                )
            )
            .filter(coont_correct_answers__gt=0)
            .count()
        )

    def get_answers_by_ids(self, ids: list[int]) -> models.QuerySet[AnswerChoice]:
        return self.answers.filter(pk__in=ids)

    def create_history(
        self,
        answer: "AnswerChoice",
        user: User,
    ):
        response_history.ResponseHistory(  # fix circular import
            user=user,
            answer_choice=answer,
            question=self,
        ).save()

    def get_user_responses(
        self,
        user: User,
    ) -> models.QuerySet[response_history.ResponseHistory]:
        return self.response_history.filter(user=user)

    def get_answers(self) -> models.QuerySet[AnswerChoice]:
        return self.answers.all()

    def __get_request_answers_correct_count_for_user(self, user: User):
        return (
            self.response_history.filter(user=user)
            .filter(answer_choice__correct=True)
            .count()
        )

    def __get_request_answers_correct_count_for_request_answers(
        self, request_answers: models.QuerySet[AnswerChoice]
    ):
        return request_answers.filter(correct=True).count()

    def __get_request_answers_count_for_request_answers(
        self, request_answers: models.QuerySet[AnswerChoice]
    ):
        return len(request_answers)

    def __get_request_answers_count_for_user(self, user: User):
        return self.response_history.filter(user=user).count()

    def __comparison_to_determine_correct_answer(
        self, request_answers_correct_count, request_answers_count
    ):
        db_answers_correct_count = self.answers.filter(correct=True).count()

        return (
            request_answers_correct_count,
            request_answers_count - request_answers_correct_count,
        ) == (db_answers_correct_count, 0)

    def is_correct_for_user(self, user):
        request_answers_correct_count = (
            self.__get_request_answers_correct_count_for_user(user)
        )
        request_answers_count = self.__get_request_answers_count_for_user(user)

        return self.__comparison_to_determine_correct_answer(
            request_answers_correct_count, request_answers_count
        )

    def is_correct_for_request_answers(self, request_answers):
        request_answers_correct_count = (
            self.__get_request_answers_correct_count_for_request_answers(
                request_answers
            )
        )
        request_answers_count = self.__get_request_answers_count_for_request_answers(
            request_answers
        )
        return self.__comparison_to_determine_correct_answer(
            request_answers_correct_count, request_answers_count
        )

    def is_correct(
        self,
        *,
        request_answers: models.QuerySet[AnswerChoice] | None = None,
        user: User | None = None,
    ) -> bool:
        if not user and not request_answers:
            raise ValueError(
                "If you do not specify 'request_answers', then you must specify 'user'"
            )
        if user:
            return self.is_correct_for_user(user)
        return self.is_correct_for_request_answers(request_answers)
