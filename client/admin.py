from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        'nom', 'prenom', 'societe', 'telephone',
        'ville', 'date_creation'
    )
    list_filter = ('ville',  'date_creation')
    search_fields = ('nom', 'prenom', 'societe',  'telephone')
    ordering = ('-date_creation',)
    fieldsets = (
        ("Informations Générales", {
            'fields': ('nom', 'prenom', 'societe', 'telephone')
        }),
        ("Adresse", {
            'fields': ('adresse', 'ville')
        }),
        ("Informations Légales", {
            'fields': ('idf', 'rc', 'ice')
        }),
    )
