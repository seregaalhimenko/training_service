from django.urls import path
from rest_framework import routers

from . import views

router = routers.SimpleRouter()
urlpatterns = [
    path("questions/<int:question_id>/", views.QuestionController.as_view()),
]

router.register(
    r"topics",
    views.TopicController,
    basename="topic",
)
urlpatterns += router.urls
