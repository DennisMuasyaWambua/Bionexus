from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AIModelViewSet,
    IdentificationFeedbackViewSet,
    IdentificationAPIView,
    BatchIdentificationAPIView,
    TaxonomyAPIView
)

router = DefaultRouter()
router.register(r'models', AIModelViewSet)
router.register(r'feedback', IdentificationFeedbackViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('identify/', IdentificationAPIView.as_view(), name='identify'),
    path('identify/batch/', BatchIdentificationAPIView.as_view(), name='batch-identify'),
    path('taxonomy/<str:species>/', TaxonomyAPIView.as_view(), name='taxonomy'),
]