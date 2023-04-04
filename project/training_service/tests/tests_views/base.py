from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from training_service.tests import base


class BaseTestAPI(APITestCase, base.Base):
    @classmethod
    def setUpTestData(cls) -> None:
        super().setUpTestData()
        cls.token = Token.objects.get(user=cls.owner)

    def setUp(self) -> None:
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
