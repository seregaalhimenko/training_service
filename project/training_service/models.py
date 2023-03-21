from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from .comfig import CREATE_CORRECT_ANSWERS_FIRST


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


class Test(models.Model):
    title = models.CharField(max_length=200)
    topic = models.OneToOneField(
        Topic,
        on_delete=models.CASCADE,
    )
    publication_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)


class Question(models.Model):
    text = models.CharField(max_length=500)
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    def check_correct_answers(self):
        if self.answers.filter(correct=True).count() == 0:
            return False
        return True


class AnswerChoice(models.Model):
    text = models.CharField(max_length=500)
    question = models.ForeignKey(
        Question,
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


class Comment(models.Model):
    question = models.OneToOneField(
        Question,
        on_delete=models.CASCADE,
    )
    theory = models.TextField()


class ResponseHistory(models.Model):  # AnswerChoice_and_User
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="response_history",
    )
    answer_choice = models.ForeignKey(
        AnswerChoice,
        on_delete=models.CASCADE,
        related_name="response_history",
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="response_history",
    )
    # добвать уникальность на пару
