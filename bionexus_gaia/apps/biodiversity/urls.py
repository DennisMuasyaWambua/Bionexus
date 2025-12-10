from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BiodiversityRecordViewSet, species_list

router = DefaultRouter()
router.register(r'records', BiodiversityRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('species/', species_list, name='species-list'),
]