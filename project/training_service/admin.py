from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from .config import EXCEPTION_CREATE_CORRECT_ANSWERS_FIRST_FOR_QUESTION
from .models import AnswerChoice, Comment, Question, ResponseHistory, Test, Topic


class AnswerChoicForm(forms.ModelForm):
    class Meta:
        model = AnswerChoice
        fields = "__all__"


class ChoiceInline(admin.TabularInline):
    model = AnswerChoice
    form = AnswerChoicForm
    extra = 1


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
    def is_valid_question(self, obj):
        return obj.is_valid_question()

    def save_related(self, request, form, formsets, change):
        if EXCEPTION_CREATE_CORRECT_ANSWERS_FIRST_FOR_QUESTION:
            answer_choice_formsets = formsets[0]
            corrects = [x.get("correct") for x in answer_choice_formsets.cleaned_data]
            if not any(corrects):
                raise ValidationError(
                    message="There are no correct answers to this question, add the correct answer first."
                )
        super().save_related(request, form, formsets, change)


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    show_change_link = True


class TestAdmin(admin.ModelAdmin):
    inlines = [QuestionInline]
    list_display = ["title", "publication_date", "update_date"]


class AnswerChoiceAdmin(admin.ModelAdmin):
    form = AnswerChoicForm
    list_display = [
        "text",
        "question",
        "question_id",
        "correct",
    ]


class ResponseHistoryAdmin(admin.ModelAdmin):
    list_display = [
        "get_user",
        "get_test",
        "get_question",
        "get_is_correct_question",
        "get_answer_choice",
        "get_answer_choice_correct",
        "get_is_passed_test",
    ]
    list_filter = ["user"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    @admin.display(ordering="user", description="user")
    def get_user(self, obj):
        return obj.user

    @admin.display(ordering="answer_choice", description="answer_choice")
    def get_answer_choice(self, obj):
        return obj.answer_choice

    @admin.display(boolean=True, ordering="answer_choice", description="correct")
    def get_answer_choice_correct(self, obj):
        return obj.answer_choice.correct

    @admin.display(ordering="question", description="question")
    def get_question(self, obj):
        return obj.question

    @admin.display(ordering="question", description="test")
    def get_test(self, obj):
        return obj.question.test

    @admin.display(
        boolean=True, ordering="question", description="was the test passed?"
    )
    def get_is_passed_test(self, obj):
        return obj.question.test.is_passed(obj.user)

    @admin.display(
        boolean=True, ordering="question", description="is the question correct?"
    )
    def get_is_correct_question(self, obj):
        return obj.question.is_correct(user=obj.user)


admin.site.register(Topic)
admin.site.register(Test, TestAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(AnswerChoice, AnswerChoiceAdmin)
admin.site.register(Comment)
admin.site.register(ResponseHistory, ResponseHistoryAdmin)
