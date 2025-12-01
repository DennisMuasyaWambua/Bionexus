from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserProfileView,
    UserStatsView,
    UserActivityViewSet,
    OnboardingView,
    OnboardView,
    NotificationViewSet,
    ProjectViewSet,
    RewardViewSet
)

router = DefaultRouter()
router.register(r'activities', UserActivityViewSet, basename='user-activity')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'rewards', RewardViewSet, basename='reward')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('stats/', UserStatsView.as_view(), name='user-stats'),
    path('onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('onboard/', OnboardView.as_view(), name='onboard'),
]