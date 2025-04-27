from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
import math
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from num2words import num2words  # Assurez-vous d'importer num2words
from base.pdf_utils import draw_page_nb, draw_footer
from order.pdf_bc_fa import (
    draw_page_nb, draw_footer, draw_document_info, draw_orderly_simple_table, draw_header
)
from .pdf_utils_dir import draw_summary_table


def bon_de_livraison_direct_print(buffer, commandes, utilisateur_nom, document_type):
    canvas = Canvas(buffer, pagesize=A4)
    lignes_per_page = 25
    header_style = ParagraphStyle(name="header_centered", alignment=TA_CENTER, fontSize=10, fontName="Helvetica")

    for commande in commandes:
        produits = [ligne.produit for ligne in commande.lignes.all()]  # Utiliser 'produit' au lieu de 'article'
        nb_lignes = len(produits)
        page_total = math.ceil(nb_lignes / lignes_per_page)

        for i in range(page_total):
            canvas.translate(0, 30 * cm)
            canvas.setFont('Helvetica', 4)

            site = commande.client.site

            if site:
                draw_header(canvas, site, document_type)
                draw_footer(canvas, site=site)

                info_data = [
                    [u'Référence bon :', commande.bon_livraison],
                    [u'Date :', commande.date],

                ]

                canvas.saveState()
                draw_document_info(canvas, info_data, end_position=-9 * cm)
                canvas.restoreState()


                info_data_client = [
                    [u'Client :', commande.client.nom],
                    [u'Réf :', commande.client.external_id],
                    [u'ICE :', commande.client.ice if commande.client.ice else ''],
                ]
                if hasattr(commande.client, 'adresse_livraison') and commande.client.adresse_livraison:
                    info_data_client.append([u'Adresse Livraison :', commande.client.adresse_livraison])

                canvas.saveState()
                canvas.translate(11 * cm, 0)  # Décaler vers la droite
                draw_document_info(canvas, info_data_client, end_position=-6 * cm)
                canvas.restoreState()




            info_data_chauffeur = []
            if commande.chauffeur:
                if hasattr(commande.chauffeur, 'nom'):
                    info_data_chauffeur.append([u'Chauffeur :', commande.chauffeur.nom])


            if commande.modele:
                info_data_chauffeur.append([u'Modèle :', commande.modele])

            # Add matricule only if it exists
            if commande.matricule:
                info_data_chauffeur.append([u'Matricule :', commande.matricule])

            info_data_chauffeur.append([u' '])

            canvas.saveState()
            canvas.translate(11 * cm, 0)  # Décaler vers la droite
            draw_info(canvas, info_data_chauffeur, end_position=-10.5 * cm)
            canvas.restoreState()

            # En-tête du tableau
            header = [
                Paragraph(u'Article', header_style),

                Paragraph(u'Quantité ', header_style),



            ]
            data_to_print = []

            # Itération sur les produits
            for ligne in commande.lignes.all():
                produit = ligne.produit.strip()  # Supprime les espaces inutiles
                quantite = ligne.quantite
                unit = ligne.unite


                if produit.lower() == "gasoil":
                    produit_affiche = "Gasoil PPM 10"
                else:
                    produit_affiche = produit


                if quantite == int(quantite):
                    quantite_formatted = f"{int(quantite)} {unit}"
                else:
                    quantite_formatted = f"{quantite:.2f} {unit}"

                # Créer un paragraphe pour la quantité
                quantity_paragraph = Paragraph(quantite_formatted, header_style)

                # Ajouter les données au tableau
                data_to_print.append([
                    Paragraph(produit_affiche, header_style),
                    quantity_paragraph,

                ])

            # Configuration des colonnes
            col_widths = [12 * cm, 7 * cm]

            # Dessiner la table
            canvas.saveState()
            draw_orderly_simple_table(
                canvas, header, data_to_print, col_widths, lignes_per_page,
                expand_to_bottom=True, start_position=-10 * cm
            )


            # Affichage des numéros de page
            canvas.showPage()

    canvas.save()
import textwrap

def bon_de_commande_direct_print(buffer, commandes, utilisateur_nom, document_type):
    canvas = Canvas(buffer, pagesize=A4)
    lignes_per_page = 20
    header_style = ParagraphStyle(name="header_centered", alignment=TA_CENTER, fontSize=10, fontName="Helvetica")

    for commande in commandes:
        produits = [ligne.produit for ligne in commande.lignes.all()]  # Utiliser 'produit' au lieu de 'article'
        nb_lignes = len(produits)
        page_total = math.ceil(nb_lignes / lignes_per_page)

        for i in range(page_total):
            canvas.translate(0, 29.7 * cm)
            canvas.setFont('Helvetica', 4)

            site = commande.client.site

            if site:
                draw_header(canvas, site, document_type)
                draw_footer(canvas, site=site)

                # Informations générales sur le bon de commande
                info_data = [
                    [u'Référence bon :', commande.bon_commande],
                    [u'Date :', commande.date],

                ]

            canvas.saveState()
            draw_document_info(canvas, info_data, end_position=-7 * cm)
            canvas.restoreState()

            def wrap_text(text, width=40):
                """Enveloppe le texte à une largeur maximale."""
                if text:
                    return '\n'.join(textwrap.wrap(text, width=width))
                return ''
            # Informations du client
            info_data_client = [
                [u'Client :', commande.client.nom],
                [u'Réf :', commande.client.external_id],
                [u'ICE :', commande.client.ice if commande.client.ice else ''],
                [u'Adresse Livresion :', wrap_text(commande.client.adresse_livraison, width=40)],
                [u'Adresse Facturation:', wrap_text(commande.client.adresse_facturation, width=40)],
            ]

            canvas.saveState()
            canvas.translate(8.5 * cm, 0)
            draw_document_info(canvas, info_data_client, end_position=-7 * cm)
            canvas.restoreState()

            # Header of the table
            header = [
                Paragraph(u'Article', header_style),
                Paragraph(u'Quantité', header_style),
                Paragraph(u'Unité', header_style),
                Paragraph(u'Prix Ttc', header_style),
                Paragraph(u'Remise', header_style),
                Paragraph(u'TVA', header_style),
                Paragraph(u'Montant TTC', header_style),
            ]

            data_to_print = []
            montant_ht_10 = 0
            montant_ht_20 = 0
            montant_tva_10 = 0
            montant_tva_20 = 0
            montant_ttc_10 = 0
            montant_ttc_20 = 0

            # Iterate over the articles for the BonCommande
            for ligne in commande.lignes.all():  # Boucle sur les lignes du bon de commande
                produit = ligne.produit
                prix_unitaire = ligne.prix
                remise = ligne.remise  # Remise, faut-il l'utiliser correctement ?

                total = ligne.quantite * prix_unitaire  # Calculer le total sans la remise (remise peut être soustraite plus tard si nécessaire)
                # Assurez-vous que 'tva' est un nombre Decimal
                tva = commande.tva
                unite_formatted = ligne.unite

                # Convertir 'tva' en Decimal, si ce n'est pas déjà un nombre Decimal
                tva = Decimal(tva) if tva else Decimal(0.0)  # Utiliser Decimal(0.0) si 'tva' est vide ou invalide

                # Convertir 'prix_unitaire' et 'quantite' en Decimal si nécessaire
                prix_unitaire = Decimal(prix_unitaire)
                quantite = Decimal(ligne.quantite)

                total_article = quantite * prix_unitaire  # Calcul du total par article
                total_article_apres_remise = total_article - (total_article * (Decimal(remise) / Decimal(100)))


                total_with_tva = total_article_apres_remise
                total_with_ht = total_article_apres_remise / (Decimal(1) + tva / Decimal(100))
                total_tva = total_with_tva - total_with_ht


                unit = " "  # Unité par défaut
                if ligne.quantite == int(ligne.quantite):
                    quantite_formatted = f"{int(ligne.quantite)}{unit}"  # Format entier avec unité
                else:
                    quantite_formatted = f"{ligne.quantite:.2f}{unit}"  # Format décimal avec unité

                # Formater le prix unitaire et le total
                prix_unitaire_formatted = f"{prix_unitaire:.2f} "  # Format avec deux décimales
                total_formatted = f"{total_with_tva:.2f}"  # Format total avec deux décimales

                # Formater la remise et la TVA
                remise_formatted =f"{remise:.0f}%"  # Remise formatée
                tva_formatted = f"{tva:.0f}%"  # TVA formatée (en pourcentage)

                # Créer les paragraphes pour chaque valeur
                quantity_paragraph = Paragraph(quantite_formatted, header_style)
                price_paragraph = Paragraph(prix_unitaire_formatted, header_style)
                remise_paragraph = Paragraph(remise_formatted, header_style)
                unite_paragraph = Paragraph(unite_formatted, header_style)
                tva_paragraph = Paragraph(tva_formatted, header_style)
                total_paragraph = Paragraph(total_formatted, header_style)

                # Ajouter les données formatées dans la liste à imprimer
                data_to_print.append([
                    produit.strip(),

                    quantity_paragraph,
                    unite_paragraph,
                    price_paragraph,
                    remise_paragraph,
                    tva_paragraph,
                    total_paragraph,
                ])

                if tva == 10:
                    montant_ht_10 += total_with_ht
                    montant_tva_10 += total_tva
                    montant_ttc_10 += total_with_tva
                elif tva == 20:
                    montant_ht_20 += total_with_ht
                    montant_tva_20 += total_tva
                    montant_ttc_20 += total_with_tva
            total_ttc = montant_ttc_10 + montant_ttc_20
            totals = {
                'montant_ht_10': montant_ht_10,
                'montant_ht_20': montant_ht_20,
                'montant_tva_10': montant_tva_10,
                'montant_tva_20': montant_tva_20,
                'montant_ttc_10': montant_ttc_10,
                'montant_ttc_20': montant_ttc_20,
                'total_ttc': total_ttc,

            }

                # Définir les largeurs des colonnes
            col_widths = [7 * cm, 2 * cm,1.5 * cm, 2 * cm, 2 * cm, 1.5 * cm, 3 * cm]  # Ajuster les largeurs des colonnes


            canvas.saveState()
            draw_orderly_simple_table(
                canvas, header, data_to_print, col_widths, lignes_per_page,
                expand_to_bottom=True, start_position=-8.5 * cm
            )
            canvas.restoreState()
            canvas.saveState()
            draw_summary_table(canvas, totals, start_position=-22.5 * cm)
            canvas.restoreState()

            # Add page number
            canvas.showPage()

    canvas.save()

