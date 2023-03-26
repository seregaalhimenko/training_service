from django.db import models


class Comment(models.Model):
    question = models.OneToOneField(
        "training_service.Question",
        on_delete=models.CASCADE,
    )
    text = models.TextField()

    def __str__(self) -> str:
        return self.text
