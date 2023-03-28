from django import forms
from django.contrib import admin

from training_service.models import Question

from .answer_choice import ChoiceInline


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = "__all__"


class QuestionAdmin(admin.ModelAdmin):
    form = QuestionForm
    inlines = [ChoiceInline]
    list_display = ["text", "test", "is_valid_question"]

    @admin.display(
        boolean=True,
        ordering="test",
        description="Does the question have 1 correct answer?",
    )
    def is_valid_question(self, question: Question):
        return question.is_valid_question()


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True
