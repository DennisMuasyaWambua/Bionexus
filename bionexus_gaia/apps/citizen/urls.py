from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MissionViewSet,
    CitizenObservationViewSet,
    LeaderboardView,
    BiodiversityMapView
)

router = DefaultRouter()
router.register(r'missions', MissionViewSet)
router.register(r'observations', CitizenObservationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('map/', BiodiversityMapView.as_view(), name='biodiversity-map'),
]