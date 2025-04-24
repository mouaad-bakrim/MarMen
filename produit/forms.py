from django import forms
from .models import Categorie, Produit



class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = [
            'code', 'nom', 'description', 'categorie', 'marque',
            'prix_achat', 'prix_unitaire', 'stock', 'seuil_alerte',
            'unite', 'actif'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }
