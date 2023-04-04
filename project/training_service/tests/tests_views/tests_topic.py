import uuid
from datetime import datetime

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import User

from training_service import models, serializers

from . import base


class TestShortTopic(APITestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create(
            email="owner@test.com", password=uuid.uuid4().hex
        )
        self.token = Token.objects.get(user=self.owner)

        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        self.topic = models.Topic.objects.create(
            title="Topic title", theory="Topic theory", owner=self.owner
        )
        self.topic_2 = models.Topic.objects.create(
            title="Topic title 2", theory="Topic theory 2", owner=self.owner
        )

    def test_list(self):
        url = reverse("topic-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        topics = models.Topic.objects.all()
        self.assertEqual(
            response.data, serializers.TopicListSerializer(topics, many=True).data
        )

    def test_retrieve(self):
        url_topic = reverse("topic-detail", kwargs={"pk": self.topic.id})
        url_topic_2 = reverse("topic-detail", kwargs={"pk": self.topic_2.id})
        response = self.client.get(url_topic)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.TopicSerializer(self.topic).data)
        self.assertEqual(
            response.data,
            {
                "id": self.topic.id,
                "test": None,
                "title": "Topic title",
                "theory": "Topic theory",
                "publication_date": f"{datetime.now().date()}",
                "update_date": f"{datetime.now().date()}",
                "owner": self.owner.id,
            },
        )

        response = self.client.get(url_topic_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.TopicSerializer(self.topic_2).data)
        self.assertEqual(
            response.data,
            {
                "id": self.topic.id,
                "test": None,
                "title": "Topic title 2",
                "theory": "Topic theory 2",
                "publication_date": f"{datetime.now().date()}",
                "update_date": f"{datetime.now().date()}",
                "owner": self.owner.id,
            },
        )


class TestTopic(base.BaseTestAPI):
    def test_retrieve(self):
        url_topic = reverse("topic-detail", kwargs={"pk": self.topic.id})
        response = self.client.get(url_topic)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.TopicSerializer(self.topic).data)
