from dataclasses import dataclass

from django.conf import settings
from django.db import models
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from training_service.models import ResponseHistory
from training_service.models.question import Question


class NoPassedTestError(Exception):
    pass


class Test(models.Model):
    title = models.CharField(max_length=200)
    topic = models.OneToOneField(
        "training_service.Topic",
        on_delete=models.CASCADE,
    )
    publication_date = models.DateField(auto_now_add=True)
    update_date = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    @classmethod
    def get_by_id(cls, id: int) -> "Test":
        return get_object_or_404(cls, pk=id)

    def is_passed(self, user: settings.AUTH_USER_MODEL) -> bool:
        questions_test = self.questions.all()
        count_questions_test = Question.get_count_valid_questions(questions_test)
        count_questions_history = ResponseHistory.get_count_question_by_user(user)
        return count_questions_history == count_questions_test

    def get_statistics(self, user: settings.AUTH_USER_MODEL):
        if not self.is_passed(user):
            raise NoPassedTestError

        @dataclass
        class StatisticsTest:
            user: settings.AUTH_USER_MODEL
            test: "Test"
            questions: QuerySet[Question]
            correct_count: int
            incorrect_count: int

            def __str__(self) -> str:
                return f"Увожаемый {self.user.email}.Тест {self.test.title} пройден.\n \
                правильных ответов на вопрос:{self.correct_count}\n  \
                не правильных ответов на вопрос:{self.incorrect_count}\n"

        questions: QuerySet[Question] = self.questions.filter(
            response_history__user=user
        ).distinct()
        correct_count = 0
        for question in questions:
            if question.is_correct(user=user):
                correct_count += 1
        incorrect_count = questions.count() - correct_count

        return StatisticsTest(
            user=user,
            test=self,
            questions=questions,
            correct_count=correct_count,
            incorrect_count=incorrect_count,
        )
