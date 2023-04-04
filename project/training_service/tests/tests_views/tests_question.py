from django.core.exceptions import ValidationError
from django.urls import reverse
from rest_framework import status

from training_service import models, serializers

from . import base


class Test(base.BaseTestAPI):
    def test_retrieve(self):
        url = reverse("question-detail", kwargs={"pk": self.question.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, serializers.QuestionSerializer(self.question).data
        )

        url = reverse("question-detail", kwargs={"pk": self.question_2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, serializers.QuestionSerializer(self.question_2).data
        )

    def test_set_answer_false_correct_no_comments(self):
        url = reverse("question-set-answer", kwargs={"pk": self.question.id})
        data = {"ids": [1, 2]}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {"answer": False, "comment": {"details": "Not found."}},
        )

    def test_set_answer_false_correct(self):
        comment = models.Comment.objects.create(
            text="Coment text", question=self.question
        )
        url = reverse("question-set-answer", kwargs={"pk": self.question.id})
        data = {"ids": [1, 2]}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "answer": False,
                "comment": {
                    "id": comment.id,
                    "text": "Coment text",
                    "question": comment.question.id,
                },
            },
        )

    def test_set_answer_true_correct(self):
        models.Comment.objects.create(text="Coment text", question=self.question)
        url = reverse("question-set-answer", kwargs={"pk": self.question.id})
        data = {"ids": [1, 4]}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"answer": True})

    def test_set_answer_empty(self):
        models.Comment.objects.create(text="Coment text", question=self.question)
        url = reverse("question-set-answer", kwargs={"pk": self.question.id})
        data = {"ids": []}
        with self.assertRaises(ValidationError):
            self.client.post(url, data=data, format="json")
