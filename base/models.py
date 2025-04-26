
from django.contrib.auth.models import User
from django.db import models
from simple_history.models import HistoricalRecords
from django.core.exceptions import ValidationError



class Societe(models.Model):
    FORMES = (
        ('sarl', 'SARL'),
        ('sarlau', 'SARL AU'),
        ('sa', 'SA'),
    )

    class Meta:
        ordering = ["nom"]
        verbose_name_plural = "Sociétés"
        default_permissions = ['add', 'change', 'view']
        db_table = "base_company"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verbose_name = "Société"
    nom = models.CharField(max_length=30, verbose_name="Raison sociale")
    phone = models.CharField(max_length=16, verbose_name="Téléphone", null=True, blank=True)
    adresse1 = models.CharField(max_length=30, verbose_name="Adresse", null=True, blank=True)
    adresse2 = models.CharField(max_length=30, verbose_name="Suite", null=True, blank=True)
    ville = models.CharField(max_length=15, verbose_name="Ville")
    patente = models.CharField(max_length=15, verbose_name="Patente", null=True, blank=True)
    rc = models.CharField(max_length=15, verbose_name="Registre de commerce", null=True, blank=True)
    cnss = models.CharField(max_length=15, verbose_name="Num CNSS", null=True, blank=True)
    idf = models.CharField(max_length=15, verbose_name="Identifiant fiscal", null=True, blank=True)
    actif = models.BooleanField(default=True, verbose_name="Actif")
    ice = models.CharField(max_length=15, verbose_name="ICE", null=True, blank=True)
    rib = models.CharField(max_length=30, verbose_name="RIB", null=True, blank=True)
    logo = models.ImageField(upload_to='logo', blank=True, null=True, verbose_name="Logo")
    forme = models.CharField(max_length=10, verbose_name="Forme juridique", choices=FORMES, null=True, blank=True)

    capital_social = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Capital Social (MAD)",
                                         null=True, blank=True)
    email = models.EmailField(max_length=100, verbose_name="Email", null=True, blank=True)
    secteur_activite = models.CharField(max_length=100, verbose_name="Secteur d'activité", null=True, blank=True)

    def __str__(self):
        if self.forme:
            return "{0} {1}".format(self.nom, self.get_forme_display())
        else:
            return self.nom

class Regions(models.TextChoices):
    MA01 = "MA01", "Tanger-Tétouan-Al Hoceïma"
    MA02 = "MA02", "L'Oriental"
    MA03 = "MA03", "Fès-Meknès"
    MA04 = "MA04", "Rabat-Salé-Kénitra"
    MA05 = "MA05", "Béni Mellal-Khénifra"
    MA06 = "MA06", "Casablanca-Settat"
    MA07 = "MA07", "Marrakech-Safi"
    MA08 = "MA08", "Drâa-Tafilalet"
    MA09 = "MA09", "Souss-Massa"
    MA10 = "MA10", "Guelmim-Oued Noun"
    MA11 = "MA11", "Laâyoune-Sakia El Hamra"
    MA12 = "MA12", "Dakhla-Oued Ed-Dahab"
    ATRE = "ATRE", "Autre / Etranger"


class Site(models.Model):
    class Meta:
        ordering = ["nom"]
        verbose_name_plural = "Sites"
        permissions = (
            ('can_access_hht_parameters', 'Gestion des HHT'),
            ('is_admin_for_hht', 'Mode administrateur pour'),
        )
        default_permissions = ['add', 'change', 'view']
        db_table = "base_site"

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    verbose_name = "Site"
    nom = models.CharField(max_length=40, verbose_name="Nom")
    nom_facture = models.CharField(max_length=40, verbose_name="nom_facture")
    phone = models.CharField(max_length=16, verbose_name="Téléphone", null=True, blank=True)
    adresse1 = models.CharField(max_length=30, verbose_name="Adresse", null=True, blank=True)
    adresse2 = models.CharField(max_length=40, verbose_name="Suite", null=True, blank=True)
    ville = models.CharField(max_length=40, verbose_name="Ville", null=True, blank=True)
    patente = models.CharField(max_length=15, verbose_name="Patente", null=True, blank=True)
    ref = models.CharField(max_length=5, verbose_name="Ref")
    rib = models.CharField(max_length=30, verbose_name="RIB", null=True, blank=True)  # Champ RIB
    actif = models.BooleanField(default=True, null=True, verbose_name="Actif")


    history = HistoricalRecords(table_name="base_site_history")
    societe_obj = models.ForeignKey(Societe, verbose_name="Société", related_name="sites", on_delete=models.PROTECT,
                                    limit_choices_to={'actif': True})

    region = models.CharField(max_length=6, verbose_name="Région", choices=Regions.choices)



    def __str__(self):
        return self.nom

    def invoice_footer(self, *args, **kwargs):
        first_line = f"{self.societe_obj.nom} - Tél: {self.societe_obj.phone or self.phone}"

        if self.societe_obj.secteur_activite:
            first_line += f" - Secteur d'activité: {self.societe_obj.secteur_activite}"

        additional_info = self._get_additional_info(self.societe_obj)
        payment_info = self._get_payment_info(self.societe_obj)

        return first_line, additional_info, payment_info

    def _get_additional_info(self, societe):
        info = [

            f"Ville: {societe.ville}" if societe.ville else "",
            f"ICE: {societe.ice}" if societe.ice else "",
            f"RC: {societe.rc}" if societe.rc else "",
            f"Identifiant Fiscal: {societe.idf}" if societe.idf else "",
            f"CNSS: {societe.cnss}" if societe.cnss else "",
        ]
        return " - ".join(filter(None, info))

    def _get_payment_info(self, societe):
        info = [
            f"RIB: {self.rib}" if self.rib else "",
            f"Capital Social: {societe.capital_social} MAD" if societe.capital_social else "",

        ]
        return " - ".join(filter(None, info))



class Profile(models.Model):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('superadmin', 'Superadmin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    sites = models.ManyToManyField(Site, blank=True, verbose_name="Sites")

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


    def is_superadmin(self):
        return self.role == 'superadmin'



