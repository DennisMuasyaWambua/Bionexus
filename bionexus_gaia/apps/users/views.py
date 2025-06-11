import secrets
import uuid
from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserSerializer,
    UserActivitySerializer,
    RegisterSerializer,
    Web3RegisterSerializer,
    CustomTokenObtainPairSerializer,
    Web3AuthSerializer,
    UserStatsSerializer
)
from .models import UserActivity
# Temporarily disabled due to GDAL/GEOS dependency
# from bionexus_gaia.apps.biodiversity.models import BiodiversityRecord
# from bionexus_gaia.apps.citizen.models import MissionParticipation, CitizenObservation

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration (Web2).
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token view with additional user info.
    """
    serializer_class = CustomTokenObtainPairSerializer


class Web3RegisterView(generics.GenericAPIView):
    """
    API endpoint for Web3 wallet-based registration.
    """
    permission_classes = [AllowAny]
    serializer_class = Web3RegisterSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Register a new user with Web3 wallet.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        wallet_address = serializer.validated_data['wallet_address']
        wallet_type = serializer.validated_data['wallet_type']
        
        # Generate username if not provided
        username = serializer.validated_data.get('username')
        if not username:
            # Generate username based on wallet address
            username = f"user_{wallet_address[:8]}"
            # Ensure uniqueness
            if User.objects.filter(username=username).exists():
                username = f"{username}_{uuid.uuid4().hex[:6]}"
        
        # Create user
        user = User.objects.create(
            username=username,
            email=serializer.validated_data.get('email', ''),
            wallet_address=wallet_address,
            wallet_type=wallet_type,
            web3_nonce=secrets.token_hex(16)  # Generate nonce for future auth
        )
        
        # Create welcome activity
        UserActivity.objects.create(
            user=user,
            activity_type='web3_registration',
            description='Welcome to BioNexus Gaia!',
            points_earned=10
        )
        
        # Generate token for the new user
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)


class Web3AuthView(generics.GenericAPIView):
    """
    API endpoint for Web3 wallet authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = Web3AuthSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Authenticate user with Web3 wallet.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate new nonce for future auth
        user.web3_nonce = secrets.token_hex(16)
        user.save()
        
        # Generate token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserStatsView(generics.GenericAPIView):
    """
    API endpoint for user contribution statistics.
    """
    serializer_class = UserStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """
        Get detailed statistics for the authenticated user.
        """
        user = request.user
        
        # Calculate stats (with biodiversity and citizen features disabled)
        stats = {
            'total_observations': 0,  # Temporarily set to 0 while BiodiversityRecord is disabled
            'verified_observations': 0,  # Temporarily set to 0 while BiodiversityRecord is disabled
            'total_missions': 0,  # Temporarily set to 0 while MissionParticipation is disabled
            'completed_missions': 0,  # Temporarily set to 0 while MissionParticipation is disabled
            'total_points': user.total_points,
            'badges': user.badges or [],
            'leaderboard_position': self._get_leaderboard_position(user)
        }
        
        serializer = self.get_serializer(stats)
        return Response(serializer.data)
    
    def _get_leaderboard_position(self, user):
        """
        Calculate user's position in the leaderboard.
        """
        # Get users ordered by total points
        users_by_points = User.objects.order_by('-total_points')
        
        # Find user's position (1-indexed)
        for position, u in enumerate(users_by_points, 1):
            if u.id == user.id:
                return position
        
        return 0  # Fallback if not found


class UserActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user activity history.
    """
    serializer_class = UserActivitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter activities to only show the current user's activities.
        """
        return UserActivity.objects.filter(user=self.request.user)
