
import logging

from base.models import Profile


from decimal import Decimal
from datetime import date
import json
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django_tables2 import RequestConfig

from base.utils import PagedFilteredTableView
from .models import Order, OrderLigne, Produit, Devis  # À adapter selon ton projet
from .forms import OrderForm  # Ton formulaire
from .tables import OrderListTable, DevisListTable

logger = logging.getLogger(__name__)


def add_order(request):
    logger.debug("Début de la vue add_order")

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    user_sites = profile.sites.all() if profile and profile.sites.exists() else None
    if not user_sites:
        messages.error(request, "Aucun site associé à votre profil.")
        return redirect('some_error_page')  # Remplacer par une page d'erreur correcte

    if request.method == 'POST':
        form = OrderForm(request.POST, user_site=user_sites)
        if form.is_valid():
            order = form.save(commit=False)
            order.site = user_sites.first()
            order.client = form.cleaned_data.get('client')  # Assure-toi que ton form a un champ 'client'
            order.date = date.today()
            order.save()

            logger.debug("Données du formulaire validées : %s", {field: form.cleaned_data.get(field) for field in form.fields})

            article_ids = request.POST.getlist('articles[]')
            prix_list = request.POST.getlist('prix[]')
            remise_list = request.POST.getlist('remise[]')
            quantites_list = request.POST.getlist('quantite[]')

            if article_ids and len(article_ids) == len(prix_list) == len(remise_list) == len(quantites_list):
                for i in range(len(article_ids)):
                    try:
                        produit = Produit.objects.get(id=article_ids[i])

                        prix = Decimal(prix_list[i]) if prix_list[i] else Decimal(0)
                        quantite = int(quantites_list[i]) if quantites_list[i] else 0
                        remise_value = Decimal(remise_list[i]) if remise_list[i] else Decimal(0)

                        if prix < 0 or quantite <= 0:
                            messages.error(request, "Le prix et la quantité doivent être des valeurs positives.")
                            raise ValueError("Prix ou quantité invalide.")

                        OrderLigne.objects.create(
                            order=order,
                            produit=produit,
                            prix=prix,
                            quantite=quantite,
                            remise=remise_value,
                            montant=(prix * quantite) * (1 - (remise_value / 100))
                        )
                    except Produit.DoesNotExist:
                        messages.error(request, f"Produit avec ID {article_ids[i]} n'existe pas.")
                    except ValueError as e:
                        messages.error(request, str(e))
            else:
                messages.error(request, "Erreur dans les listes d'articles, prix, quantités et remises.")

            return redirect('order:add_order')  # Redirige correctement
    else:
        form = OrderForm(user_site=user_sites)

    # Préparation des articles
    articles = Produit.objects.all()
    articles_list = list(
        articles.values('id', 'nom', 'prix_unitaire', 'unite')
    )

    for article in articles_list:
        article['prix_unitaire'] = float(article['prix_unitaire']) if isinstance(article['prix_unitaire'], Decimal) else article['prix_unitaire']

    today = date.today()
    order = Order.objects.filter(date=today)
    table = OrderListTable(order)
    RequestConfig(request).configure(table)

    return render(request, 'order/add_order.html', {
        'form': form,
        'user_sites': user_sites,
        'articles': articles,
        'table': table,
        'articles_json': json.dumps(articles_list),
        'active_item': 'lubrifiant_direct',
        'active_menu': 'direct',
    })


class Devis_direct(PagedFilteredTableView):
    permission_required = 'direct.view_boncommandedirect'
    model = Devis
    table_class = DevisListTable
    #formhelper_class = BonCommandeDirectListFormHelper
    #filter_class = BonDevisDirectListFilter
    template_name = 'devis/devis_direct.html'
    active_item = 'bon_devis_list'
    active_menu = 'factures'

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        # Vérification des permissions de l'utilisateur
        if user.is_superuser:
            logger.debug("Utilisateur superuser, affichage de tous les devis.")
            queryset = queryset.order_by(
                '-date')
            return queryset

        # Vérification du site utilisateur
        if hasattr(user, 'profile'):
            user_sites = user.profile.sites.all()  # Récupérer tous les sites associés à l'utilisateur
            if user_sites.exists():
                queryset = queryset.filter(client__site__in=user_sites)
                logger.debug("Filtrage des devis pour les sites de l'utilisateur.")
            else:
                queryset = queryset.none()
                logger.debug("Aucun site associé à l'utilisateur, aucun devis à afficher.")

        # Tri des devis par date de création (du plus récent au plus ancien)
        queryset = queryset.order_by('-date')  # Tri descendant par date de création (le plus récent en premier)

        # Log du nombre de résultats trouvés après filtrage
        logger.debug("Nombre de devis trouvés : %d", queryset.count())
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Récupérer les bons de commande filtrés
        bons_commande_direct = self.get_queryset()

        # Récupérer les sites de l'utilisateur
        user_sites = None
        try:
            profile = Profile.objects.get(user=self.request.user)
            user_sites = profile.sites.all()
            logger.debug("Sites associés au profil de l'utilisateur : %s", user_sites)
        except Profile.DoesNotExist:
            logger.warning("Profil de l'utilisateur introuvable, aucun site associé.")

        # Passer 'request' au filtre
#        filter = self.filter_class(self.request.GET, queryset=bons_commande_direct, request=self.request)

        # Configuration de la table


        # Mise à jour du contexte
        context.update({
            'active_item': self.active_item,
            'active_menu': self.active_menu,
            'user_sites': user_sites,

        })

        return context