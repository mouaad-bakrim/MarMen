
import logging

from base.models import Profile


from decimal import Decimal
from datetime import date
import json
import logging
from django.shortcuts import render, redirect
from django.contrib import messages
from django_tables2 import RequestConfig

from .models import Order, OrderLigne, Produit  # À adapter selon ton projet
from .forms import OrderForm  # Ton formulaire
from .tables import OrderListTable

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

            return redirect('direct:devis')  # Redirige correctement
    else:
        form = OrderForm(user_site=user_sites)

    # Préparation des articles
    articles = Produit.objects.all()
    articles_list = list(
        articles.values('id', 'nom', 'prix_unitaire', 'unite')
    )

    for article in articles_list:
        article['prix'] = float(article['prix']) if isinstance(article['prix'], Decimal) else article['prix']

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

