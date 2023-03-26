from django.db import models


class AnswerChoice(models.Model):
    text = models.CharField(max_length=500)
    question = models.ForeignKey(
        "training_service.Question",
        on_delete=models.CASCADE,
        related_name="answers",
    )
    correct = models.BooleanField()

    def __str__(self) -> str:
        return self.text
