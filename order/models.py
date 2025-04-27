from django.db import models
from io import BytesIO
from django.shortcuts import get_list_or_404
from django.utils.timezone import now
from django.core.mail import send_mail
from decimal import Decimal
from base.models import Site
from client.models import Client
from produit.models import Produit
import os
from datetime import date

from datetime import timedelta
from django_fsm import FSMField, transition
from django.utils import timezone
from django_fsm_log.decorators import fsm_log_by, fsm_log_description



class Order(models.Model):
    class Meta:
        ordering = ["-id"]
        verbose_name = "Order"
        verbose_name_plural = "Order"
        default_permissions = ['add', 'change', 'view']
        db_table = "order_order"

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client')
    date = models.DateField(verbose_name="Date", default=timezone.now)
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant', default=0)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Site", null=True, blank=True)

    def __str__(self):
        return f"Order {self.id}"

    def update_montant_total(self):
        total = self.order.aggregate(
            total=models.Sum('montant')
        )['total'] or 0
        self.montant = total
        self.save()

    def create_devis_from_order(self):

        with transaction.atomic():
            # 1. Créer un Devis
            devis = Devis.objects.create(
                code=f"DEV-{timezone.now().strftime('%Y%m%d')}-{self.id}",
                client=self.client,
                site=self.site,
                date=self.date,
                tva=10,  # TVA fixe à 10% par défaut
            )

            # 2. Créer les lignes du Devis à partir des OrderLigne
            for order_ligne in self.order.all():
                DevisLinge.objects.create(
                    devis=devis,
                    produit=order_ligne.produit,
                    unite="U",  # ou récupère l'unité depuis Produit si tu l'as
                    quantite=order_ligne.quantite,
                    prix=order_ligne.prix,
                    remise=order_ligne.remise,
                    montant=order_ligne.montant,
                )
            return devis

    from django.db import transaction


class OrderLigne(models.Model):
    class Meta:
        ordering = ["-id"]
        verbose_name = "Article Lubrifiant Direct"
        verbose_name_plural = "Articles Lubrifiant Direct"
        default_permissions = ['add', 'change', 'view']
        db_table = "direct_ArticleLubrifiant"

    order = models.ForeignKey(
        'Order',
        on_delete=models.CASCADE,
        related_name='order'
    )
    produit = models.ForeignKey(
        Produit,
        on_delete=models.CASCADE,
        verbose_name="Article "
    )
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantite = models.PositiveIntegerField()
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant', default=0)
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name='Remise (%)')

    def save(self, *args, **kwargs):
        remise_appliquee = (1 - (self.remise / 100))
        self.montant = self.prix * self.quantite * remise_appliquee
        super().save(*args, **kwargs)

        # Met à jour automatiquement le montant de l'Order
        if self.order:
            self.order.update_montant_total()

    def __str__(self):
        return f"{self.produit} - {self.quantite} unités"


from django.db import transaction


class Devis(models.Model):
    class Meta:
        verbose_name = 'Devis'
        verbose_name_plural = 'Devis'
        permissions = [
            ("can_commande_conf", "Can view Bon de Commande conf"),
            ("can_commande_annule", "Can view Devis annule"),
        ]
        ordering = ['-date']

    DRAFT = 'draft'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    STATES = [
        (DRAFT, 'Brouillon'),
        (ACCEPTED, 'Accepté'),
        (REJECTED, 'Rejeté'),
    ]

    code = models.CharField(max_length=20, verbose_name='Code Devis', unique=True)
    date = models.DateField(verbose_name='Date', default=timezone.now)
    tva = models.DecimalField(max_digits=5, decimal_places=2, default=10, verbose_name="TVA")
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Site', blank=True, null=True)
    etat = FSMField(default=DRAFT, db_index=True, choices=STATES, verbose_name="État", protected=True)


    def __str__(self):
        return f"Devis {self.code} - {self.client.nom}"

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

    def get_total_quantite(self):
        total_quantite = self.devislinge_set.aggregate(total_quantite=models.Sum('quantite'))['total_quantite']
        return total_quantite if total_quantite is not None else 0

    def get_total_montant(self):
        total_montant = self.devislinge_set.aggregate(total_montant=models.Sum('montant'))['total_montant']
        return total_montant if total_montant is not None else 0

    def can_commande_divis_annule(self):
        return True

    @fsm_log_by
    @fsm_log_description
    @transition(field=etat, source=DRAFT, target=REJECTED, conditions=[can_commande_divis_annule],
                permission='direct.can_commande_annule')
    def mark_as_commande_divis_annule(self, by, description=None):
        self.data_create = datetime.now()

    def devis_accepted_direect(self):
        return True

    @fsm_log_by
    @fsm_log_description
    @transition(field=etat, source=DRAFT, target=ACCEPTED, conditions=[devis_accepted_direect],
                permission='direct.can_commande_ongoing')
    def mark_as_accepted_direct(self, by, description=None):
        self.data_create = datetime.now()
        self.create_bon_commande()

        # Check if there is any article associated with the devis lines before calling retirer_quantite_stock
        if self.devislinge_set.filter(article__isnull=False).exists():  # Ensure there's an article in the line
            self.retirer_quantite_stock()

    def retirer_quantite_stock(self):
        lignes_devis = self.devislinge_set.all()
        if not lignes_devis.exists():
            raise ValueError("La commande ne contient aucune ligne.")
        try:
            # Itérer sur chaque ligne de devis
            for ligne in lignes_devis:
                # Vérifier si l'article_site existe et retirer la quantité
                article_site = ArticleSite.objects.filter(
                    article=ligne.article.article,  # Utilisation de 'article' de la ligne de devis
                    site=self.site
                ).first()

                if article_site:
                    article_site.retirer_quantite(ligne.quantite)  # Retirer la quantité de l'article
                else:
                    raise ValueError(f"Article {ligne.article} non trouvé dans le stock.")
        except ValueError as e:
            print(f"Erreur lors du retrait de stock : {e}")

    def create_bon_commande(self):
        try:
            with transaction.atomic():
                # Récupération des lignes de devis
                lignes_devis = self.devislinge_set.all()

                # Validation des lignes
                if not lignes_devis.exists():
                    raise ValueError("Le devis ne contient aucune ligne.")

                produits = lignes_devis.values_list('produit', flat=True).distinct()
                if len(produits) > 1:
                    raise ValueError("Le devis contient plusieurs produits différents.")

                produit = lignes_devis.first().produit
                current_year = self.date.year
                last_bon = BonClientCommandeDirect.objects.filter(
                    bon_commande__startswith=f"BC/DD/{current_year}"
                ).order_by('-id').first()

                last_id = int(last_bon.bon_commande.split("-")[-1]) if last_bon else 0
                bon_commande_code = f"BC/DD/{current_year}-{last_id + 1:05d}"

                # Calcul des totaux
                total_remise = sum(ligne.remise for ligne in lignes_devis)
                total_montant_ht = sum(ligne.montant for ligne in lignes_devis)
                total_montant_tva = total_montant_ht * Decimal('0.1')
                total_montant_ttc = total_montant_ht + total_montant_tva
                total_quantite = sum(ligne.quantite for ligne in lignes_devis)
                total_prix = sum(ligne.prix for ligne in lignes_devis)

                bon_commande = BonClientCommandeDirect.objects.create(
                    date=self.date,
                    client=self.client,
                    tva=self.tva,
                    montant_ht=total_montant_ht,
                    montant_tva=total_montant_tva,
                    montant_ttc=total_montant_ttc,
                    bon_commande=bon_commande_code,
                    chauffeur=self.chauffeur,
                    matricule=self.matricule,
                    modele=self.modele,
                    site=self.site,
                )

                # Création des lignes de commande à partir des lignes de devis
                for ligne in lignes_devis:
                    if ligne.article:
                        # Si un article existe, on l'utilise
                        article = ligne.article.article
                    else:
                        # Sinon, utiliser le produit associé à la ligne
                        article = ligne.produit

                    CommandeLigne.objects.create(
                        bon_commande=bon_commande,
                        produit=article,
                        unite=ligne.unite,
                        quantite=ligne.quantite,
                        prix=ligne.prix,
                        remise=ligne.remise,
                        montant_ht=ligne.montant,
                        montant_tva=ligne.montant * Decimal('0.1'),
                        montant_ttc=ligne.montant * Decimal('1.1'),
                    )



        except Exception as e:
            raise ValueError(f"Erreur lors de la création du Bon de Commande : {e}")

    def generate_devis_number(self):
        # Crée un numéro unique pour le devis
        return f"DEV-{self.pk}-{timezone.now().strftime('%Y')}"




