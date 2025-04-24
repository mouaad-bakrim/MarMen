from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'nom', 'prenom', 'societe', 'email', 'telephone',
            'adresse', 'ville', 'code_postal', 'pays',
            'numero_identification_fiscale', 'registre_commerce', 'site_web'
        ]
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }
