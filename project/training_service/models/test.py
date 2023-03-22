from django.db import models
from django.shortcuts import get_object_or_404

from training_service.models.question import Question
from training_service.models.response_history import ResponseHistory


class Test(models.Model):
    title = models.CharField(max_length=200)
    topic = models.OneToOneField(
        "training_service.Topic",
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
