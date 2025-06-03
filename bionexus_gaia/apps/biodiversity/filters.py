from django_filters import rest_framework as filters
from .models import BiodiversityRecord

class BiodiversityRecordFilter(filters.FilterSet):
    """
    Filter for BiodiversityRecord model.
    """
    species_name = filters.CharFilter(lookup_expr='icontains')
    common_name = filters.CharFilter(lookup_expr='icontains')
    location_name = filters.CharFilter(lookup_expr='icontains')
    observation_date_min = filters.DateTimeFilter(field_name='observation_date', lookup_expr='gte')
    observation_date_max = filters.DateTimeFilter(field_name='observation_date', lookup_expr='lte')
    is_verified = filters.BooleanFilter()
    contributor_id = filters.CharFilter(field_name='contributor__id')
    
    class Meta:
        model = BiodiversityRecord
        fields = [
            'species_name', 'common_name', 'location_name',
            'observation_date_min', 'observation_date_max',
            'is_verified', 'contributor_id'
        ]