import secrets
import uuid
from django.db.models import Count, Sum, Q
from django.contrib.auth import get_user_model
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
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
    UserStatsSerializer,
    NotificationSerializer,
    ProjectSerializer,
    ProjectParticipationSerializer,
    RewardSerializer,
    GoogleOAuthSerializer,
    OnboardingSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    AcceptTermsSerializer
)
from .models import UserActivity, Notification, Project, ProjectParticipation, Reward, EmailVerification, PasswordResetToken
from django.utils import timezone
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


class GoogleOAuthView(generics.GenericAPIView):
    """
    API endpoint for Google OAuth authentication.
    """
    permission_classes = [AllowAny]
    serializer_class = GoogleOAuthSerializer
    
    def post(self, request, *args, **kwargs):
        """
        Authenticate or register user with Google OAuth.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        access_token = serializer.validated_data['access_token']
        role = serializer.validated_data.get('role')
        
        # In a real implementation, verify the Google access token and get user info
        # For now, we'll use mock data
        google_user_info = {
            'email': 'user@example.com',  # This would come from Google API
            'name': 'John Doe',
            'picture': 'https://example.com/avatar.jpg',
            'google_id': '1234567890'
        }
        
        # Check if user already exists
        user = User.objects.filter(
            Q(email=google_user_info['email']) |
            Q(oauth_id=google_user_info['google_id'], oauth_provider='google')
        ).first()
        
        if user:
            # Existing user, log them in
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'is_new_user': False
            })
        else:
            # New user, create account
            username = google_user_info['email'].split('@')[0]
            
            # Ensure username uniqueness
            if User.objects.filter(username=username).exists():
                username = f"{username}_{uuid.uuid4().hex[:6]}"
            
            user = User.objects.create(
                username=username,
                email=google_user_info['email'],
                first_name=google_user_info['name'].split(' ')[0],
                last_name=' '.join(google_user_info['name'].split(' ')[1:]),
                oauth_provider='google',
                oauth_id=google_user_info['google_id'],
                role=role
            )
            
            # Create welcome activity
            UserActivity.objects.create(
                user=user,
                activity_type='google_oauth_registration',
                description='Welcome to BioNexus Gaia!',
                points_earned=10
            )
            
            # Create welcome notification
            Notification.objects.create(
                user=user,
                title='Welcome to BioNexus Gaia!',
                message='Thank you for joining our community. Complete your onboarding to get started.',
                notification_type='general'
            )
            
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data,
                'is_new_user': True
            }, status=status.HTTP_201_CREATED)


class OnboardingView(generics.GenericAPIView):
    """
    API endpoint for user onboarding process.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = OnboardingSerializer
    
    def get(self, request, *args, **kwargs):
        """
        Get current onboarding status and available steps.
        """
        user = request.user
        
        onboarding_steps = [
            {
                'step': 1,
                'title': 'Choose Your Role',
                'description': 'Select how you\'ll engage with GAIA',
                'completed': bool(user.role),
                'required': True
            },
            {
                'step': 2,
                'title': 'Set Location',
                'description': 'Tell us where you\'re based for local content',
                'completed': False,  # This would be based on location data
                'required': False
            },
            {
                'step': 3,
                'title': 'Your Affiliations',
                'description': 'Share your organization or research interests',
                'completed': False,  # This would be based on profile completion
                'required': False
            },
            {
                'step': 4,
                'title': 'How Do You Want to Contribute?',
                'description': 'Select your areas of interest',
                'completed': False,  # This would be based on preferences
                'required': False
            },
            {
                'step': 5,
                'title': 'Your SKS Level',
                'description': 'Tell us about your experience level',
                'completed': False,  # This would be based on skill assessment
                'required': False
            }
        ]
        
        return Response({
            'current_step': user.onboarding_step,
            'completed': user.onboarding_completed,
            'steps': onboarding_steps,
            'user': UserSerializer(user).data
        })
    
    def post(self, request, *args, **kwargs):
        """
        Update onboarding progress.
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update user onboarding data
        user = serializer.save()
        
        # If role is set, move to next step
        if user.role and user.onboarding_step == 0:
            user.onboarding_step = 1
            user.save()
            
            # Create role-specific welcome activity
            UserActivity.objects.create(
                user=user,
                activity_type='role_selection',
                description=f'Selected role: {user.get_role_display()}',
                points_earned=5
            )
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Onboarding updated successfully'
        })


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter notifications to only show the current user's notifications.
        """
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """
        Mark a notification as read.
        """
        notification = self.get_object()
        notification.read = True
        notification.save()
        
        return Response({'status': 'notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read.
        """
        self.get_queryset().update(read=True)
        return Response({'status': 'all notifications marked as read'})


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for projects.
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return active projects, with user's projects first.
        """
        return Project.objects.filter(status='active').order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Set the creator to the current user.
        """
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """
        Join a project.
        """
        project = self.get_object()
        
        # Check if already joined
        participation, created = ProjectParticipation.objects.get_or_create(
            user=request.user,
            project=project,
            defaults={'is_active': True}
        )
        
        if not created and participation.is_active:
            return Response({
                'error': 'You are already part of this project'
            }, status=status.HTTP_400_BAD_REQUEST)
        elif not created:
            # Rejoin the project
            participation.is_active = True
            participation.save()
        
        # Create activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='project_join',
            description=f'Joined project: {project.title}',
            points_earned=15
        )
        
        # Create notification for project creator
        Notification.objects.create(
            user=project.creator,
            title='New Project Member',
            message=f'{request.user.username} joined your project "{project.title}"',
            notification_type='project'
        )
        
        return Response({
            'status': 'joined project successfully',
            'participation': ProjectParticipationSerializer(participation).data
        })
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """
        Leave a project.
        """
        project = self.get_object()
        
        try:
            participation = ProjectParticipation.objects.get(
                user=request.user,
                project=project,
                is_active=True
            )
            participation.is_active = False
            participation.save()
            
            return Response({'status': 'left project successfully'})
        except ProjectParticipation.DoesNotExist:
            return Response({
                'error': 'You are not part of this project'
            }, status=status.HTTP_400_BAD_REQUEST)


class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for user rewards.
    """
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter rewards to only show the current user's rewards.
        """
        return Reward.objects.filter(user=self.request.user, is_active=True)


class EmailVerificationView(generics.GenericAPIView):
    """
    API endpoint for email verification.
    """
    permission_classes = [AllowAny]
    serializer_class = EmailVerificationSerializer
    
    @extend_schema(
        operation_id="verify_email",
        tags=["Authentication"],
        summary="Verify email address",
        description="Verify user's email address using a 6-digit verification code sent via email after registration.",
        request=EmailVerificationSerializer,
        responses={
            200: OpenApiResponse(
                description="Email verified successfully",
                examples=[
                    OpenApiExample(
                        name="Success Response",
                        value={
                            "message": "Email verified successfully",
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "username": "testuser",
                                "email": "test@example.com",
                                "email_verified": True
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Invalid verification code or expired code")
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Verify user's email with 6-digit code.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        verification = serializer.validated_data['verification']
        
        # Mark verification as used
        verification.is_used = True
        verification.save()
        
        # Mark user's email as verified
        user.email_verified = True
        user.save()
        
        # Create activity
        UserActivity.objects.create(
            user=user,
            activity_type='email_verification',
            description='Email address verified successfully',
            points_earned=5
        )
        
        return Response({
            'message': 'Email verified successfully',
            'user': UserSerializer(user).data
        })


class ResendVerificationView(generics.GenericAPIView):
    """
    API endpoint for resending email verification.
    """
    permission_classes = [AllowAny]
    serializer_class = ResendVerificationSerializer
    
    @extend_schema(
        operation_id="resend_verification_email",
        tags=["Authentication"],
        summary="Resend verification email",
        description="Resend a new 6-digit verification code to the user's email address.",
        request=ResendVerificationSerializer,
        responses={
            200: OpenApiResponse(
                description="Verification email sent successfully",
                examples=[
                    OpenApiExample(
                        name="Success Response",
                        value={"message": "Verification email sent successfully"}
                    )
                ]
            ),
            400: OpenApiResponse(description="Email already verified or user not found")
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Resend verification email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        serializer.send_verification_email(email)
        
        return Response({
            'message': 'Verification email sent successfully'
        })


class ForgotPasswordView(generics.GenericAPIView):
    """
    API endpoint for forgot password functionality.
    """
    permission_classes = [AllowAny]
    serializer_class = ForgotPasswordSerializer
    
    @extend_schema(
        operation_id="forgot_password",
        tags=["Authentication"],
        summary="Request password reset",
        description="Send a password reset email with a secure reset link. The reset token expires after 1 hour.",
        request=ForgotPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset email sent successfully",
                examples=[
                    OpenApiExample(
                        name="Success Response",
                        value={"message": "Password reset email sent successfully"}
                    )
                ]
            ),
            400: OpenApiResponse(description="User with email not found")
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Send password reset email.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        serializer.send_reset_email(email)
        
        return Response({
            'message': 'Password reset email sent successfully'
        })


class ResetPasswordView(generics.GenericAPIView):
    """
    API endpoint for resetting password with token.
    """
    permission_classes = [AllowAny]
    serializer_class = ResetPasswordSerializer
    
    @extend_schema(
        operation_id="reset_password",
        tags=["Authentication"],
        summary="Reset password with token",
        description="Reset user's password using a secure token received via email.",
        request=ResetPasswordSerializer,
        responses={
            200: OpenApiResponse(
                description="Password reset successfully",
                examples=[
                    OpenApiExample(
                        name="Success Response",
                        value={"message": "Password reset successfully"}
                    )
                ]
            ),
            400: OpenApiResponse(description="Invalid or expired reset token")
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Reset password using token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reset_token = serializer.validated_data['reset_token']
        new_password = serializer.validated_data['new_password']
        
        # Update user password
        user = reset_token.user
        user.set_password(new_password)
        user.save()
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.save()
        
        # Create activity
        UserActivity.objects.create(
            user=user,
            activity_type='password_reset',
            description='Password reset successfully',
            points_earned=0
        )
        
        return Response({
            'message': 'Password reset successfully'
        })


class AcceptTermsView(generics.GenericAPIView):
    """
    API endpoint for accepting terms and conditions.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AcceptTermsSerializer
    
    @extend_schema(
        operation_id="accept_terms",
        tags=["Authentication"],
        summary="Accept terms and conditions",
        description="Record user's acceptance of the platform's terms and conditions.",
        request=AcceptTermsSerializer,
        responses={
            200: OpenApiResponse(
                description="Terms accepted successfully",
                examples=[
                    OpenApiExample(
                        name="Success Response",
                        value={
                            "message": "Terms and conditions accepted successfully",
                            "user": {
                                "id": "123e4567-e89b-12d3-a456-426614174000",
                                "terms_accepted": True,
                                "terms_accepted_at": "2024-11-21T10:00:00Z"
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description="Terms acceptance required")
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Accept terms and conditions.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.terms_accepted = True
        user.terms_accepted_at = timezone.now()
        user.save()
        
        # Create activity
        UserActivity.objects.create(
            user=user,
            activity_type='terms_acceptance',
            description='Accepted terms and conditions',
            points_earned=0
        )
        
        return Response({
            'message': 'Terms and conditions accepted successfully',
            'user': UserSerializer(user).data
        })


class CheckTermsStatusView(generics.GenericAPIView):
    """
    API endpoint to check if user has accepted terms.
    """
    permission_classes = [AllowAny]
    
    @extend_schema(
        operation_id="check_terms_status",
        tags=["Authentication"],
        summary="Check terms and conditions status",
        description="Check if terms and conditions acceptance is required for registration.",
        responses={
            200: OpenApiResponse(
                description="Terms status information",
                examples=[
                    OpenApiExample(
                        name="Terms Status Response",
                        value={
                            "terms_required": True,
                            "terms_url": "/terms-and-conditions",
                            "privacy_url": "/privacy-policy"
                        }
                    )
                ]
            )
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Check if terms need to be accepted before registration.
        """
        return Response({
            'terms_required': True,
            'terms_url': '/terms-and-conditions',
            'privacy_url': '/privacy-policy'
        })
