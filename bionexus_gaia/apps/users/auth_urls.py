from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    CustomTokenObtainPairView,
    Web3RegisterView,
    Web3AuthView,
    GoogleOAuthView,
    EmailVerificationView,
    ResendVerificationView,
    ForgotPasswordView,
    ResetPasswordView,
    AcceptTermsView,
    CheckTermsStatusView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('wallet-register/', Web3RegisterView.as_view(), name='wallet-register'),
    path('wallet-connect/', Web3AuthView.as_view(), name='wallet-connect'),
    path('google/', GoogleOAuthView.as_view(), name='google-oauth'),
    
    # Email verification endpoints
    path('verify-email/', EmailVerificationView.as_view(), name='verify-email'),
    path('resend-verification/', ResendVerificationView.as_view(), name='resend-verification'),
    
    # Password reset endpoints  
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    
    # Terms and conditions endpoints
    path('accept-terms/', AcceptTermsView.as_view(), name='accept-terms'),
    path('terms-status/', CheckTermsStatusView.as_view(), name='terms-status'),
]