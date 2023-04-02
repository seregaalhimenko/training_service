from django.http import Http404

from training_service.models import ResponseHistory, Test
from training_service.models.test import NoPassedTestError
from training_service.tests.base import Base


class TestTest(Base):
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

    def test__str__(self):
        self.assertEqual(str(self.test), self.test.title)

    def test_get_by_id(self):
        with self.assertRaises(Http404):
            fake_id = Test.objects.last().id + 1
            Test.get_by_id(id=fake_id)
        self.assertEqual(Test.get_by_id(self.test.id), self.test)

    def test_is_passed(self):
        self.assertIsInstance(self.test.is_passed(user=self.user), bool)
        self.assertFalse(self.test.is_passed(user=self.user))
        self.assertTrue(self.test.is_passed(user=self.user_2))

    def test_get_statistics(self):
        with self.assertRaises(NoPassedTestError):
            self.test.get_statistics(self.user)

        statistics = self.test.get_statistics(self.user_2)
        self.assertIsNotNone(getattr(statistics, "user", None))
        self.assertEqual(statistics.user, self.user_2)

        self.assertIsNotNone(getattr(statistics, "test", None))
        self.assertEqual(statistics.test, self.test)

        self.assertIsNotNone(getattr(statistics, "questions", None))
        self.assertEqual(
            list(statistics.questions),
            [self.question, self.question_2],
        )

        self.assertIsNotNone(getattr(statistics, "correct_count", None))
        self.assertEqual(statistics.correct_count, 2)

        self.assertIsNotNone(getattr(statistics, "incorrect_count", None))
        self.assertEqual(statistics.incorrect_count, 0)
