from django.utils import timezone
from django.db.models import Sum, Count, F, Q
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, generics, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema

from .models import Mission, MissionParticipation, CitizenObservation
from .serializers import (
    MissionSerializer,
    MissionParticipationSerializer,
    CitizenObservationSerializer,
    LeaderboardEntrySerializer,
    MapDataSerializer
)
from bionexus_gaia.apps.biodiversity.models import BiodiversityRecord
from bionexus_gaia.apps.biodiversity.serializers import BiodiversityRecordSerializer

User = get_user_model()

class MissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for citizen science missions.
    """
    queryset = Mission.objects.all()
    serializer_class = MissionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active']
    search_fields = ['title', 'description', 'location_name']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'participants_count', 'observations_count']
    ordering = ['-start_date']
    
    def get_permissions(self):
        """
        Override permissions - allow authenticated users to create missions.
        """
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
    
    def get_queryset(self):
        """
        Filter missions based on active status.
        """
        queryset = Mission.objects.all()
        
        # Filter active missions only for non-staff users
        if not self.request.user.is_staff and self.request.method != 'POST':
            queryset = queryset.filter(is_active=True)
            
            # Filter by current date for non-staff
            now = timezone.now()
            queryset = queryset.filter(
                Q(start_date__lte=now) & 
                (Q(end_date__isnull=True) | Q(end_date__gte=now))
            )
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Join a mission.
        """
        mission = self.get_object()
        user = request.user
        
        # Check if already participating
        if MissionParticipation.objects.filter(user=user, mission=mission).exists():
            return Response(
                {"detail": "You are already participating in this mission."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if mission is active
        if not mission.is_active:
            return Response(
                {"detail": "This mission is not active."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if mission has ended
        if mission.end_date and mission.end_date < timezone.now():
            return Response(
                {"detail": "This mission has ended."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create participation
        participation = MissionParticipation.objects.create(
            user=user,
            mission=mission
        )
        
        # Update mission stats
        mission.participants_count += 1
        mission.save()
        
        serializer = MissionParticipationSerializer(participation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LeaderboardView(generics.ListAPIView):
    """
    API endpoint for the community leaderboard.
    """
    serializer_class = LeaderboardEntrySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = CitizenObservation.objects.none()  # Fix for schema generation
    
    def get_queryset(self):
        """
        Calculate leaderboard data.
        """
        # Check for swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return []
        # Calculate total points per user
        users_data = CitizenObservation.objects.values('user').annotate(
            total_points=Sum('points_awarded'),
            observations_count=Count('id')
        ).order_by('-total_points')
        
        # Get missions completed count
        for user_data in users_data:
            user_data['missions_completed'] = MissionParticipation.objects.filter(
                user_id=user_data['user'],
                is_completed=True
            ).count()
        
        # Add rank and username
        leaderboard = []
        for rank, user_data in enumerate(users_data, 1):
            user = User.objects.get(id=user_data['user'])
            leaderboard.append({
                'user_id': user.id,
                'username': user.username,
                'total_points': user_data['total_points'],
                'observations_count': user_data['observations_count'],
                'missions_completed': user_data['missions_completed'],
                'rank': rank
            })
        
        return leaderboard
    
    def list(self, request, *args, **kwargs):
        """
        Get leaderboard data with optional filtering.
        """
        # Get time period filter if provided
        period = request.query_params.get('period', 'all')
        
        # Apply pagination
        page = self.paginate_queryset(self.get_queryset())
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response(serializer.data)


class BiodiversityMapView(generics.ListAPIView):
    """
    API endpoint for the interactive biodiversity map.
    """
    serializer_class = MapDataSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = BiodiversityRecord.objects.none()  # Fix for schema generation
    
    def get_queryset(self):
        """
        Get biodiversity records for map display.
        """
        # Check for swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return []
            
        # Query public biodiversity records with location data
        records = BiodiversityRecord.objects.filter(
            is_public=True,
            location__isnull=False
        ).select_related('contributor')
        
        # Limit to 1000 records for performance
        records = records[:1000]
        
        # Format for map display
        map_data = []
        for record in records:
            if record.location:
                map_data.append({
                    'id': record.id,
                    'species_name': record.species_name,
                    'common_name': record.common_name,
                    'latitude': record.location.y,
                    'longitude': record.location.x,
                    'observation_date': record.observation_date,
                    'image_url': record.image.url if record.image else None,
                    'contributor_username': record.contributor.username,
                    'is_verified': record.is_verified
                })
        
        return map_data


class CitizenObservationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for citizen science observations.
    """
    queryset = CitizenObservation.objects.all()
    serializer_class = CitizenObservationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter observations by user unless staff.
        """
        if self.request.user.is_staff:
            return CitizenObservation.objects.all()
        return CitizenObservation.objects.filter(user=self.request.user)
