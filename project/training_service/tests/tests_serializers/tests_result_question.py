from collections import OrderedDict

from training_service import models, serializers
from training_service.tests import base


class Test(base.Base):
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

    def test_one(self):
        self.assertEqual(
            serializers.ResultQuestionSerializer(
                self.question,
                context={"user": self.user_2},
            ).data,
            {
                "id": 1,
                "text": "Question text",
                "correct": True,
                "answers": [
                    OrderedDict([("id", 1), ("text", "Answer_1"), ("correct", True)]),
                    OrderedDict([("id", 2), ("text", "Answer_2"), ("correct", False)]),
                ],
                "response_answers": [
                    OrderedDict([("id", 1), ("text", "Answer_1"), ("correct", True)])
                ],
            },
        )

    def test_many(self):
        self.assertEqual(
            serializers.ResultQuestionSerializer(
                self.test.questions.all(),
                many=True,
                context={"user": self.user_2},
            ).data,
            [
                OrderedDict(
                    [
                        ("id", 1),
                        ("text", "Question text"),
                        ("correct", True),
                        (
                            "answers",
                            [
                                OrderedDict(
                                    [("id", 1), ("text", "Answer_1"), ("correct", True)]
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
                                    [("id", 1), ("text", "Answer_1"), ("correct", True)]
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
                                    [("id", 3), ("text", "Answer_3"), ("correct", True)]
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
                                    [("id", 3), ("text", "Answer_3"), ("correct", True)]
                                )
                            ],
                        ),
                    ]
                ),
            ],
        )
