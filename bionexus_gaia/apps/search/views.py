from django.db.models import Q
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from django.contrib.auth import get_user_model

from ..users.models import Project, Notification
from ..users.serializers import UserSerializer, ProjectSerializer, NotificationSerializer
# Temporarily disabled due to GDAL/GEOS dependency
# from ..biodiversity.models import BiodiversityRecord
# from ..citizen.models import Mission, CitizenObservation

User = get_user_model()


@extend_schema(
    tags=['Search'],
    summary='Global search',
    description='Search across users, projects, notifications, observations, and missions.',
    parameters=[
        OpenApiParameter(
            name='q',
            type=OpenApiTypes.STR,
            description='Search query string',
            required=True
        )
    ],
    responses={
        200: OpenApiResponse(
            description='Search results across all models',
            examples=[
                OpenApiExample(
                    name='Search Results',
                    value={
                        "users": [],
                        "projects": [],
                        "notifications": [],
                        "observations": [],
                        "missions": [],
                        "total_count": 0
                    }
                )
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def global_search(request):
    """
    Global search endpoint that searches across multiple models.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({
            'error': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    results = {
        'users': [],
        'projects': [],
        'notifications': [],
        'observations': [],
        'missions': [],
        'total_count': 0
    }
    
    # Search users
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    
    results['users'] = UserSerializer(users, many=True).data
    
    # Search projects
    projects = Project.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(short_description__icontains=query)
    ).filter(status='active')[:10]
    
    results['projects'] = ProjectSerializer(projects, many=True).data
    
    # Search user's notifications
    notifications = Notification.objects.filter(
        user=request.user
    ).filter(
        Q(title__icontains=query) |
        Q(message__icontains=query)
    )[:5]
    
    results['notifications'] = NotificationSerializer(notifications, many=True).data
    
    # TODO: Add biodiversity records and citizen observations when GDAL is available
    # observations = BiodiversityRecord.objects.filter(
    #     Q(species_name__icontains=query) |
    #     Q(description__icontains=query)
    # ).filter(user=request.user)[:10]
    # results['observations'] = BiodiversityRecordSerializer(observations, many=True).data
    
    # missions = Mission.objects.filter(
    #     Q(title__icontains=query) |
    #     Q(description__icontains=query)
    # ).filter(is_active=True)[:10]
    # results['missions'] = MissionSerializer(missions, many=True).data
    
    # Calculate total count
    results['total_count'] = (
        len(results['users']) +
        len(results['projects']) +
        len(results['notifications']) +
        len(results['observations']) +
        len(results['missions'])
    )
    
    return Response(results)


@extend_schema(
    tags=['Search'],
    summary='Get search suggestions',
    description='Get search suggestions based on user activity and popular content.',
    responses={
        200: OpenApiResponse(
            description='Search suggestions',
            examples=[
                OpenApiExample(
                    name='Suggestions Response',
                    value={
                        "popular_searches": [
                            "endangered species",
                            "local wildlife",
                            "bird observations"
                        ],
                        "recent_searches": [],
                        "trending_species": []
                    }
                )
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_suggestions(request):
    """
    Get search suggestions based on user activity and popular content.
    """
    suggestions = {
        'popular_searches': [
            'endangered species',
            'local wildlife',
            'bird observations',
            'marine life',
            'forest conservation'
        ],
        'recent_projects': [],
        'trending_topics': [
            'climate change',
            'biodiversity loss',
            'conservation efforts',
            'citizen science',
            'species identification'
        ]
    }
    
    # Get recent active projects
    recent_projects = Project.objects.filter(
        status='active'
    ).order_by('-created_at')[:5]
    
    suggestions['recent_projects'] = [
        {'id': str(p.id), 'title': p.title} 
        for p in recent_projects
    ]
    
    return Response(suggestions)
