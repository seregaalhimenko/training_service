from django.contrib import admin
from django.contrib.auth import get_user_model

from training_service.models import (
    AnswerChoice,
    Comment,
    Question,
    ResponseHistory,
    Test,
    Topic,
)

from . import answer_choice, question, response_history, test, user_app

User = get_user_model()
admin.site.unregister(User)
admin.site.register(User, user_app.UserAppAdmin)
admin.site.register(Topic)
admin.site.register(Test, test.TestAdmin)
admin.site.register(Question, question.QuestionAdmin)
admin.site.register(AnswerChoice, answer_choice.AnswerChoiceAdmin)
admin.site.register(Comment)
admin.site.register(ResponseHistory, response_history.ResponseHistoryAdmin)
