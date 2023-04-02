from django.conf import settings
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from . import models, serializers


class QuestionController:
    def __call__(self, data, user: settings.AUTH_USER_MODEL, question_id: int):
        question: models.Question = models.Question.get_by_id(question_id)
        # todo: проверка на пустой ответ
        if self.get_response_history(user, question):
            return {"details": _("You have already answered this question")}

        if not question.is_valid():
            return {"details": _("The question has no right answers")}

        request_answers = question.get_answers_by_ids(data.get("ids"))
        self.create_answers_user(user, request_answers, question)

        if question.test.is_passed(user):
            send_mail(
                "statistics",
                str(question.test.get_statistics(user)),
                settings.EMAIL_HOST_USER,
                [user.email],
            )

        if question.is_correct(request_answers=request_answers):
            return {"answer": True}
        comment = self.get_comment(question)
        return {"answer": False, "comment": comment}

    def get_comment(self, question: models.Question) -> dict:
        try:
            comment = question.comment
        except models.Comment.DoesNotExist:
            return {"details": _("Not found.")}
        return serializers.CommentSerializer(comment).data

    def get_response_history(
        self, user: settings.AUTH_USER_MODEL, question: models.Question
    ):
        return models.ResponseHistory.get_history_user_by_question(
            question=question,
            user=user,
        )

    def create_answers_user(
        self,
        user: settings.AUTH_USER_MODEL,
        request_answers: list[models.AnswerChoice],
        question: models.Question,
    ) -> None:
        for answer in request_answers:
            question.create_history(answer, user)


question_controller = QuestionController()

#       Внедрение потерна State. Была идея разбить функцию контроллера на отдельные состояния для удобочитаемости
#       но к сожалению сложность и объем кода увеличились больше чем читаемость
#
#   (рабочий вариант но совсем тут не нужный)
# from django.conf import settings
# from django.core.mail import send_mail
# from django.utils.translation import gettext_lazy as _

# from . import models, serializers


# class AbstractState:
#     _next_state: "AbstractState"

#     def __init__(
#         self,
#         data: dict,
#         user: settings.AUTH_USER_MODEL,
#         question: models.Question,
#         request_answers,
#     ) -> None:
#         self.data: dict = data
#         self.request_answers = request_answers
#         self.user: settings.AUTH_USER_MODEL = user
#         self.question: models.Question = question

#     def __get_insides(self):
#         return {
#             "data": self.data,
#             "request_answers": self.request_answers,
#             "user": self.user,
#             "question": self.question,
#         }

#     def get_next_state(self):
#         if not self._next_state:
#             return None
#         return self._next_state(**self.__get_insides())


# class CommentState(AbstractState):
#     _next_state = None

#     def handle(self):
#         try:
#             comment = self.question.comment
#         except models.Comment.DoesNotExist:
#             return {"details": "Not found."}
#         return {"answer": False, "comment": serializers.CommentSerializer(comment).data}


# class CheckAnswerState(AbstractState):
#     _next_state = CommentState

#     def handle(self):
#         if self.question.is_correct(request_answers=self.request_answers):
#             return {"answer": True}


# class IsPassedTestSate(AbstractState):
#     _next_state = CheckAnswerState

#     def handle(self):
#         if self.question.test.is_passed(self.user):  # проверить пройден ли тест
#             send_mail(
#                 "statistics",
#                 str(self.question.test.get_statistics(self.user)),
#                 settings.EMAIL_HOST_USER,
#                 [self.user.email],
#             )


# class AddResponeHistoryState(AbstractState):
#     _next_state = IsPassedTestSate

#     def handle(self):
#         for answer in self.request_answers:
#             self.question.create_history(answer, self.user)
#         return None


# class CheckValidTestState(AbstractState):
#     _next_state = AddResponeHistoryState

#     def handle(self):
#         if not self.question.is_valid():
#             return {"answers": _("The question has no right answers")}
#         return None


# class IsPassedQuestionState(AbstractState):
#     _next_state = CheckValidTestState

#     def handle(self):
#         if self.get_response_history():  # docs отвечал или нет?
#             return {"details": "you have already answered this question"}
#         return None

#     def get_response_history(self):
#         return models.ResponseHistory.get_history_user_by_question(
#             question=self.question,
#             user=self.user,
#         )


# class QuestionController:
#     _state = None

#     def handle(self, data, user: settings.AUTH_USER_MODEL, question_id: int):
#         question: models.Question = models.Question.get_by_id(question_id)
#         request_answers = question.get_answers_by_ids(data.get("ids"))
#         self._state = IsPassedQuestionState(
#             data=data,
#             request_answers=request_answers,
#             user=user,
#             question=question,
#         )
#         while not (result := self._state.handle()):
#             self._state = self._state.get_next_state()
#         return result
