import random
import uuid
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.gis.geos import Point

from .models import AIModel, IdentificationFeedback
from .serializers import (
    AIModelSerializer,
    IdentificationFeedbackSerializer,
    IdentificationSerializer,
    TaxonomySerializer
)
from bionexus_gaia.apps.biodiversity.models import BiodiversityRecord

class AIModelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for AI model information.
    """
    queryset = AIModel.objects.filter(is_active=True)
    serializer_class = AIModelSerializer
    
    @action(detail=False, methods=['get'])
    def info(self, request):
        """
        Get information about available AI models.
        """
        models = self.get_queryset()
        serializer = self.get_serializer(models, many=True)
        
        # Add overall platform stats
        stats = {
            'total_models': models.count(),
            'average_accuracy': sum(model.accuracy for model in models) / models.count() if models else 0,
            'supported_media_types': ['image', 'audio', 'video'],
            'identification_count': BiodiversityRecord.objects.filter(ai_prediction__isnull=False).count(),
        }
        
        return Response({
            'models': serializer.data,
            'stats': stats
        })


class IdentificationFeedbackViewSet(viewsets.ModelViewSet):
    """
    API endpoint for identification feedback.
    """
    queryset = IdentificationFeedback.objects.all()
    serializer_class = IdentificationFeedbackSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter feedback by user unless staff.
        """
        if self.request.user.is_staff:
            return IdentificationFeedback.objects.all()
        return IdentificationFeedback.objects.filter(user=self.request.user)


class IdentificationAPIView(generics.GenericAPIView):
    """
    API endpoint for species identification from media.
    """
    serializer_class = IdentificationSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Process an identification request.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Mock identification logic (in production, this would call ML model API)
        species_data = self._mock_species_identification(serializer.validated_data)
        
        # Create a biodiversity record if requested
        save_record = request.data.get('save_record', False)
        if save_record:
            record = self._create_biodiversity_record(serializer.validated_data, species_data)
            return Response({
                'identification': species_data,
                'record_id': record.id,
                'record_created': True
            }, status=status.HTTP_201_CREATED)
        
        return Response({'identification': species_data}, status=status.HTTP_200_OK)
    
    def _mock_species_identification(self, data):
        """
        Mock species identification (for MVP).
        In production, this would integrate with ML models.
        """
        # Mock species data
        mock_species = [
            {"name": "Panthera leo", "common_name": "Lion", "confidence": 0.92},
            {"name": "Buteo jamaicensis", "common_name": "Red-tailed Hawk", "confidence": 0.88},
            {"name": "Quercus rubra", "common_name": "Northern Red Oak", "confidence": 0.95},
            {"name": "Papilio machaon", "common_name": "Swallowtail Butterfly", "confidence": 0.89},
            {"name": "Bufo bufo", "common_name": "Common Toad", "confidence": 0.82},
        ]
        
        # Randomly select a species from the mock data
        species = random.choice(mock_species)
        
        # Add additional details
        result = {
            "species": species["name"],
            "common_name": species["common_name"],
            "confidence": species["confidence"],
            "alternatives": [s for s in mock_species if s != species][:3],
            "model_used": "BioDiversityNet v1.0",
            "identification_time": timezone.now().isoformat(),
        }
        
        return result
    
    def _create_biodiversity_record(self, input_data, species_data):
        """
        Create a biodiversity record from identification data.
        """
        # Extract coordinates if provided
        location = None
        if 'latitude' in input_data and 'longitude' in input_data:
            location = Point(
                input_data['longitude'],
                input_data['latitude'],
                srid=4326
            )
        
        # Create record
        record = BiodiversityRecord.objects.create(
            id=uuid.uuid4(),
            contributor=self.request.user,
            species_name=species_data['species'],
            common_name=species_data['common_name'],
            image=input_data.get('image', None),
            audio=input_data.get('audio', None),
            video=input_data.get('video', None),
            location=location,
            observation_date=input_data.get('observation_date', timezone.now()),
            ai_prediction=species_data,
            ai_confidence=species_data['confidence'],
            is_public=True
        )
        
        return record


class BatchIdentificationAPIView(generics.GenericAPIView):
    """
    API endpoint for batch species identification.
    """
    serializer_class = IdentificationSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Process multiple identification requests at once.
        """
        if not isinstance(request.data, list):
            return Response(
                {"error": "Request body must be a JSON array of identification requests"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        results = []
        for item in request.data:
            serializer = self.get_serializer(data=item)
            if serializer.is_valid():
                # Mock identification logic
                identification_view = IdentificationAPIView()
                identification_view.request = request
                species_data = identification_view._mock_species_identification(serializer.validated_data)
                
                # Add to results
                results.append({
                    'identification': species_data,
                    'input': item,
                    'success': True
                })
            else:
                # Add error to results
                results.append({
                    'input': item,
                    'success': False,
                    'errors': serializer.errors
                })
        
        return Response(results, status=status.HTTP_200_OK)


@api_view(['GET'])
def taxonomy_view(request, species):
    """
    Get taxonomic information for a species.
    """
    # Mock taxonomy data (in production, this would call a taxonomy database or API)
    mock_taxonomy = {
        "kingdom": "Animalia",
        "phylum": "Chordata",
        "class_name": "Mammalia",
        "order": "Carnivora",
        "family": "Felidae",
        "genus": "Panthera",
        "species": species,
        "common_names": ["Lion", "African Lion"]
    }
    
    serializer = TaxonomySerializer(data=mock_taxonomy)
    serializer.is_valid()
    
    return Response(serializer.data)
