import csv
import json
from datetime import datetime
from django.http import HttpResponse
from django.db.models import Q
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import BiodiversityRecord
from .serializers import BiodiversityRecordSerializer, BiodiversityRecordExportSerializer
from .filters import BiodiversityRecordFilter
from .permissions import IsContributorOrReadOnly

class BiodiversityRecordViewSet(viewsets.ModelViewSet):
    """
    API endpoint for biodiversity records.
    
    list:
        Return a list of all biodiversity records.
        
    create:
        Create a new biodiversity record.
        
    retrieve:
        Return the given biodiversity record.
        
    update:
        Update the given biodiversity record.
        
    partial_update:
        Update part of the given biodiversity record.
        
    destroy:
        Delete the given biodiversity record.
    """
    queryset = BiodiversityRecord.objects.all()
    serializer_class = BiodiversityRecordSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsContributorOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BiodiversityRecordFilter
    search_fields = ['species_name', 'common_name', 'notes', 'location_name']
    ordering_fields = ['species_name', 'observation_date', 'created_at', 'ai_confidence']
    ordering = ['-observation_date']
    
    def get_queryset(self):
        """
        Filter records based on public status and user permissions.
        """
        queryset = BiodiversityRecord.objects.all()
        
        # If not authenticated, only show public records
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(is_public=True)
        # If authenticated but not staff, show public records and user's own records
        elif not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(is_public=True) | Q(contributor=self.request.user)
            )
        
        # Filter by geographic radius if provided
        lat = self.request.query_params.get('lat')
        lng = self.request.query_params.get('lng')
        radius = self.request.query_params.get('radius')
        
        if lat and lng and radius:
            try:
                point = Point(float(lng), float(lat), srid=4326)
                queryset = queryset.filter(
                    location__distance_lte=(point, Distance(km=float(radius)))
                )
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export biodiversity records as CSV or JSON.
        """
        format_type = request.query_params.get('format', 'csv')
        queryset = self.get_queryset()
        
        # Limit export to 10000 records for performance
        queryset = queryset[:10000]
        
        if format_type.lower() == 'json':
            # Export as JSON
            serializer = BiodiversityRecordExportSerializer(queryset, many=True)
            response = HttpResponse(
                json.dumps(serializer.data, indent=2, default=str),
                content_type='application/json'
            )
            response['Content-Disposition'] = 'attachment; filename="biodiversity_export.json"'
            
        else:
            # Default: Export as CSV
            serializer = BiodiversityRecordExportSerializer(queryset, many=True)
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="biodiversity_export.csv"'
            
            # Create CSV writer and write header
            writer = csv.DictWriter(response, fieldnames=serializer.child.fields.keys())
            writer.writeheader()
            
            # Write data rows, handling datetime serialization
            for item in serializer.data:
                # Convert datetime fields to strings
                for key, value in item.items():
                    if isinstance(value, datetime):
                        item[key] = value.isoformat()
                writer.writerow(item)
        
        return response
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Validate a biodiversity record on the blockchain.
        This is a placeholder for the actual blockchain integration.
        """
        record = self.get_object()
        
        # In a real implementation, this would interact with a blockchain smart contract
        if not record.is_verified:
            # Mock blockchain hash (in production this would be the actual transaction hash)
            mock_hash = "0x" + "".join([f"{i}" for i in range(64)])
            record.blockchain_hash = mock_hash
            record.is_verified = True
            record.save()
            return Response({
                "success": True,
                "message": "Record verified on blockchain",
                "blockchain_hash": record.blockchain_hash
            })
        
        return Response({
            "success": False,
            "message": "Record already verified",
            "blockchain_hash": record.blockchain_hash
        })
