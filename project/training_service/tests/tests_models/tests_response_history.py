from django.db import models

from training_service.models import ResponseHistory
from training_service.tests.base import Base


class TestResponseHistory(Base):
    def setUp(self) -> None:
        self.response_history = {
            self.user: {
                self.question: ResponseHistory.objects.create(
                    user=self.user,
                    question=self.question,
                    answer_choice=self.answer_choices[self.question][False],
                )
            },
            self.user_2: {
                self.question: ResponseHistory.objects.create(
                    user=self.user_2,
                    answer_choice=self.answer_choices[self.question][True],
                    question=self.question,
                ),
                self.question_2: ResponseHistory.objects.create(
                    user=self.user_2,
                    answer_choice=self.answer_choices[self.question_2][True],
                    question=self.question_2,
                ),
            },
        }

    def test_get_history_user_by_question(self):
        self.response_history_obj = ResponseHistory.get_history_user_by_question(
            user=self.user, question=self.question
        )
        self.assertIsInstance(self.response_history_obj, models.QuerySet)
        self.assertEqual(
            list(self.response_history_obj),
            [self.response_history[self.user][self.question]],
        )
        self.assertEqual(
            list(
                ResponseHistory.get_history_user_by_question(
                    user=self.user_2, question=self.question
                )
            ),
            [self.response_history[self.user_2][self.question]],
        )
        self.assertEqual(
            list(
                ResponseHistory.get_history_user_by_question(
                    user=self.user_2, question=self.question_2
                )
            ),
            [self.response_history[self.user_2][self.question_2]],
        )

    def test_get_count_question_by_user(self):
        count_question_by_user = ResponseHistory.get_count_question_by_user(
            user=self.user
        )
        count_question_by_user_2 = ResponseHistory.get_count_question_by_user(
            user=self.user_2
        )
        self.assertIsInstance(count_question_by_user, int)
        self.assertEqual(count_question_by_user, 1)
        self.assertEqual(count_question_by_user_2, 2)
