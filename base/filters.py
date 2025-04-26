import django_filters as df
from base.models import Site
from django import forms
from django.utils.encoding import force_str
from django.core.exceptions import ValidationError
import datetime
from crum import get_current_user
from django.db.models import Q, Func, F, OuterRef
from django.contrib.postgres.aggregates import ArrayAgg


def authorized_sites(request):
    return Site.objects.all().order_by('nom')




class SiteListFilter(df.FilterSet):
    nom = df.CharFilter(widget=forms.TextInput(attrs={'placeholder': 'Nom'}), lookup_expr='icontains')

    # external_id = df.CharFilter(widget=forms.TextInput(attrs={'placeholder': 'Numéro de commande'}),lookup_expr= 'icontains')
    # site = df.ModelChoiceFilter(queryset = Site.objects.order_by('nom'), empty_label = "--- Site ---")
    # date= df.DateFilter(field_name="date", widget=forms.DateInput(attrs={'placeholder': 'Date de commande'}))
    class Meta:
        model = Site
        fields = {}


class TreeNodeCharFilter(df.CharFilter):
    def get_filter_predicate(self, v):
        if v in self.parent_choices:
            return Q(**{self.field_name: v}) | Q(**{self.parent_field_name: v})
        else:
            return Q(**{self.field_name: v})



# Permet l'afichage d'un champ de période avec un séparateur
class MaeDateRangeFilter(df.Filter):
    field_class = forms.CharField

    def filter(self, qs, value):
        SEPARATOR = " au "

        if not value or value in df.constants.EMPTY_VALUES:
            return qs

        unicode_value = force_str(value, strings_only=True)
        if isinstance(unicode_value, str):
            value = unicode_value.strip()
        else:
            return qs

        if SEPARATOR in value:
            str_dates = value.split(SEPARATOR, 2)

            try:
                start = datetime.datetime.strptime(str_dates[0].strip(), '%d/%m/%Y').date()
            except ValidationError as e:
                return qs
                # raise ValidationError('Début de période incorrect: '+ e.message, e.code)

            try:
                stop = datetime.datetime.strptime(str_dates[1].strip(), '%d/%m/%Y').date()
            except ValidationError as e:
                return qs
                # raise ValidationError('Fin de période incorrect: '+ e.message, e.code)

            if start is not None and stop is not None:
                self.lookup_expr = "range"
                value = (start, stop)
            elif start is not None:
                self.lookup_expr = "gte"
                value = start
            elif stop is not None:
                self.lookup_expr = "lte"
                value = stop
        else:
            # Cas une seule date
            try:
                start = datetime.datetime.strptime(value, '%d/%m/%Y').date()
                self.lookup_expr = "range"
                value = (start, start)
                return super().filter(qs, value)
            except ValidationError as e:
                return qs
        return super().filter(qs, value)
