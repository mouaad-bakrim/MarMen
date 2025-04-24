from django.contrib import admin
from .models import Categorie, Produit


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'date_creation')
    search_fields = ('nom',)
    ordering = ('-date_creation',)


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = (
        'code', 'nom', 'categorie', 'marque', 'prix_unitaire', 'stock',
        'seuil_alerte', 'unite', 'actif', 'date_ajout'
    )
    list_filter = ('categorie', 'actif', 'unite', 'marque')
    search_fields = ('code', 'nom', 'marque')
    list_editable = ('prix_unitaire', 'stock', 'actif')
    ordering = ('-date_ajout',)
