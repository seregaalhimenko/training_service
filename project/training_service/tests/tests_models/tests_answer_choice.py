from training_service.tests.base import Base


class CommentTopic(Base):
    def test__str__(self):
        answer = self.answer_choices[self.question][True]
        self.assertEqual(str(answer), answer.text)
