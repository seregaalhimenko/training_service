from django.contrib import admin

from .models import AnswerChoice, Comment, Question, ResponseHistory, Test, Topic

admin.site.register(Topic)
admin.site.register(Test)
admin.site.register(Question)
admin.site.register(AnswerChoice)
admin.site.register(Comment)
admin.site.register(ResponseHistory)
