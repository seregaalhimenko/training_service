from django.contrib import admin

from .question import QuestionInline


class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ["title", "publication_date", "update_date"]
