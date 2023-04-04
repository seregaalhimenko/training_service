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
                "answers": serializers.ResultAnswerSerializer(
                    self.question.answers.all(), many=True
                ).data,
                "response_answers": serializers.ResultAnswerSerializer(
                    self.question.response_answers.get(user=self.user).answer_choice,
                ).data,
            },
        )
