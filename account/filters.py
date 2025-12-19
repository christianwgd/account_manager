import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from account.models import Account


class CompanyFilter(django_filters.FilterSet):
    class Meta:
        model = Account
        fields = [
            'name', 'type'
        ]

    author = django_filters.CharFilter(
        lookup_expr='icontains',
        label=_('Name contains')
    )