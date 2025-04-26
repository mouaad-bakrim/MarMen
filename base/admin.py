from django.contrib import admin

from base.models import Societe, Site, Profile


# Register your models here.

class SocieteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'phone', 'ville', 'actif', 'forme')
    search_fields = ('nom', 'phone', 'ville', 'patente', 'rc', 'cnss', 'idf', 'ice')
    list_filter = ('actif', 'forme')

    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20

    fieldsets = (
        (None, {
            'fields': ('nom', 'forme', 'actif')
        }),
        ('Coordonnées Complètes', {
            'fields': ('phone', 'adresse1', 'adresse2', 'ville'),
            'classes': ('collapse',)
        }),
        ('Documents', {
            'fields': ('patente','rib', 'rc', 'cnss', 'idf', 'ice', 'email','secteur_activite','capital_social'),
            'classes': ('collapse',)
        }),
        ('Logo et Dates', {
            'fields': ('logo', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )



class SiteAdmin(admin.ModelAdmin):
    list_display = ('nom','nom_facture', 'phone', 'ville', 'actif', 'region', 'societe_obj')
    search_fields = ('nom', 'phone', 'ville')
    list_filter = ('actif', 'region', 'societe_obj')
    ordering = ('nom',)
    raw_id_fields = ('societe_obj',)
    autocomplete_fields = ('societe_obj',)

    fieldsets = (
        (None, {
            'fields': ('nom','nom_facture', 'phone', 'actif')
        }),
        ('Société Associée', {
            'fields': ('societe_obj',),
            'classes': ('collapse',)
        }),
        ('Adresse', {
            'fields': ('adresse1', 'adresse2', 'ville', 'region', 'patente','rib', 'ref'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'display_sites')
    list_filter = ('role', 'sites')
    search_fields = ('user__username', 'role', 'sites__nom')


    def display_sites(self, obj):
        return ", ".join([site.nom for site in obj.sites.all()])


    display_sites.short_description = "Sites"
admin.site.register(Societe, SocieteAdmin)
admin.site.register(Site, SiteAdmin)