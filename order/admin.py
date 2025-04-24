from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Devis, LigneDevis,
    BonCommande, LigneCommande,
    BonLivraison, Facture,
    ModePaiement, Paiement
)


class LigneDevisInline(admin.TabularInline):
    model = LigneDevis
    extra = 1


@admin.register(Devis)
class DevisAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'date_devis', 'statut', 'total_ht')
    list_filter = ('statut', 'date_devis')
    search_fields = ('reference', 'client__nom')
    inlines = [LigneDevisInline]


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 1


@admin.register(BonCommande)
class BonCommandeAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'date_commande', 'statut', 'total_ht')
    list_filter = ('statut', 'date_commande')
    search_fields = ('reference', 'client__nom')
    inlines = [LigneCommandeInline]


@admin.register(BonLivraison)
class BonLivraisonAdmin(admin.ModelAdmin):
    list_display = ('reference', 'commande', 'date_livraison', 'statut')
    list_filter = ('statut', 'date_livraison')
    search_fields = ('reference', 'commande__reference')


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('reference', 'client', 'commande', 'date_facture', 'statut', 'total_ht', 'total_ttc')
    list_filter = ('statut', 'date_facture')
    search_fields = ('reference', 'client__nom', 'commande__reference')


@admin.register(ModePaiement)
class ModePaiementAdmin(admin.ModelAdmin):
    list_display = ('nom',)
    search_fields = ('nom',)


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('facture', 'date_paiement', 'montant', 'mode')
    list_filter = ('date_paiement', 'mode')
    search_fields = ('facture__reference', 'mode__nom')
