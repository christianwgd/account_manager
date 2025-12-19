import django_filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Q

from account.models import Account


class AccountFilter(django_filters.FilterSet):
    class Meta:
        model = Account
        fields = ['search']

    search = django_filters.CharFilter(
        method='search_all',
        label=_('Search')
    )

    def search_all(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) |
            Q(username__icontains=value) |
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(description__icontains=value)
        )