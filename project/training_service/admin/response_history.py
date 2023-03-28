from django.contrib import admin

from training_service.models import ResponseHistory


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

    @admin.display(ordering="user", description="user")
    def get_user(self, obj: ResponseHistory):
        return obj.user

    @admin.display(ordering="answer_choice", description="answer_choice")
    def get_answer_choice(self, obj: ResponseHistory):
        return obj.answer_choice

    @admin.display(boolean=True, ordering="answer_choice", description="correct")
    def get_answer_choice_correct(self, obj: ResponseHistory) -> bool:
        return obj.answer_choice.correct

    @admin.display(ordering="question", description="question")
    def get_question(self, obj: ResponseHistory):
        return obj.question

    @admin.display(ordering="question", description="test")
    def get_test(self, obj: ResponseHistory):
        return obj.question.test

    @admin.display(
        boolean=True, ordering="question", description="was the test passed?"
    )
    def get_is_passed_test(self, obj: ResponseHistory) -> bool:
        return obj.question.test.is_passed(obj.user)

    @admin.display(
        boolean=True, ordering="question", description="is the question correct?"
    )
    def get_is_correct_question(self, obj: ResponseHistory) -> bool:
        return obj.question.is_correct(user=obj.user)
