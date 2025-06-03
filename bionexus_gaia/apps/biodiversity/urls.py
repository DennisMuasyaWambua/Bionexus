from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BiodiversityRecordViewSet

router = DefaultRouter()
router.register(r'records', BiodiversityRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]