import django_filters
from .models import Trip

class TripFilter(django_filters.FilterSet):
    origin = django_filters.CharFilter(field_name='origin', lookup_expr='icontains')
    destination = django_filters.CharFilter(field_name='destination', lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    date = django_filters.DateFilter(field_name='date', lookup_expr='date')
    
    class Meta:
        model = Trip
        fields = ['origin', 'destination', 'min_price', 'max_price', 'date']
