import uuid

from django.test import TestCase
from users.models import User

from training_service.models import AnswerChoice, Question, Test, Topic


class CreateAnswerChoiceMixin:
    count_answer = 0

    @classmethod
    def create_answer_choice(
        cls,
        *,
        text: str | None = None,
        question: Question | None = None,
        correct: bool,
    ) -> AnswerChoice:
        cls.count_answer += 1
        return AnswerChoice.objects.create(
            text=text or f"Answer_{cls.count_answer}",
            question=question or cls.question,
            correct=correct,
        )


class PreBase(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.count_answer = 0
        cls.owner = User.objects.create(
            email="owner@test.com", password=uuid.uuid4().hex
        )
        cls.user = User.objects.create(
            email="test@test.com",
            password=uuid.uuid4().hex,
        )
        cls.user_2 = User.objects.create(
            email="Bob@test.com", password=uuid.uuid4().hex
        )
        cls.topic = Topic.objects.create(
            title="Topic title", theory="Topic theory", owner=cls.owner
        )
        cls.test = Test.objects.create(title="Test title", topic=cls.topic)

        cls.question = Question.objects.create(text="Question text", test=cls.test)
        cls.question_2 = Question.objects.create(text="Question2 text", test=cls.test)


class Base(PreBase, CreateAnswerChoiceMixin):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.answer_choices = {
            cls.question: {
                True: cls.create_answer_choice(correct=True),
                False: cls.create_answer_choice(correct=False),
            },
            cls.question_2: {
                True: cls.create_answer_choice(question=cls.question_2, correct=True),
                False: cls.create_answer_choice(question=cls.question_2, correct=False),
            },
        }
