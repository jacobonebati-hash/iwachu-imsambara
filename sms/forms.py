from django import forms

from members.models import Member
from .models import SMSMessage


class SMSForm(forms.ModelForm):

    recipients = forms.ModelMultipleChoiceField(
        queryset=Member.objects.filter(status=True),
        widget=forms.SelectMultiple(
            attrs={
                "class": "form-select",
                "size": "10"
            }
        )
    )

    class Meta:
        model = SMSMessage
        fields = ["message"]

        widgets = {
            "message": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 6,
                    "placeholder": "Andika ujumbe wako hapa..."
                }
            )
        }