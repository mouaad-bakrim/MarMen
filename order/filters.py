import django_filters as df
from django import forms
from base.filters import MaeDateRangeFilter
from .models import BonLivraisonDirect,Devis,FactureDirect,CarburateurDirect, BonClientCommandeDirect
from client.models import Client
from user_management.models import Employee


class CarburantDirectListFilter(df.FilterSet):
    date = MaeDateRangeFilter(
        field_name="date",
        widget=forms.TextInput(attrs={'placeholder': 'Date', "class": "date-range-picker"})
    )

    mois = df.ChoiceFilter(
        field_name='date',
        method='filter_by_month',
        label='Mois',
        choices=[
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Mois",
                "data-hide-search": "true",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    client = df.ModelChoiceFilter(
        field_name='client',
        queryset=Client.objects.all(),
        label='Client',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un client",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    chauffeur = df.ModelChoiceFilter(
        field_name='chaffeur',
        queryset=Employee.objects.filter(calification='Chauffeur'),
        label='Chauffeur',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un chauffeur",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )

    # Nouveau filtre pour matricule
    matricule = df.CharFilter(
        field_name='matricule',
        lookup_expr='icontains',  # Recherche insensible à la casse
        label='Matricule',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control form-control-solid',
                'placeholder': 'Saisir le matricule',
            }
        )
    )

    class Meta:
        model = CarburateurDirect
        fields = ["client", "mois", "date", "chauffeur", "matricule"]


    def filter_by_month(self, queryset, name, value):
        if value:
            return queryset.filter(**{
                f'{name}__month': value
            })
        return queryset


class LubrifiantDirectListFilter(df.FilterSet):
    date = MaeDateRangeFilter(
        field_name="date",
        widget=forms.TextInput(attrs={'placeholder': 'Date', "class": "date-range-picker"})
    )

    mois = df.ChoiceFilter(
        field_name='date',
        method='filter_by_month',
        label='Mois',
        choices=[
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Mois",
                "data-hide-search": "true",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    client = df.ModelChoiceFilter(
        field_name='client',
        queryset=Client.objects.all(),
        label='Client',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un client",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )



    class Meta:
        model = CarburateurDirect
        fields = ["client", "mois", "date"]


    def filter_by_month(self, queryset, name, value):
        if value:
            return queryset.filter(**{
                f'{name}__month': value
            })
        return queryset





class BonDevisDirectListFilter(df.FilterSet):
    date = MaeDateRangeFilter(
        field_name="date",
        widget=forms.TextInput(attrs={'placeholder': 'Date', "class": "date-range-picker"})
    )

    mois = df.ChoiceFilter(
        field_name='date',
        method='filter_by_month',
        label='Mois',
        choices=[
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Mois",
                "data-hide-search": "true",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    client = df.ModelChoiceFilter(
        field_name='client',
        queryset=Client.objects.all(),
        label='Client',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un client",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )

    etat = df.ChoiceFilter(
        field_name='etat',
        label="État",
        choices=Devis.STATES,  # Utiliser les états définis dans votre modèle Devis
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un état",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )




    class Meta:
        model = Devis
        fields = ["client", "mois", "date", "etat"]

    def filter_by_month(self, queryset, name, value):
        if value:
            return queryset.filter(**{
                f'{name}__month': value
            })
        return queryset


class BonCommandeDirectListFilter(df.FilterSet):
    date = MaeDateRangeFilter(
        field_name="date",
        widget=forms.TextInput(attrs={'placeholder': 'Date', "class": "date-range-picker"})
    )


    mois = df.ChoiceFilter(
        field_name='date',
        method='filter_by_month',
        label='Mois',
        choices=[
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Mois",
                "data-hide-search": "true",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    etat = df.ChoiceFilter(
        field_name='etat',
        label="État",
        choices=BonClientCommandeDirect.ETATS,
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un état",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    client = df.ModelChoiceFilter(
        field_name='client',
        queryset=Client.objects.all(),
        label='Client',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un client",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
  

    class Meta:
        model = BonClientCommandeDirect
        fields = ["client", "mois", "date","etat"]




    def filter_by_month(self, queryset, name, value):
        if value:
            return queryset.filter(**{
                f'{name}__month': value
            })
        return queryset

class BonLivraisonDirectListFilter(df.FilterSet):
    date = MaeDateRangeFilter(
        field_name="date",
        widget=forms.TextInput(attrs={'placeholder': 'Date', "class": "date-range-picker"})
    )


    mois = df.ChoiceFilter(
        field_name='date',
        method='filter_by_month',
        label='Mois',
        choices=[
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Mois",
                "data-hide-search": "true",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    client = df.ModelChoiceFilter(
        field_name='client',
        queryset=Client.objects.all(),
        label='Client',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un client",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )

    class Meta:
        model = BonLivraisonDirect
        fields = ["client", "mois", "date"]




    def filter_by_month(self, queryset, name, value):
        if value:
            return queryset.filter(**{
                f'{name}__month': value
            })
        return queryset

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column


def get_client_queryset(request):
    if request:
        user = request.user
        # Vérifiez si l'utilisateur a des sites associés
        if user.profile.sites.exists():
            # Filtrer les clients associés aux sites de l'utilisateur
            return Client.objects.filter(
                category__type='compte',  # Catégorie "Compte"
                site__in=user.profile.sites.all()  # Utilisation de 'site' au lieu de 'sites'
            ).distinct()

    # Si la requête est absente ou si l'utilisateur n'a pas de sites associés, renvoyer une liste vide de clients
    return Client.objects.filter(
        category__type='compte',  # Catégorie "Compte"
    ).distinct()


class Filter_Facture_client_list(df.FilterSet):
    # Filtre par date (utilisation d'un filtre de type DateFromToRangeFilter)
    date = df.DateFromToRangeFilter(
        field_name="date",
        widget=forms.TextInput(attrs={'placeholder': 'Date', 'class': 'date-range-picker'}),
        label="Date (de - à)"
    )
    mois = df.ChoiceFilter(
        field_name='date',
        method='filter_by_month',
        label='Mois',
        choices=[
            ('1', 'Janvier'), ('2', 'Février'), ('3', 'Mars'), ('4', 'Avril'),
            ('5', 'Mai'), ('6', 'Juin'), ('7', 'Juillet'), ('8', 'Août'),
            ('9', 'Septembre'), ('10', 'Octobre'), ('11', 'Novembre'), ('12', 'Décembre')
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Mois",
                "data-hide-search": "true",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )
    client = df.ModelChoiceFilter(
        field_name='client',
        queryset=get_client_queryset,
        label='Client',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un client",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )

    # Filtre par numéro (utilisation d'un filtre de type CharFilter)
    numero = df.CharFilter(
        field_name='numero',
        lookup_expr='icontains',  # Filtrer par correspondance partielle
        widget=forms.TextInput(attrs={'placeholder': 'Numéro de Facture'})
    )
    statut_paiement = df.ChoiceFilter(
        field_name='statut_paiement',
        choices=FactureDirect.STATUT_PAIEMENT_CHOICES,
        label='Statut Paiement',
        widget=forms.Select(
            attrs={
                'class': 'form-select form-select-solid form-select-sm',
                "data-control": "select2",
                "data-placeholder": "Sélectionner un statut de paiement",
                "data-hide-search": "false",
                "size": "1",
                "data-dropdown-auto-width": "true",
            }
        )
    )



    class Meta:
        model = FactureDirect
        fields = ['client','date', "mois","statut_paiement", 'numero']




    def filter_by_month(self, queryset, name, value):
        if value:
            return queryset.filter(**{
                f'{name}__month': value
            })
        return queryset