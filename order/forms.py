
from django import forms
from client.models import Client
from order.models import Order
from produit.models import Produit

from datetime import date

class OrderForm(forms.ModelForm):
    produit = forms.ModelMultipleChoiceField(
        queryset=Produit.objects.none(),
        widget=forms.SelectMultiple,
        required=False,
    )

    class Meta:
        model = Order
        fields = [
            'date', 'client'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user_site = kwargs.pop('user_site', None)
        super(OrderForm, self).__init__(*args, **kwargs)

        self.fields['date'].initial = date.today()


