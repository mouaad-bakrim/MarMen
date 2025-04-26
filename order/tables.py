import django_tables2 as tables
from .models import Order


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


