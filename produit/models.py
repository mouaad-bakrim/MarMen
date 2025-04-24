from django.db import models

class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

class Produit(models.Model):
    code = models.CharField(max_length=50, unique=True)  # Référence ou SKU
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    marque = models.CharField(max_length=100, blank=True, null=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)  # Pour alerte stock bas
    unite = models.CharField(max_length=20, default="pièce")  # ex: pièce, kg, litre
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} ({self.code})"
