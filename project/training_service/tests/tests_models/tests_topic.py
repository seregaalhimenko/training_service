import uuid

from django.test import TestCase
from users.models import User

from training_service.models import Topic


class TestTopic(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.owner = User.objects.create(
            email="owner@test.com", password=uuid.uuid4().hex
        )

    def test__str__(self):
        topic = Topic.objects.create(
            title="Topic title", theory="Topic theory", owner=self.owner
        )
        self.assertEqual(str(topic), topic.title)
        self.assertEqual(str(topic), "Topic title")