class DevisLinge(models.Model):
    class Meta:
        verbose_name = 'Ligne de Devis'
        verbose_name_plural = 'Lignes de Devis'
        permissions = [
            ("can_view_devislinge", "Can view Ligne de Devis"),
            ("can_edit_devislinge", "Can edit Ligne de Devis"),
            ("can_delete_devislinge", "Can delete Ligne de Devis"),
        ]

    devis = models.ForeignKey(Devis, on_delete=models.CASCADE, verbose_name='Devis')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, verbose_name='Produit', blank=True, null=True)
    unite = models.CharField(max_length=20, verbose_name='Unité', blank=True, null=True)
    quantite = models.PositiveIntegerField(verbose_name='Quantité')
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix unitaire")
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant')

    def __str__(self):
        return f"{self.quantite}"

    def save(self, *args, **kwargs):
        # Calcul du montant avec remise
        # La remise est exprimée en pourcentage, donc diviser par 100
        remise_appliquee = (1 - self.remise / 100)
        self.montant = self.quantite * self.prix * remise_appliquee
        super().save(*args, **kwargs)


class BonLivraison(models.Model):
    class Meta:
        verbose_name = 'Bon de Livraison Direct'
        verbose_name_plural = 'Bons de Livraison Direct'
        permissions = [
            ("can_view_bonlivraison", "Can view Bon de Livraison "),
        ]

    date = models.DateField(verbose_name='Date')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Client')
    tva = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="TVA")
    bon_livraison = models.CharField(max_length=16, verbose_name='Code Bon de Livraison', unique=True)

    bon_commande = models.CharField(max_length=16, verbose_name="Numéro du Bon de Commande", null=True, blank=True)
    matricule = models.CharField(max_length=20, verbose_name='Matricule', blank=True, null=True)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant HT')
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant TVA')
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant TTC')
    site = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name='Site', blank=True, null=True)

    def __str__(self):
        return f"{self.bon_livraison}"

    def total_quantite(self):
        return self.lignes.aggregate(total=Sum('quantite'))['total'] or 0

    def get_Quantité_livreur(self):
        quantite = self.total_quantite()

        # Vérifier si la quantité est un entier (ex: 10.000 → 10)
        if quantite == int(quantite):
            return int(quantite)  # Retourner un entier sans les décimales
        else:
            return round(quantite, 2)  # Retourner un nombre avec 2 décimales si nécessaire

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)



class BonLivraisonLigne(models.Model):
    class Meta:
        verbose_name = 'Ligne de Bon de Livraison'
        verbose_name_plural = 'Lignes de Bons de Livraison'

    bon_livraison = models.ForeignKey(
        BonLivraison,
        on_delete=models.CASCADE,
        related_name='lignes',
        verbose_name='Bon de Livraison'
    )

    produit = models.CharField(max_length=100, verbose_name='Produit', blank=True, null=True)
    quantite = models.DecimalField(max_digits=10, decimal_places=4)
    prix = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Prix Unitaire')
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")
    unite = models.CharField(max_length=20, verbose_name='Unité', blank=True, null=True)
    montant_ht = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant HT', editable=False)
    montant_tva = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant TVA', editable=False)
    montant_ttc = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Montant TTC', editable=False)

    def save(self, *args, **kwargs):
        # Récupérer le taux de TVA depuis l'objet BonLivraisonDirect
        taux_tva = self.bon_livraison.tva / Decimal('100')  # Convertir en pourcentage

        # Calcul des montants
        self.montant_ttc = self.quantite * self.prix * (1 - self.remise / Decimal('100'))

        self.montant_ht = self.montant_ttc / (1 + taux_tva)
        self.montant_tva = self.montant_ttc - self.montant_ht

        super().save(*args, **kwargs)

from django.conf import settings
from django.utils import timezone
from num2words import num2words
import logging
from django.core.mail import EmailMessage

