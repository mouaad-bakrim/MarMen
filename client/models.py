from django.db import models

class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True, null=True)
    societe = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    code_postal = models.CharField(max_length=10, blank=True, null=True)
    pays = models.CharField(max_length=100, blank=True, null=True)
    numero_identification_fiscale = models.CharField(max_length=50, blank=True, null=True)
    registre_commerce = models.CharField(max_length=50, blank=True, null=True)
    site_web = models.URLField(blank=True, null=True)
    date_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nom} {self.prenom or ''}".strip()
