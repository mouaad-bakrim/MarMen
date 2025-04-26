from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
import math
import locale
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph

from base.pdf_bc_utils import draw_page_nb, draw_footer, draw_document_info, draw_orderly_simple_table, draw_header, \
    draw_summary_table, background_text
import textwrap
def wrap_text(text, width=40):
    """Enveloppe le texte à une largeur maximale."""
    if text:
        return '\n'.join(textwrap.wrap(text, width=width))
    return ''
from decimal import Decimal
def bon_de_commande_achate_direct_print(buffer, commandes, utilisateur_nom, document_type):
    """ Draws the purchase order """
    canvas = Canvas(buffer, pagesize=A4)
    lignes_per_page = 20  # Number of lines per page
    lignes_page = 1  # Number of lines per page for table

    for commande in commandes:

        # Calculating number of lines needed to display products/articles (adjust as per your model)
        related_items = lignes_page  # This is an integer, representing quantity
        nb_lignes = related_items  # Directly assign the quantity as the number of lines
        page_total = math.ceil(nb_lignes / lignes_page)

        for i in range(page_total):
            canvas.translate(0, 29.7 * cm)  # Adjust to fit content on the page
            canvas.setFont('Helvetica', 10)

            # Get the site associated with the command
            site = commande.site
            if site:
                draw_header(canvas, site, document_type)
                draw_footer(canvas, site=site)  # Pass the correct site to the footer
                info_data = [
                    [u'Adresse de Livraision  :', site.nom],
                ]
            else:
                info_data = [
                    [u'Adresse de Livraision  :', 'Aucun site associé'],  # Handle the case where no site is associated
                ]

            # Draw document information
            canvas.saveState()
            draw_document_info(canvas, info_data, end_position=-7.6 * cm)
            canvas.restoreState()


            info_data_fourniseur = [
                [u'Fournisseur :', commande.fournisseur.nom],

                [u'ICE :', commande.fournisseur.ice if commande.fournisseur.ice else ''],
                [u'Adresse :', wrap_text(commande.fournisseur.adresse, width=40)],
                [u'Tél :', commande.fournisseur.telephone],
                [u'Fax :', commande.fournisseur.fix],

            ]

            canvas.saveState()
            canvas.translate(11 * cm, 0)  # Décaler vers la droite
            draw_document_info(canvas, info_data_fourniseur, end_position=-7.5 * cm)
            canvas.restoreState()

            # Drawing order number and date
            info_data = [
                [u'N° de Confirmation du bon de commande :', commande.bon_commande],
            ]
            canvas.saveState()
            draw_document_info(canvas, info_data, end_position=-9.5 * cm)
            canvas.restoreState()

            # Draw the table headers for order info
            headers = [u'Référence ', u'Date de Commande', u'Validée par']
            data_to_print = []
            reference = commande.numero
            date = commande.date.strftime('%d/%m/%Y')
            responsable = utilisateur_nom
            data_to_print.append([reference, date, responsable])

            col_widths = [9 * cm, 5 * cm, 5 * cm]
            canvas.saveState()
            draw_orderly_simple_table(canvas, headers, data_to_print, col_widths, lignes_page,
                                      expand_to_bottom=True, start_position=-9.8 * cm)
            canvas.restoreState()

            # Create a centered style for "Quantité" and "Date" columns
            header_style = ParagraphStyle(name="header_centered", alignment=TA_CENTER, fontSize=10,
                                          fontName="Helvetica")
            header = [
                Paragraph(u'Description', header_style),
                Paragraph(u'Taxes', header_style),
                Paragraph(u'Quantité', header_style),
                Paragraph(u'Prix Unit', header_style),
                Paragraph(u'Prix Net', header_style),
                Paragraph(u'Date', header_style)
            ]
            data_to_print = []

            # Fill in the data for each order row
            product_name = commande.produit.nom  # Adjust this according to your model's field
            tax = Paragraph("TVA 10%", header_style)
            Prix = Paragraph(f"{commande.prix_ttc}", header_style)
            montant = Paragraph(f"{commande.montant}", header_style)
            quantity = Paragraph(f"{commande.quantite} ", header_style)
            date = Paragraph(commande.date.strftime('%d/%m/%Y'), header_style)  # Centered date
            data_to_print.append([product_name, tax,quantity,Prix,montant, date])

            tva_rate = Decimal('1.1')  # TVA à 10% (1 + 0.1)
            montant_ht = commande.montant / tva_rate
            montant_tva = commande.montant - montant_ht
            montant_ttc = commande.montant

            montant_ht_str = f"{montant_ht:.2f} DH"
            montant_tva_str = f"{montant_tva:.2f} DH"
            montant_ttc_str = f"{montant_ttc:.2f} DH"
            # Column widths for the table
            col_widths = [4 * cm, 3 * cm, 3 * cm,3 * cm, 3 * cm, 3 * cm]

            # Draw the table with the order lines
            canvas.saveState()
            draw_orderly_simple_table(
                canvas, header, data_to_print, col_widths, lignes_per_page,
                expand_to_bottom=True, start_position=-11.5 * cm
            )
            canvas.restoreState()

            summary_header = ['Montant']  # Une seule colonne pour le titre
            summary_data = [
                ['Montant HT: ' + f"{montant_ht_str}"],
                ['Montant TVA: ' + f"{montant_tva_str}"],
                ['Montant TTC: ' + f"{montant_ttc_str}"],
            ]
            summary_col_widths = [6 * cm]  # Largeur suffisante pour le texte

            canvas.saveState()
            canvas.translate(13 * cm, 0)
            draw_orderly_simple_table(
                canvas, summary_header, summary_data, summary_col_widths,
                lignes_per_page, expand_to_bottom=False, start_position=-24.8 * cm
            )
            canvas.restoreState()

            # Add page number
            draw_page_nb(canvas, i + 1, page_total)
            canvas.showPage()

    canvas.save()
