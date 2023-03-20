from rest_framework import serializers

from . import models


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
    test = TestSerializer()  # read_only=True

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
