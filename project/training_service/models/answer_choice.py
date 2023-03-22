from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from training_service.config import CREATE_CORRECT_ANSWERS_FIRST


class AnswerChoice(models.Model):
    text = models.CharField(max_length=500)
    question = models.ForeignKey(
        "training_service.Question",
        on_delete=models.CASCADE,
        related_name="answers",
    )
    correct = models.BooleanField()

    def clean(self):
        if not CREATE_CORRECT_ANSWERS_FIRST:
            return
        if not self.correct:
            count_correct_answers = self.question.answers.filter(correct=True).count()
            if count_correct_answers == 0:
                raise ValidationError(
                    {
                        "answers": _(
                            "There are no correct answers to this question, add the correct answer first."
                        )
                    }
                )
