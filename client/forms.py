from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'nom', 'prenom', 'societe', 'telephone',
            'adresse', 'ville',
            'idf', 'rc', 'ice'
        ]
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }
