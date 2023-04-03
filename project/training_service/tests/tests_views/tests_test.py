from collections import OrderedDict

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from training_service import models, serializers

from . import base


class Test(base.BaseTestAPI):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()

    def setUp(self) -> None:
        super().setUp()
        self.response_history = {
            self.user: {
                self.question: models.ResponseHistory.objects.create(
                    user=self.user,
                    question=self.question,
                    answer_choice=self.answer_choices[self.question][False],
                )
            },
            self.user_2: {
                self.question: models.ResponseHistory.objects.create(
                    user=self.user_2,
                    answer_choice=self.answer_choices[self.question][True],
                    question=self.question,
                ),
                self.question_2: models.ResponseHistory.objects.create(
                    user=self.user_2,
                    answer_choice=self.answer_choices[self.question_2][True],
                    question=self.question_2,
                ),
            },
        }

    def test_retrieve_redirect(self):
        topic = models.Topic.objects.create(
            title="Topic title", theory="Topic theory", owner=self.owner
        )
        test = models.Test.objects.create(title="Test title", topic=topic)
        question = models.Question.objects.create(text="Question text", test=test)
        models.AnswerChoice.objects.create(text="text", question=question, correct=True)
        url = reverse("test-detail", kwargs={"pk": test.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def test_retrieve_(self):
        url = reverse("test-detail", kwargs={"pk": self.test.id})
        user_token = Token.objects.get(user=self.user_2)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + user_token.key)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            serializers.StatisticsSerializer(
                self.test.get_statistics(self.user_2)
            ).data,
        )
        self.assertEqual(
            response.data,
            {
                "user": 3,
                "test": 1,
                "questions": [
                    OrderedDict(
                        [
                            ("id", 1),
                            ("text", "Question text"),
                            ("correct", True),
                            (
                                "answers",
                                [
                                    OrderedDict(
                                        [
                                            ("id", 1),
                                            ("text", "Answer_1"),
                                            ("correct", True),
                                        ]
                                    ),
                                    OrderedDict(
                                        [
                                            ("id", 2),
                                            ("text", "Answer_2"),
                                            ("correct", False),
                                        ]
                                    ),
                                ],
                            ),
                            (
                                "response_answers",
                                [
                                    OrderedDict(
                                        [
                                            ("id", 1),
                                            ("text", "Answer_1"),
                                            ("correct", True),
                                        ]
                                    )
                                ],
                            ),
                        ]
                    ),
                    OrderedDict(
                        [
                            ("id", 2),
                            ("text", "Question2 text"),
                            ("correct", True),
                            (
                                "answers",
                                [
                                    OrderedDict(
                                        [
                                            ("id", 3),
                                            ("text", "Answer_3"),
                                            ("correct", True),
                                        ]
                                    ),
                                    OrderedDict(
                                        [
                                            ("id", 4),
                                            ("text", "Answer_4"),
                                            ("correct", False),
                                        ]
                                    ),
                                ],
                            ),
                            (
                                "response_answers",
                                [
                                    OrderedDict(
                                        [
                                            ("id", 3),
                                            ("text", "Answer_3"),
                                            ("correct", True),
                                        ]
                                    )
                                ],
                            ),
                        ]
                    ),
                ],
                "correct_count": 2,
                "incorrect_count": 0,
            },
        )
