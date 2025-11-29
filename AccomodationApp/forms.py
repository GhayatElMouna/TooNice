from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    note = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'min': '1',
            'max': '5',
            'step': '1',
            'class': 'form-range',
            'id': 'noteRange'
        }),
        label='Note (sur 5 étoiles)',
        help_text='Sélectionnez une note de 1 à 5 étoiles',
        min_value=1,
        max_value=5
    )
    
    commentaire = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Partagez votre expérience...',
            'maxlength': 500
        }),
        label='Commentaire (optionnel)',
        required=False,
        max_length=500
    )
    
    class Meta:
        model = Note
        fields = ['note', 'commentaire']

