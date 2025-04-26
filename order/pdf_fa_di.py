from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
import math
import locale
from reportlab.lib.styles import getSampleStyleSheet
from .pdf_utils_dir import draw_page_nb, draw_footer,draw_info, draw_document_info, draw_orderly_simple_table, draw_header, \
    draw_summary_table, background_text


def draw_logo(canvas, site):
    # Récupérer le chemin du logo depuis le modèle 'Site'
    logo_path = site.societe_obj.logo.path if site.societe_obj.logo else None

    if logo_path:
        page_width, page_height = A4
        logo_width = 5 * cm
        logo_height = 5 * cm

        # Positionner l'image au centre de la page
        x = (page_width - logo_width) / 2
        y = (page_height - logo_height) - 6 * cm  # Ajustez la position verticale

        # Ajouter l'image au centre de la page
        canvas.drawImage(logo_path, x, y, width=logo_width, height=logo_height)

import textwrap


def wrap_text(text, width=30):
    """Enveloppe le texte à une largeur maximale."""
    if text:
        return '\n'.join(textwrap.wrap(text, width=width))
    return ''
def facture_direct_print(buffer, factures):
    """ Draws the invoice """
    canvas = Canvas(buffer, pagesize=A4)
    lignes_per_page = 21
    locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')  # Ensure that this locale is installed on the system

    for facture in factures:
        nb_lignes = facture.bons_livraison_direct.count()  # Number of lines in the invoice
        page_total = math.ceil(nb_lignes / lignes_per_page)

        # Extraire le mois des bons de livraison
        mois_bons = []
        for bon_livraison in facture.bons_livraison_direct.all():
            mois_formatte = bon_livraison.date.strftime('%B %Y').capitalize()
            mois_bons.append(mois_formatte)

        mois_unique = set(mois_bons)
        mois_affiche = ', '.join(mois_unique)  # Concatenate months if there are multiple


        for i in range(page_total):
            canvas.translate(0, 29.7 * cm)
            canvas.setFont('Helvetica', 9)

            canvas.saveState()
            background_text(canvas, "STATION")
            canvas.restoreState()

            canvas.saveState()
            draw_logo(canvas, site=facture.client.site)
            canvas.restoreState()

            canvas.saveState()
            draw_header(canvas, site=facture.client.site)
            canvas.restoreState()

            canvas.saveState()
            draw_footer(canvas, site=facture.client.site)
            canvas.restoreState()


            info_data_facture = [
                [u'FACTURE N° :', facture.numero],
                [u'DATE :', facture.date.strftime('%d/%m/%Y')],
                [u'DESCRIPTION :', mois_affiche],  # Affichage des mois des bons de livraison
            ]

            # Dessin des informations de la facture
            canvas.saveState()
            draw_document_info(canvas, info_data_facture, end_position=-5.8 * cm)
            canvas.restoreState()

            # Informations du client
            info_data_client = []

            # Ajouter le nom du client
            if facture.client.nom:
                info_data_client.append([u'Client :', facture.client.nom])

            # Ajouter la référence si elle est présente
            if facture.bon_commande:
                info_data_client.append([u'Bon commande :', facture.bon_commande])

            # Ajouter l'ICE si elle est présente
            if facture.client.ice:
                info_data_client.append([u'ICE :', facture.client.ice])
            if facture.client.adresse_facturation:
                info_data_client.append( [u'Adresse Facturation:', wrap_text(facture.client.adresse_facturation, width=30)])
            # Vous pouvez ensuite passer info_data_client à votre template ou l'afficher

            canvas.saveState()
            canvas.translate(10.5 * cm, 0)  # Décaler vers la droite
            draw_info(canvas, info_data_client, end_position=-6.5 * cm)
            canvas.restoreState()

            info_data = [
                [facture.montant_lettres],
            ]

            canvas.saveState()
            draw_document_info(canvas, info_data, end_position=-27.8 * cm)
            canvas.restoreState()

            headers = [u'Date',u'Bon Livraison', u'Produit', u'Quantité',u'Unité', u'P.U TTC', u'Remise', u'Tax TVA', u'Montant TTC']
            data_to_print = []

            # Initialisation des montants pour chaque taux de TVA
            montant_ht_10 = 0
            montant_ht_20 = 0
            montant_tva_10 = 0
            montant_tva_20 = 0
            montant_ttc_10 = 0
            montant_ttc_20 = 0

            # Data collection
            for bon_livraison in facture.bons_livraison_direct.all():
                canvas.saveState()
                background_text(canvas, "STATION")
                canvas.restoreState()

                canvas.saveState()
                draw_logo(canvas, site=facture.client.site)
                canvas.restoreState()

                # Accédez aux lignes du bon de livraison pour obtenir les produits
                for ligne in bon_livraison.lignes.all():
                    product_name = ligne.produit.strip()
                    if product_name.lower() == "gasoil":
                        produit_affiche = "Gasoil PPM 10"
                    else:
                        produit_affiche = product_name
                    date = bon_livraison.date
                    quantity = ligne.quantite  # Utilisez la quantité de la ligne
                    unite = ligne.unite  #
                    formatted_quantity = "{:.2f}".format(quantity)

                    tva = bon_livraison.tva
                    tva_percentage = int(float(tva))
                    montant_ttc = ligne.montant_ttc  # Utilisez le montant TTC de la ligne
                    montant_tva = ligne.montant_tva  # Utilisez le montant TVA de la ligne
                    price = ligne.prix

                    remise = ligne.remise

                    remise_formatted = f"{remise:.0f}%"
                    tva_formatted = f"TVA {tva_percentage}%"
                    data_to_print.append(
                        [date, bon_livraison.bon_livraison, produit_affiche, formatted_quantity, unite, price,
                         remise_formatted,
                         tva_formatted,
                         montant_ttc])

                    # Calcul des montants selon le taux de TVA
                    if bon_livraison.tva == 10:
                        montant_ht_10 += ligne.montant_ht
                        montant_tva_10 += ligne.montant_tva
                        montant_ttc_10 += ligne.montant_ttc
                    elif bon_livraison.tva == 20:
                        montant_ht_20 += ligne.montant_ht
                        montant_tva_20 += ligne.montant_tva
                        montant_ttc_20 += ligne.montant_ttc

            # Calcul du total TTC général
            total_ttc = montant_ttc_10 + montant_ttc_20   # Ajout de la main d'œuvre

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

            canvas.saveState()
            draw_orderly_simple_table(canvas, headers, data_to_print,
                                      [2 * cm,3.3 * cm, 4.5 * cm, 1.7 * cm, 1 * cm, 1.5 * cm, 1.3 * cm, 1.5 * cm, 2.2 * cm],
                                      lignes_per_page, expand_to_bottom=True, start_position=-7 * cm)
            canvas.restoreState()

            # Position pour le texte "Arrêté la présente facture à la somme de :"
            canvas.setFont('Helvetica-Bold', 10)
            position_y = -26.8 * cm  # Ajustez cette position en fonction de votre mise en page
            canvas.drawString(1 * cm, position_y, f"Arrêté la présente facture à la somme de :")

            canvas.saveState()
            # background_text(canvas, "FACTURE")  # Adjust the text as needed
            canvas.restoreState()

            canvas.saveState()
            draw_summary_table(canvas, totals, start_position=-22.5 * cm)
            canvas.restoreState()

            # Displaying page numbers
            draw_page_nb(canvas, i + 1, page_total)
            canvas.showPage()

    canvas.save()


