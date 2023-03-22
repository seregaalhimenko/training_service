from rest_framework import routers

from . import views

router = routers.SimpleRouter()

router.register(
    r"questions",
    views.QuestionView,
    basename="question",
)

router.register(
    r"topics",
    views.TopicView,
    basename="topic",
)
router.register(
    r"tests",
    views.TestView,
    basename="test",
)
urlpatterns = router.urls
