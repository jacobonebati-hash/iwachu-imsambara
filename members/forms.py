from django import forms
from .models import Member


class MemberForm(forms.ModelForm):

    class Meta:
        model = Member

        fields = [
            'jina',
            'simu',
            'kitongoji',
            'jinsia',
            'status',
        ]

        widgets = {

            'jina': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Andika jina kamili'
            }),

            'simu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mfano: 0712345678'
            }),

            'kitongoji': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Andika kitongoji'
            }),

            'jinsia': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Mfano: Male / Female'
            }),

            'status': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }