from training_service.tests.base import Base


class TestAnswerChoice(Base):
    def test__str__(self):
        answer = self.answer_choices[self.question][True]
        self.assertEqual(str(answer), answer.text)