class FactureDirect(models.Model):
    class Meta:
        ordering = ["-updated_at"]
        verbose_name_plural = "Facture"

        permissions = [
            ("can_view_facture", "Peut voir les factures"),
            ("can_add_facture", "Peut ajouter une facture"),
            ("can_edit_facture", "Peut modifier une facture"),
            ("can_delete_facture", "Peut supprimer une facture"),
        ]

    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('virement', 'Virement Bancaire'),
        ('cmi', 'CMI'),
        ('effet', 'EFFET'),
        ('autre', 'Autre'),
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name="Client")
    date = models.DateTimeField(default=timezone.now)
    date_echeance = models.DateField(verbose_name="Date d'Échéance", null=True, blank=True)
    total_quantity = models.IntegerField(verbose_name="Quantité Totale")
    bons_livraison = models.ManyToManyField('BonLivraison', related_name='factures',
                                                   verbose_name="Bons de Livraison")
    tva = models.CharField(max_length=16, verbose_name="TVA")
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")
    montant_ht = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="montant_ht")
    montant_lettres = models.CharField(max_length=255, null=True, blank=True, verbose_name="Montant en lettres")
    montant_ttc = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant TTC")
    montant_tva = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Montant TVA")
    numero = models.CharField(max_length=100, unique=True)
    STATUT_PAIEMENT_CHOICES = [
        ('non_paye', 'Non Payé'),
        ('demi_paye', 'Demi Payé'),
        ('paye', 'Payé'),
    ]
   
    mode_paiement = models.CharField(
        max_length=20,
        blank=True, null=True,
        choices=MODE_PAIEMENT_CHOICES,
        verbose_name="Mode de Paiement"
    )

    statut_paiement = models.CharField(max_length=20, choices=STATUT_PAIEMENT_CHOICES, default='non_paye')
    montant_paye = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant Payé")
    email_envoye = models.BooleanField(default=False)

    def __str__(self):
        return f"Facture {self.numero} - {self.client.nom}"

    def get_avancement(self):
        if self.montant_ttc > 0:
            return (self.montant_paye / self.montant_ttc) * 100
        return 0

    def montant_restant(self):
        """Calculer le montant restant après paiement."""
        return self.montant_ttc - self.montant_paye if self.montant_ttc and self.montant_paye else self.montant_ttc

    def enregistrer_paiement(self, montant, justification=None):
        """Enregistre un paiement et ajuste le statut de la facture et du solde du client."""
        if montant <= 0 or montant > (self.montant_ttc - self.montant_paye):
            raise ValueError("Montant invalide pour ce paiement.")

        # Mise à jour du montant payé
        self.montant_paye += montant

        # Mise à jour du statut de paiement
        if self.montant_paye >= self.montant_ttc:
            self.statut_paiement = 'paye'
        elif self.montant_paye > 0:
            self.statut_paiement = 'demi_paye'

        # Enregistrer la justification de paiement s'il y en a une
        if justification:
            self.justification_paiement = justification

        # Enregistrer la mise à jour
        self.save()

        # Ajuster le solde du client
        self.mettre_a_jour_solde(montant)


    def render_bons_livraison(self, value, record):
        print(f"Rendering bons livraison for record {record.numero}")
        return record.nombre_bons_livraison()

    def convert_number_to_words(self, number):
        """Convertit un montant en chiffres en lettres."""
        entier = int(number)
        centimes = int((number * 100) % 100)

        entier_en_lettres = num2words(entier, lang='fr').replace('-', ' ')
        resultat = f"{entier_en_lettres} Dirhams"

        if centimes > 0:
            centimes_en_lettres = num2words(centimes, lang='fr').replace('-', ' ')
            resultat += f" et {centimes_en_lettres} centimes"

        return resultat

    def save(self, *args, **kwargs):
        # Convertir montant_ttc en montant_lettres
        if self.montant_ttc is not None:
            self.montant_lettres = self.convert_number_to_words(self.montant_ttc)
        else:
            self.montant_lettres = ""

            # Mettre à jour le statut de paiement
        if self.montant_paye >= self.montant_ttc:
            self.statut_paiement = 'paye'
        elif self.montant_paye > 0:
            self.statut_paiement = 'demi_paye'
        else:
            self.statut_paiement = 'non_paye'

        super().save(*args, **kwargs)

    from django.core.mail import EmailMessage
    from django.utils.timezone import now
    from django.conf import settings

    def envoyer_email_echeance(self):
        """Envoie un email avec un design amélioré si la facture est échue et non payée."""
        if self.date_echeance and self.date_echeance < now().date() and self.statut_paiement == 'non_paye':
            subject = f"🔔 URGENT : Rappel de paiement - Facture {self.numero}"

            message = f"""\
                    <html>
                    <body style="font-family: Arial, sans-serif; color: #333; background-color: #f4f4f4; padding: 20px;">
                        <div style="max-width: 600px; background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 0px 10px #ccc;">
                            <h2 style="color: #003366; text-align: center;">🔔 Rappel de paiement</h2>
                            <p>Bonjour <strong>{self.client.nom}</strong>,</p>
                            <p style="color: red; font-size: 16px;"><strong>Votre facture est échue et reste impayée.</strong></p>
                            <p>Merci de procéder au règlement dès que possible afin d'éviter toute pénalité ou interruption de service.</p>

                            <h3 style="color: #003366;">📄 Détails de la facture</h3>
                            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                                <tr>
                                    <td style="background: #003366; color: white; padding: 10px; text-align: left;"><strong>Référence</strong></td>
                                    <td style="padding: 10px; text-align: right;">{self.numero}</td>
                                </tr>
                                <tr>
                                    <td style="background: #f8f8f8; padding: 10px; text-align: left;"><strong>Montant dû</strong></td>
                                    <td style="padding: 10px; text-align: right;"><strong>{self.montant_ttc} MAD</strong></td>
                                </tr>
                                <tr>
                                    <td style="background: #f8f8f8; padding: 10px; text-align: left;"><strong>Date d’échéance</strong></td>
                                    <td style="padding: 10px; text-align: right;">{self.date_echeance}</td>
                                </tr>
                            </table>

                            <h3 style="color: #003366;">🏢 Informations du site</h3>
                            <p><strong>Site :</strong> {self.client.site.nom}</p>
                            <p><strong>Adresse :</strong> {self.client.site.adresse1}</p>

                            <h3 style="color: #003366;">📜 Articles de la facture</h3>
                            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                                <tr style="background: #003366; color: white;">
                                    <th style="padding: 10px;">Désignation</th>
                                    <th style="padding: 10px;">Quantité</th>
                                    <th style="padding: 10px;">Prix Unitaire</th>
                                    <th style="padding: 10px;">Total</th>
                                </tr>"""

            for bon_livraison in self.bons_livraison_direct.all():  # Iterate through each related BonLivraisonDirect
                for ligne in bon_livraison.lignes.all():  # Access the related BonLivraisonLigne objects
                    message += f"""
                        <tr style="background: #f8f8f8;">
                            <td style="padding: 10px;">{ligne.produit}</td>
                            <td style="padding: 10px; text-align: center;">{ligne.quantite}</td>
                            <td style="padding: 10px; text-align: right;">{ligne.prix} MAD</td>
                            <td style="padding: 10px; text-align: right;">{ligne.montant_ttc} MAD</td>
                        </tr>
                    """

            message += """
                            </tbody>
                        </table>


                        <p>Vous trouverez en pièce jointe une copie de votre facture.</p>
                        <p>Pour toute question ou assistance, n'hésitez pas à nous contacter.</p>

                        <p style="text-align: center; color: gray; font-size: 12px;">
                            Merci pour votre prompt règlement. <br> Cordialement, <br> <strong>L'équipe de Gestion</strong>
                        </p>
                    </div>
                </body>
                </html>
            """

            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [self.client.email]

            # Création de l'email avec HTML
            email = EmailMessage(subject, message, from_email, recipient_list)
            email.content_subtype = "html"  # Indiquer que l'email est en HTML

            email.send()

    @property
    def three_days_later(self):
        """Retourne la date actuelle + 3 jours."""
        return now().date() + timedelta(days=3)

    def doit_envoyer_email_rappel(self):
        """Vérifie si l'email doit être envoyé."""
        return (
                self.date_echeance
                and self.date_echeance <= self.three_days_later
                and self.statut_paiement == "non_paye"
                and not self.email_envoye
        )

    def facture_en_retard(self):
        """Vérifie si la facture est en retard."""
        return self.date_echeance and self.date_echeance <= self.three_days_later

