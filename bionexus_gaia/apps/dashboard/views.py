from django.db.models import Count, Sum
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from django.contrib.auth import get_user_model

from ..users.models import UserActivity, Project, Notification, Reward
# Temporarily disabled due to GDAL/GEOS dependency
# from ..biodiversity.models import BiodiversityRecord
# from ..citizen.models import Mission, CitizenObservation

User = get_user_model()


@extend_schema(
    tags=['Dashboard'],
    summary='Get dashboard overview',
    description='Get dashboard overview data including user stats, activities, and global statistics.',
    responses={
        200: OpenApiResponse(
            description='Dashboard overview data',
            examples=[
                OpenApiExample(
                    name='Dashboard Response',
                    value={
                        "user_stats": {
                            "total_points": 150,
                            "observations_count": 5,
                            "level": 2,
                            "badges_count": 3
                        },
                        "recent_activities": [],
                        "user_projects": [],
                        "unread_notifications": 2,
                        "global_stats": {
                            "total_users": 100,
                            "active_projects": 5,
                            "total_observations": 500,
                            "total_species_identified": 250
                        }
                    }
                )
            ]
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_overview(request):
    """
    Get dashboard overview data for the authenticated user.
    """
    user = request.user
    
    # User stats
    user_stats = {
        'total_points': user.total_points,
        'observations_count': user.observations_count,
        'level': _calculate_user_level(user.total_points),
        'badges_count': len(user.badges) if user.badges else 0
    }
    
    # Recent activities
    recent_activities = UserActivity.objects.filter(
        user=user
    ).order_by('-created_at')[:5]
    
    # Active projects
    user_projects = Project.objects.filter(
        participants=user,
        projectparticipation__is_active=True,
        status='active'
    )[:3]
    
    # Recent notifications
    unread_notifications = Notification.objects.filter(
        user=user,
        read=False
    ).count()
    
    # Global stats (for community engagement)
    global_stats = {
        'total_users': User.objects.count(),
        'active_projects': Project.objects.filter(status='active').count(),
        'total_observations': 0,  # Would be BiodiversityRecord.objects.count() when GDAL is available
        'total_species_identified': 0  # Would be calculated from biodiversity records
    }
    
    # Recent achievements
    recent_rewards = Reward.objects.filter(
        user=user,
        is_active=True
    ).order_by('-earned_at')[:3]
    
    # Suggested actions (based on user role and activity)
    suggested_actions = _get_suggested_actions(user)
    
    return Response({
        'user_stats': user_stats,
        'recent_activities': [
            {
                'id': str(activity.id),
                'type': activity.activity_type,
                'description': activity.description,
                'points': activity.points_earned,
                'date': activity.created_at
            }
            for activity in recent_activities
        ],
        'user_projects': [
            {
                'id': str(project.id),
                'title': project.title,
                'short_description': project.short_description,
                'status': project.status
            }
            for project in user_projects
        ],
        'unread_notifications': unread_notifications,
        'global_stats': global_stats,
        'recent_rewards': [
            {
                'id': str(reward.id),
                'title': reward.title,
                'type': reward.reward_type,
                'points': reward.points_value,
                'date': reward.earned_at
            }
            for reward in recent_rewards
        ],
        'suggested_actions': suggested_actions
    })


def _calculate_user_level(total_points):
    """
    Calculate user level based on total points.
    """
    if total_points < 100:
        return 1
    elif total_points < 500:
        return 2
    elif total_points < 1000:
        return 3
    elif total_points < 2500:
        return 4
    elif total_points < 5000:
        return 5
    else:
        return 6


def _get_suggested_actions(user):
    """
    Get personalized suggested actions based on user role and activity.
    """
    actions = []
    
    # Common actions for all users
    if user.observations_count == 0:
        actions.append({
            'type': 'first_observation',
            'title': 'Log Your First Sighting',
            'description': 'Record your first species observation to get started',
            'points': 25,
            'action_url': '/submissions/new'
        })
    
    if not user.onboarding_completed:
        actions.append({
            'type': 'complete_onboarding',
            'title': 'Complete Your Profile',
            'description': 'Finish setting up your profile to unlock all features',
            'points': 50,
            'action_url': '/onboarding'
        })
    
    # Role-specific actions
    if user.role == 'contributor':
        actions.append({
            'type': 'join_project',
            'title': 'Join a Conservation Project',
            'description': 'Contribute to ongoing research projects',
            'points': 100,
            'action_url': '/projects'
        })
    elif user.role == 'researcher':
        actions.append({
            'type': 'create_project',
            'title': 'Create a Research Project',
            'description': 'Start your own research initiative',
            'points': 200,
            'action_url': '/projects/new'
        })
    elif user.role == 'expert':
        actions.append({
            'type': 'validate_observations',
            'title': 'Validate Community Observations',
            'description': 'Help verify species identifications',
            'points': 50,
            'action_url': '/validation'
        })
    
    return actions[:3]  # Return up to 3 suggestions
