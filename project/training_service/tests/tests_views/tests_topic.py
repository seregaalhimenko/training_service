import uuid

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import User

from training_service import models, serializers


class Test(APITestCase):
    def setUp(self) -> None:
        self.owner = User.objects.create(
            email="owner@test.com", password=uuid.uuid4().hex
        )
        self.token = Token.objects.get(user=self.owner)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_list(self):
        models.Topic.objects.create(
            title="Topic title", theory="Topic theory", owner=self.owner
        )
        models.Topic.objects.create(
            title="Topic title 2", theory="Topic theory 2", owner=self.owner
        )
        url = reverse("topic-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        topics = models.Topic.objects.all()
        self.assertEqual(
            response.data, serializers.TopicListSerializer(topics, many=True).data
        )

    def test_retrieve(self):
        topic = models.Topic.objects.create(
            title="Topic title", theory="Topic theory", owner=self.owner
        )
        url_topic = reverse("topic-detail", kwargs={"pk": topic.id})
        topic_2 = models.Topic.objects.create(
            title="Topic title 2", theory="Topic theory 2", owner=self.owner
        )
        url_topic_2 = reverse("topic-detail", kwargs={"pk": topic_2.id})
        response = self.client.get(url_topic)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.TopicSerializer(topic).data)
        self.assertEqual(
            response.data,
            {
                "id": 1,
                "test": None,
                "title": "Topic title",
                "theory": "Topic theory",
                "publication_date": "2023-04-03",
                "update_date": "2023-04-03",
                "owner": 1,
            },
        )

        response = self.client.get(url_topic_2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializers.TopicSerializer(topic_2).data)
        self.assertEqual(
            response.data,
            {
                "id": 2,
                "test": None,
                "title": "Topic title 2",
                "theory": "Topic theory 2",
                "publication_date": "2023-04-03",
                "update_date": "2023-04-03",
                "owner": 1,
            },
        )
