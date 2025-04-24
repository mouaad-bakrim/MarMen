from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'prenom', 'societe', 'email', 'telephone',
        'ville', 'pays', 'date_creation'
    )
    list_filter = ('ville', 'pays', 'date_creation')
    search_fields = ('nom', 'prenom', 'societe', 'email', 'telephone')
    ordering = ('-date_creation',)
    fieldsets = (
        ("Informations Générales", {
            'fields': ('nom', 'prenom', 'societe', 'email', 'telephone')
        }),
        ("Adresse", {
            'fields': ('adresse', 'ville', 'code_postal', 'pays')
        }),
        ("Informations Légales", {
            'fields': ('numero_identification_fiscale', 'registre_commerce', 'site_web')
        }),
    )
