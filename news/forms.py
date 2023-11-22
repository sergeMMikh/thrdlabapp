from .models import Articles
from django.forms import ModelForm, TextInput, DateInput, Textarea


class ArticlesForm(ModelForm):
    class Meta:
        model = Articles
        # fields = ['title', 'anons', 'full_text', 'date']
        fields = ('__all__')

        widgets = {
            "title": TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Title',
                },
            ),
            "anons": TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Date',
                },
            ),
            "full_text": Textarea(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Text of article',
                },
            ),
            "date": DateInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Publishing Data',
                },
            ),
        }
