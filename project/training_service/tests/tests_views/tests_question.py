from collections import OrderedDict

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
        self.assertEqual(
            response.data,
            {
                "id": 1,
                "answers": [
                    OrderedDict([("id", 1), ("text", "Answer_1")]),
                    OrderedDict([("id", 2), ("text", "Answer_2")]),
                ],
                "text": "Question text",
            },
        )

        url = reverse("question-detail", kwargs={"pk": self.question_2.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data, serializers.QuestionSerializer(self.question_2).data
        )
        self.assertEqual(
            response.data,
            {
                "id": 2,
                "answers": [
                    OrderedDict([("id", 3), ("text", "Answer_3")]),
                    OrderedDict([("id", 4), ("text", "Answer_4")]),
                ],
                "text": "Question2 text",
            },
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
        models.Comment.objects.create(text="Coment text", question=self.question)
        url = reverse("question-set-answer", kwargs={"pk": self.question.id})
        data = {"ids": [1, 2]}
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "answer": False,
                "comment": {"id": 1, "text": "Coment text", "question": 1},
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
