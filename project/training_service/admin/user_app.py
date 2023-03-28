from django.contrib import admin
from users.admin import CustomUserAdmin

from training_service import serializers
from training_service.models import Test


class UserAppAdmin(CustomUserAdmin):
    readonly_fields = ["get_passed_count_test"]
    fieldsets = (
        *CustomUserAdmin.fieldsets,
        ("Statistis Test", {"fields": ("get_passed_count_test",)}),
    )

    # todo: refactoring or delete
    @admin.display(ordering="email", description="passed test")
    def get_passed_count_test(self, instance) -> str:
        user = instance
        rh_user = user.response_history
        test_ids = rh_user.values_list("question__test__id").distinct()
        tests = Test.objects.filter(pk__in=test_ids)
        string = ""
        for test in tests:
            if test.is_passed(user):
                test.get_statistics(user)
                statistics_test = serializers.StatisticsSerializer(
                    test.get_statistics(user)
                ).data
                questions = statistics_test.get("questions")
                questions_string = ""
                for question in questions:
                    answers_string = ", ".join([x["text"] for x in question["answers"]])
                    response_answers_string = ", ".join(
                        [x["text"] for x in question["response_answers"]]
                    )
                    correct_string = "{}".format(
                        "верный" if question["correct"] else "неверный"
                    )
                    questions_string += "\n--Вопрос: {}\n \
                        ---Варианты ответа: {}\n \
                        ---Полученный ответ: {}\n \
                        ---Ответ на вопрос: {}\n".format(
                        question["text"],
                        answers_string,
                        response_answers_string,
                        correct_string,
                    )
                test_string = "test:{}\n \
                    -question: {}\n \
                    -correct_count: {}\n \
                    -incorrect_count: {}\n\n\n\n \
                    ".format(
                    test.title,
                    questions_string,
                    statistics_test["correct_count"],
                    statistics_test["incorrect_count"],
                )
                string = string + test_string
        return string
