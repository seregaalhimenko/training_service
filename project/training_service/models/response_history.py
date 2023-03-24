from django.conf import settings
from django.db import models

from training_service.models import question as q  # fix circular import


class ResponseHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="response_history",
    )
    answer_choice = models.ForeignKey(
        "training_service.AnswerChoice",
        on_delete=models.CASCADE,
        related_name="response_history",
    )
    question = models.ForeignKey(
        "training_service.Question",
        on_delete=models.CASCADE,
        related_name="response_history",
    )

    @classmethod
    def get_history_user_by_question(
        cls,
        user: settings.AUTH_USER_MODEL,
        question: "q.Question",
    ) -> models.QuerySet["ResponseHistory"]:
        return cls.objects.filter(
            question=question,
            user=user,
        )

    @classmethod
    def get_count_question_by_user(
        cls,
        user: settings.AUTH_USER_MODEL,
    ) -> int:
        return cls.objects.filter(user=user).values("question").distinct().count()
