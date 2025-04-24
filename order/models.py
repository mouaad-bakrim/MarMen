from django.db import models

from client.models import Client
from produit.models import Produit


class Devis(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='devis')
    reference = models.CharField(max_length=50, unique=True)
    date_devis = models.DateField(auto_now_add=True)

    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('accepte', 'Accepté'),
            ('rejete', 'Rejeté'),
        ],
        default='en_attente'
    )

    remarque = models.TextField(blank=True, null=True)

    def total_ht(self):
        return sum(ligne.sous_total() for ligne in self.lignes.all())

    def __str__(self):
        return f"Devis {self.reference} - {self.client.nom}"


class LigneDevis(models.Model):
    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"



class BonCommande(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='commandes')
    reference = models.CharField(max_length=50, unique=True)
    date_commande = models.DateField(auto_now_add=True)

    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_attente', 'En attente'),
            ('confirmee', 'Confirmée'),
            ('annulee', 'Annulée'),
            ('livree', 'Livrée'),
        ],
        default='en_attente'
    )

    remarque = models.TextField(blank=True, null=True)

    def total_ht(self):
        return sum(ligne.sous_total() for ligne in self.lignes.all())

    def __str__(self):
        return f"Commande {self.reference} - {self.client.nom}"


class LigneCommande(models.Model):
    commande = models.ForeignKey(BonCommande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def sous_total(self):
        return self.quantite * self.prix_unitaire

    def __str__(self):
        return f"{self.produit.nom} x {self.quantite}"


class BonLivraison(models.Model):
    commande = models.OneToOneField(BonCommande, on_delete=models.CASCADE, related_name='livraison')
    reference = models.CharField(max_length=50, unique=True)
    date_livraison = models.DateField(auto_now_add=True)

    statut = models.CharField(
        max_length=20,
        choices=[
            ('preparee', 'Préparée'),
            ('livree', 'Livrée'),
            ('retournee', 'Retournée'),
        ],
        default='preparee'
    )

    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"BDL {self.reference} - Commande {self.commande.reference}"





class Facture(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='factures')
    commande = models.OneToOneField(BonCommande, on_delete=models.CASCADE, related_name='facture')
    reference = models.CharField(max_length=50, unique=True)
    date_facture = models.DateField(auto_now_add=True)
    total_ht = models.DecimalField(max_digits=12, decimal_places=2)
    total_ttc = models.DecimalField(max_digits=12, decimal_places=2)
    statut = models.CharField(
        max_length=20,
        choices=[
            ('non_payee', 'Non payée'),
            ('partiellement_payee', 'Partiellement payée'),
            ('payee', 'Payée'),
        ],
        default='non_payee'
    )

    def __str__(self):
        return f"Facture {self.reference} - {self.client.nom}"

class ModePaiement(models.Model):
    nom = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom


class Paiement(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='paiements')
    date_paiement = models.DateField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    mode = models.ForeignKey(ModePaiement, on_delete=models.SET_NULL, null=True)

    remarque = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.montant} DH - {self.mode.nom} - Facture {self.facture.reference}"
