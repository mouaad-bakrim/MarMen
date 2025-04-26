import django_tables2 as tables
from .models import Order, Devis


class OrderListTable(tables.Table):
    client = tables.Column(
        accessor='client',
        verbose_name='Client',
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center "},
            "tf": {"class": "text-end fw-bolder text-nowrap"},

        }
    )
    site = tables.Column(
        accessor='site',
        verbose_name='Site',
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center "},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
        }
    )

    date = tables.DateColumn(
        format='d-m-Y',
        accessor='date',
        verbose_name='Date',
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center"},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
            "footer": {"class": "text-center"},
        },

    )

    montant = tables.Column(
        accessor='montant',  # Accès direct au champ du modèle
        verbose_name='Montant',
        orderable=True,
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center "},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
        },
    )
    quantite = tables.Column(
        verbose_name='Quantité totale',
        orderable=False,
        accessor=tables.A('quantite_totale'),  # Utilisation de la propriété personnalisée
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center "},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
        },
    )

    class Meta:
        model = Order
        fields = ('date','site','client', 'quantite', 'montant')  # Définir les champs à afficher
        attrs = {
            "class": "table table-bordered table-striped table-hover text-gray-600 table-heading table-datatable dataTable g-3 fs-7"
        }

        per_page = 100
        template_name = 'django_tables2/bootstrap.html'



class DevisListTable(tables.Table):
    date = tables.DateColumn(
        format='d/m/Y',
        verbose_name="Date",
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center "},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
        }
    )
    client = tables.Column(
        accessor='client',
        verbose_name='Client',
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center "},
            "tf": {"class": "text-end fw-bolder text-nowrap"},

        }
    )

    etat = tables.TemplateColumn(
        template_code='''
                  {% if record.etat == "draft" %}
                      <span class="badge badge-warning fw-bolder w-60 fs-8">{{ record.get_etat_display }}</span>
                  {% elif record.etat == "accepted" %}
                      <span class="badge badge-success fw-bolder w-60 fs-8">{{ record.get_etat_display }}</span>
                  {% elif record.etat == "rejected" %}
                      <span class="badge badge-danger fw-bolder w-60 fs-8">{{ record.get_etat_display }}</span>
                  {% else %}
                      <span class="badge badge-dark fw-bolder w-60 fs-8">{{ record.get_etat_display }}</span>
                  {% endif %}
              ''',
        accessor='etat',
        verbose_name='État',
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center"},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
        }
    )
    code = tables.TemplateColumn(
        '<a href="">{{ record.code }}</a>',
        verbose_name="Bon de Devis"
    )

    quantite = tables.Column(
        verbose_name="Quantité Totale",
        accessor='get_total_quantite',
        attrs = {
            "th": {"class": "text-center"},
            "td": {"class": "text-center"},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
        }
    )
    montant_total = tables.Column(
        verbose_name="Montant Total",
        accessor='get_total_montant',
        attrs={
            "th": {"class": "text-center"},
            "td": {"class": "text-center"},
            "tf": {"class": "text-end fw-bolder text-nowrap"},
        }
    )

    class Meta:
        model = Devis
        fields = ("code", "date", "client", "quantite", "montant_total", "etat")
        attrs = {
            "class": "table table-bordered table-striped table-hover text-gray-600 table-heading table-datatable dataTable g-3 fs-7"
        }
        per_page = 100

