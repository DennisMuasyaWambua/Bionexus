from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    Web3RegisterView,
    Web3AuthView,
    GoogleOAuthView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('wallet-register/', Web3RegisterView.as_view(), name='wallet-register'),
    path('wallet-connect/', Web3AuthView.as_view(), name='wallet-connect'),
    path('google/', GoogleOAuthView.as_view(), name='google-oauth'),
]