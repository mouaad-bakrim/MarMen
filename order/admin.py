from django.contrib import admin
from .models import Order, OrderLigne

class OrderLigneInline(admin.TabularInline):
    model = OrderLigne
    extra = 1  # Nombre de lignes vides en plus

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'date', 'montant', 'site')  # les colonnes dans la liste
    inlines = [OrderLigneInline]  # <- pour afficher les OrderLigne dans l'Order
    search_fields = ('client__nom', 'id',)
    list_filter = ('date', 'site')

admin.site.register(Order, OrderAdmin)



from django.contrib import admin
from .models import Devis, DevisLinge

class DevisLingeInline(admin.TabularInline):
    model = DevisLinge
    extra = 1

class DevisAdmin(admin.ModelAdmin):
    list_display = ('code', 'client', 'date', 'etat', 'site')  # colonnes visibles
    inlines = [DevisLingeInline]  # <- pour afficher les DevisLigne directement dans Devis
    search_fields = ('code', 'client__nom',)
    list_filter = ('etat', 'date', 'site')

admin.site.register(Devis, DevisAdmin)
