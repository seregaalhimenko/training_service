from django import forms
from django.contrib import admin

from training_service.models import AnswerChoice


class AnswerChoiceForm(forms.ModelForm):
    class Meta:
        model = AnswerChoice
        fields = "__all__"


class ChoiceInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        corrects = [x.cleaned_data.get("correct") for x in self.forms]
        if not any(corrects):
            raise forms.ValidationError(
                message="There are no correct answers to this question, add the correct answer first."
            )


class ChoiceInline(admin.TabularInline):
    model = AnswerChoice
    form = AnswerChoiceForm
    formset = ChoiceInlineFormset
    extra = 1


class AnswerChoiceAdmin(admin.ModelAdmin):
    form = AnswerChoiceForm
    list_display = [
        "text",
        "question",
        "question_id",
        "correct",
    ]
