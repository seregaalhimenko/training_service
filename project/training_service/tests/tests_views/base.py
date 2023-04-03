import uuid

# from django.urls import reverse
# from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from users.models import User

# from training_service import models, serializers
from training_service.tests import base


class BaseTestAPI(APITestCase, base.Base):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.token = Token.objects.get(user=cls.owner)

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
