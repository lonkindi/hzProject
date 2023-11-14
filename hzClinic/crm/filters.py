from decimal import Decimal
from django.db.models import Q
import django_filters
from crm.models import Candidate


class CandidateFilter(django_filters.FilterSet):
    query = django_filters.CharFilter(method='universal_search',
                                      label="")

    class Meta:
        model = Candidate
        fields = ['query']

    def universal_search(self, queryset, name, value):
        if value.replace(".", "", 1).isdigit():
            value = Decimal(value)
            return Candidate.objects.filter(
                Q(Sname=value) | Q(phoneNumber=value)
            )

        return Candidate.objects.filter(
            Q(Sname__icontains=value) | Q(phoneNumber__icontains=value)
        )
