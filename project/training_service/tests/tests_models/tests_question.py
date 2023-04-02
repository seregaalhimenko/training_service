import uuid
from itertools import combinations_with_replacement

from django.contrib.auth import get_user_model
from django.test import TestCase
from users.models import User

from training_service.models import AnswerChoice, Question, ResponseHistory, Test, Topic
from training_service.tests.base import CreateAnswerChoiceMixin


class TestQuestion(TestCase, CreateAnswerChoiceMixin):
    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create(
            email="test_owner@test.com", password=uuid.uuid4().hex
        )
        cls.user: User = get_user_model().objects.create(
            email="test_user", password=uuid.uuid4().hex
        )
        cls.topic = Topic.objects.create(
            title="Test title",
            theory="Test theory",
            owner=cls.owner,
        )
        cls.test = Test.objects.create(title="Test title", topic=cls.topic)

    def setUp(self) -> None:
        self.question = Question.objects.create(text="test text", test=self.test)
        self.count_answer = 0

    def create_answer_choice(
        self,
        *,
        text: str | None = None,
        question: Question | None = None,
        correct: bool,
    ) -> AnswerChoice:
        return super().create_answer_choice(
            question=question or self.question, correct=correct
        )

    def create_response_history(
        self,
        *,
        answer_choice: AnswerChoice,
        question: Question | None = None,
        user: User | None = None,
    ) -> ResponseHistory:
        return ResponseHistory.objects.create(
            answer_choice=answer_choice,
            user=user or self.user,
            question=question or self.question,
        )

    def test__str__(self):
        self.assertEqual(str(self.question), "test text")

    def test_get_by_id(self):
        question = Question.get_by_id(id=self.question.id)
        self.assertEqual(question, self.question)

    def test_is_valid_question(self):
        self.assertFalse(self.question.is_valid())
        self.create_answer_choice(correct=False)
        self.create_answer_choice(correct=False)
        self.assertFalse(self.question.is_valid())
        self.create_answer_choice(correct=True)
        self.assertTrue(self.question.is_valid())

    def test_get_valid_questions(self):
        Question.objects.create(text="test text2", test=self.test)
        Question.objects.create(text="test text3", test=self.test)
        self.create_answer_choice(correct=False)
        self.create_answer_choice(correct=True)
        self.assertEqual(
            Question.get_valid_questions(Question.objects.all()), (self.question,)
        )

    def test_get_answers_by_ids(self):
        answer_1 = self.create_answer_choice(correct=False)
        answer_2 = self.create_answer_choice(correct=True)
        self.create_answer_choice(correct=True)
        self.assertEqual(
            list(self.question.get_answers_by_ids([answer_1.id, answer_2.id])),
            [answer_1, answer_2],
        )

    def test_create_history(self):
        answer_choice = self.create_answer_choice(correct=False)
        self.create_answer_choice(correct=True)
        self.question.create_history(answer_choice, self.user)
        self.assertTrue(ResponseHistory.objects.count() == 1)

    def test_get_user_responses(self):
        answer_choice = self.create_answer_choice(correct=False)
        self.create_answer_choice(correct=True)
        self.question.create_history(answer_choice, self.user)
        user_responses = self.question.get_user_responses(user=self.user)
        response_history = ResponseHistory.objects.filter(
            user=self.user, question=self.question
        )
        self.assertEqual(list(user_responses), list(response_history))

    def test_get_answers(self):
        self.create_answer_choice(correct=False)
        self.create_answer_choice(correct=True)
        self.assertEqual(
            list(self.question.get_answers()),
            list(AnswerChoice.objects.filter(question=self.question)),
        )

    def test_is_correct_with_request_answers(self):
        with self.assertRaises(ValueError):
            self.question.is_correct()
        answer_1 = self.create_answer_choice(correct=False)
        answer_2 = self.create_answer_choice(correct=True)
        self.assertFalse(
            self.question.is_correct(
                request_answers=AnswerChoice.objects.filter(id=answer_1.id)
            )
        )
        self.assertTrue(
            self.question.is_correct(
                request_answers=AnswerChoice.objects.filter(id=answer_2.id)
            )
        )
        answer_3 = self.create_answer_choice(correct=False)
        answer_4 = self.create_answer_choice(correct=True)
        answer_ids = (answer_1.id, answer_2.id, answer_3.id, answer_4.id)
        full_combinations = combinations_with_replacement(answer_ids, 4)
        combinations = {frozenset(x) for x in full_combinations}
        combinations.discard({answer_2.id, answer_4.id})
        for ids in combinations:
            self.assertFalse(
                self.question.is_correct(
                    request_answers=AnswerChoice.objects.filter(pk__in=ids)
                )
            )
        self.assertTrue(
            self.question.is_correct(
                request_answers=AnswerChoice.objects.filter(
                    pk__in=[answer_2.id, answer_4.id]
                )
            )
        )

    def test_is_correct_without_request_answers(self):
        with self.assertRaises(ValueError):
            self.question.is_correct()
        answer_1 = self.create_answer_choice(correct=False)
        answer_2 = self.create_answer_choice(correct=True)
        self.create_response_history(answer_choice=answer_1)
        self.assertFalse(self.question.is_correct(user=self.user))
        ResponseHistory.objects.all().delete()
        self.create_response_history(answer_choice=answer_2)
        self.assertTrue(self.question.is_correct(user=self.user))
