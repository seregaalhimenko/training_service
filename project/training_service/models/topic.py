from django.conf import settings
from django.db import models
from django.shortcuts import get_object_or_404


class Topic(models.Model):
    title = models.CharField(max_length=200)
    theory = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="topic",
    )
    publication_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    @classmethod
    def get_by_id(cls, id: int) -> "Topic":
        topic = (
            cls.objects.select_related("test")
            .prefetch_related("test__questions")
            .prefetch_related("test__questions__answers")
        )
        return get_object_or_404(topic, pk=id)

    def __str__(self) -> str:
        return self.title
