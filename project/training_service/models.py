from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import get_object_or_404
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

    def is_passed(self, user) -> bool:
        questions_test = self.questions.all()
        count_questions_test = len(Question.get_valid_questions(questions_test))
        count_questions_history = ResponseHistory.get_count_question_by_user(user)
        return count_questions_history == count_questions_test

    @classmethod
    def get_by_id(cls, id: int):
        return get_object_or_404(cls, pk=id)


class Question(models.Model):
    text = models.CharField(max_length=500)
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name="questions",
    )

    @classmethod
    def get_by_id(cls, id: int):
        return get_object_or_404(cls, pk=id)

    def check_correct_answers(self):
        if self.answers.filter(correct=True).count() == 0:
            return False
        return True

    @classmethod
    def get_valid_questions(cls, queryset) -> tuple["Question"]:
        return tuple(filter(lambda x: x.check_correct_answers(), queryset))

    def get_answers_by_ids(self, ids: list[int]):
        return self.answers.filter(pk__in=ids)

    def create_history(
        self,
        answer: "AnswerChoice",
        user: settings.AUTH_USER_MODEL,
    ):
        ResponseHistory(
            user=user,
            answer_choice=answer,
            question=self,
        ).save()

    def get_user_responses(
        self,
        user: settings.AUTH_USER_MODEL,
    ):
        return self.response_history.filter(user=user)

    def get_answers(self):
        return self.answers.all()  # ?


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

    @classmethod
    def get_history_user_by_question(
        cls,
        user: settings.AUTH_USER_MODEL,
        question: Question,
    ):
        return cls.objects.filter(
            question=question,
            user=user,
        )

    @classmethod
    def get_count_question_by_user(
        cls,
        user: settings.AUTH_USER_MODEL,
    ):
        return cls.objects.filter(user=user).values("question").distinct().count()
