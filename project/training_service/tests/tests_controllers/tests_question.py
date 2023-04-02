from django.db import models

from training_service.controllers import question_controller
from training_service.models import Comment, Question, ResponseHistory
from training_service.serializers import CommentSerializer
from training_service.tests.base import Base


class Test(Base):
    def setUp(self) -> None:
        self.response_history = {
            self.user: {
                self.question: ResponseHistory.objects.create(
                    user=self.user,
                    question=self.question,
                    answer_choice=self.answer_choices[self.question][False],
                )
            },
            self.user_2: {
                self.question: ResponseHistory.objects.create(
                    user=self.user_2,
                    answer_choice=self.answer_choices[self.question][True],
                    question=self.question,
                ),
                self.question_2: ResponseHistory.objects.create(
                    user=self.user_2,
                    answer_choice=self.answer_choices[self.question_2][True],
                    question=self.question_2,
                ),
            },
        }

    def test__call__(self):
        question = Question.objects.create(text="new question text", test=self.test)
        self.assertEqual(
            question_controller([1, 2, 3], self.user, question.id),
            {"details": "The question has no right answers"},
        )
        answers = [
            self.create_answer_choice(question=question, correct=True).id,
            self.create_answer_choice(question=question, correct=False).id,
        ]
        data = {"ids": answers[1:]}

        self.assertEqual(
            question_controller(data, self.user, question.id),
            {"answer": False, "comment": {"details": "Not found."}},
        )
        self.assertEqual(
            question_controller(data, self.user, question.id),
            {"details": "You have already answered this question"},
        )
        ResponseHistory.objects.filter(user=self.user, question=question).delete()

        comment = Comment.objects.create(text="test Comment text", question=question)
        self.assertEqual(
            question_controller(data, self.user, question.id),
            {
                "answer": False,
                "comment": CommentSerializer(comment).data,
            },
        )
        ResponseHistory.objects.filter(user=self.user, question=question).delete()

        data = {"ids": answers[:1]}
        self.assertEqual(
            question_controller(data, self.user, question.id),
            {"answer": True},
        )
        ResponseHistory.objects.filter(user=self.user, question=question).delete()

        data = {"ids": answers}
        self.assertEqual(
            question_controller(data, self.user, question.id),
            {
                "answer": False,
                "comment": CommentSerializer(comment).data,
            },
        )

    def test_get_comment(self):
        self.assertEqual(
            question_controller.get_comment(self.question), {"details": "Not found."}
        )
        comment = Comment.objects.create(text="text", question=self.question)
        self.assertEqual(
            question_controller.get_comment(self.question),
            CommentSerializer(comment).data,
        )
        self.assertEqual(
            question_controller.get_comment(self.question),
            {"id": 1, "text": "text", "question": 1},
        )

    def test_get_response_history(self):
        self.response_history_obj = question_controller.get_response_history(
            user=self.user, question=self.question
        )
        self.assertIsInstance(self.response_history_obj, models.QuerySet)
        self.assertEqual(
            list(self.response_history_obj),
            [self.response_history[self.user][self.question]],
        )
        self.assertEqual(
            list(self.response_history_obj),
            list(
                ResponseHistory.get_history_user_by_question(
                    user=self.user, question=self.question
                )
            ),
        )
        self.assertEqual(
            list(
                question_controller.get_response_history(
                    user=self.user_2, question=self.question
                )
            ),
            [self.response_history[self.user_2][self.question]],
        )
        self.assertEqual(
            list(
                question_controller.get_response_history(
                    user=self.user_2, question=self.question
                )
            ),
            list(
                ResponseHistory.get_history_user_by_question(
                    user=self.user_2, question=self.question
                )
            ),
        )
        self.assertEqual(
            list(
                question_controller.get_response_history(
                    user=self.user_2, question=self.question_2
                )
            ),
            [self.response_history[self.user_2][self.question_2]],
        )
        self.assertEqual(
            list(
                question_controller.get_response_history(
                    user=self.user_2, question=self.question_2
                )
            ),
            list(
                ResponseHistory.get_history_user_by_question(
                    user=self.user_2, question=self.question_2
                )
            ),
        )

    def test_create_answers_user(self):
        question = Question.objects.create(text="new question text", test=self.test)
        answers = [
            self.create_answer_choice(question=question, correct=True),
            self.create_answer_choice(question=question, correct=False),
            self.create_answer_choice(question=question, correct=False),
            self.create_answer_choice(question=question, correct=True),
        ]
        request_answers = answers[1:3]
        question_controller.create_answers_user(
            user=self.user,
            request_answers=request_answers,
            question=question,
        )
        self.assertEqual(
            request_answers,
            [
                obj.answer_choice
                for obj in ResponseHistory.objects.filter(
                    user=self.user, question=question
                ).all()
            ],
        )