from decimal import Decimal
def bon_de_devis_direct_print(buffer, commandes, utilisateur_nom, document_type):
    canvas = Canvas(buffer, pagesize=A4)
    lignes_per_page = 20
    header_style = ParagraphStyle(name="header_centered", alignment=TA_CENTER, fontSize=10, fontName="Helvetica")

    for commande in commandes:
        produits = [ArticleSite.article for ArticleSite in commande.devislinge_set.all()]
        nb_lignes = len(produits)
        page_total = math.ceil(nb_lignes / lignes_per_page)

        for i in range(page_total):
            canvas.translate(0, 29.7 * cm)
            canvas.setFont('Helvetica', 4)

            site = commande.client.site

            if site:
                draw_header(canvas, site, document_type)
                draw_footer(canvas, site=site)

                info_data = [
                    [u'Référence bon :', commande.code],
                    [u'Date :', commande.date],
                ]

            canvas.saveState()
            draw_document_info(canvas, info_data, end_position=-7 * cm)
            canvas.restoreState()

            # Informations du client
            info_data_client = [
                [u'Client :', commande.client.nom],
                [u'Réf :', commande.client.external_id],
                [u'ICE :', commande.client.ice if commande.client.ice else '']
            ]

            canvas.saveState()
            canvas.translate(11 * cm, 0)  # Décaler vers la droite
            draw_info(canvas, info_data_client, end_position=-6 * cm)
            canvas.restoreState()

            # Header of the table
            header = [
                Paragraph(u'Article', header_style),
                Paragraph(u'Quantité', header_style),
                Paragraph(u'Prix TTC', header_style),
                Paragraph(u'Remise', header_style),  # Correction de "Remais" en "Remise"
                Paragraph(u'TVA', header_style),
                Paragraph(u'Total TTC', header_style),
            ]

            data_to_print = []

            total_commande = 0  # Initialiser le total de la commande
            montant_ht_10 = 0
            montant_ht_20 = 0
            montant_tva_10 = 0
            montant_tva_20 = 0
            montant_ttc_10 = 0
            montant_ttc_20 = 0

            # Iterate over the articles for the BonLivraisonClinet
            for article in commande.devislinge_set.all():
                if article.produit:
                    produit = article.produit
                else:
                    produit = article.article


                prix_unitaire = article.prix
                remise = article.remise

                quantite = article.quantite

                # Assurez-vous que 'tva' est un nombre Decimal
                tva = (
                    article.article.article.category.tva
                    if article and article.article and article.article.article and article.article.article.category
                    else (produit.tva if produit else Decimal(0))
                )

                # Convertir 'tva' en Decimal, si ce n'est pas déjà un nombre Decimal
                tva = Decimal(tva) if tva else Decimal(0.0)  # Utiliser Decimal(0.0) si 'tva' est vide ou invalide

                # Convertir 'prix_unitaire' et 'quantite' en Decimal si nécessaire
                prix_unitaire = Decimal(prix_unitaire)
                quantite = Decimal(article.quantite)

                total_article = quantite * prix_unitaire  # Calcul du total par article

                # Appliquer la remise si nécessaire
                total_article_apres_remise = total_article - (total_article * (Decimal(remise) / Decimal(100)))


                # Calculer le montant total avec TVA
                total_with_tva = total_article_apres_remise
                total_with_ht = total_article_apres_remise / (Decimal(1) + tva / Decimal(100))
                total_tva = total_with_tva - total_with_ht


                # Formater les valeurs
                unit = " "  # Unité par défaut
                quantite_formatted = f"{quantite:.2f}{unit}" if quantite != int(quantite) else f"{int(quantite)}{unit}"
                prix_unitaire_formatted = f"{prix_unitaire:.2f} "
                remise_formatted = f"{remise:.0f}%"
                tva_formatted = f"{tva:.0f}%"
                total_formatted = f"{total_with_tva:.2f}"
                total_tva_formatted = f"{total_tva:.2f}"
                if article.article and article.article.article:
                    produit_name = article.article.article
                else:
                    produit_name =  article.produit

                prix_unitaire = article.prix
                remise = article.remise
                # Ajouter les données formatées pour la table
                data_to_print.append([
                    produit_name,
                    Paragraph(quantite_formatted, header_style),
                    Paragraph(prix_unitaire_formatted, header_style),
                    Paragraph(remise_formatted, header_style),
                    Paragraph(tva_formatted, header_style),
                    Paragraph(total_formatted, header_style),
                ])

                total_commande += total_with_tva

                if tva == 10:
                    montant_ht_10 += total_with_ht
                    montant_tva_10 += total_tva
                    montant_ttc_10 += total_with_tva
                elif tva == 20:
                    montant_ht_20 += total_with_ht
                    montant_tva_20 += total_tva
                    montant_ttc_20 += total_with_tva
                    # Calcul du total TTC général
            total_ttc = montant_ttc_10 + montant_ttc_20

            # Création du dictionnaire des totaux pour chaque taux
            totals = {
                'montant_ht_10': montant_ht_10,
                'montant_ht_20': montant_ht_20,
                'montant_tva_10': montant_tva_10,
                'montant_tva_20': montant_tva_20,
                'montant_ttc_10': montant_ttc_10,
                'montant_ttc_20': montant_ttc_20,
                'total_ttc': total_ttc,

            }


            col_widths = [5 * cm, 3 * cm, 2 * cm, 3 * cm, 3 * cm, 3 * cm]

            # Draw the table
            canvas.saveState()
            draw_orderly_simple_table(
                canvas, header, data_to_print, col_widths, lignes_per_page,
                expand_to_bottom=True, start_position=-8.5 * cm
            )
            canvas.restoreState()
            canvas.saveState()
            draw_summary_table(canvas, totals, start_position=-22.5 * cm)
            canvas.restoreState()

            # Add page number


            # Optionally, add the total at the end of the page
            total_commande_formatted = f"{total_commande:.2f}"
            canvas.drawString(16 * cm, 2 * cm, f"Total de la commande: {total_commande_formatted} EUR")

            canvas.showPage()  # Start a new page if necessary

    canvas.save()