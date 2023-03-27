from rest_framework import serializers

from training_service import models


class AnswerChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnswerChoice
        exclude = ["correct", "question"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerChoiceSerializer(many=True)

    class Meta:
        model = models.Question
        exclude = ["test"]


class TestSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = models.Test
        exclude = ["topic"]


class TopicSerializer(serializers.ModelSerializer):
    test = TestSerializer()

    class Meta:
        model = models.Topic
        fields = "__all__"


class TopicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Topic
        fields = ["id", "title"]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = "__all__"


class ResultAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AnswerChoice
        fields = ["id", "text", "correct"]


class ResponseHistorySerializer(serializers.ModelSerializer):
    answer_choice = ResultAnswerSerializer(label="response_answer")

    class Meta:
        model = models.ResponseHistory
        fields = ["user", "answer_choice"]


class ResultQuestionSerializer(serializers.ModelSerializer):
    answers = ResultAnswerSerializer(many=True)
    response_answers = serializers.SerializerMethodField()
    correct = serializers.SerializerMethodField()

    class Meta:
        model = models.Question
        fields = ["id", "text", "correct", "answers", "response_answers"]

    def get_response_answers(self, question: models.Question) -> dict:
        if not self.context.get("user"):
            raise ValueError("In 'self.context' there should be 'user'")
        answers = [
            x.answer_choice
            for x in question.response_history.filter(
                user=self.context.get("user")
            ).all()
        ]
        return ResultAnswerSerializer(answers, many=True).data

    def get_correct(self, question: models.Question) -> bool:
        if not self.context.get("user"):
            raise ValueError("In 'self.context' there should be 'user'")
        return question.is_correct(user=self.context.get("user"))


class StatisticsSerializer(serializers.Serializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    test = serializers.PrimaryKeyRelatedField(read_only=True)
    questions = serializers.SerializerMethodField()
    correct_count = serializers.IntegerField()
    incorrect_count = serializers.IntegerField()

    def get_questions(self, instance) -> bool:
        return ResultQuestionSerializer(
            instance.questions,
            many=True,
            context={"user": instance.user},
        ).data
