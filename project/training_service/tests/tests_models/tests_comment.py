from training_service.models import Comment
from training_service.tests.base import PreBase


class TestComment(PreBase):
    def test__str__(self):
        comment = Comment.objects.create(question=self.question, text="Comment text")
        self.assertEqual(str(comment), comment.text)
        self.assertEqual(str(comment), "Comment text")
