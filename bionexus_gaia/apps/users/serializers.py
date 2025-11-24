from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserActivity, Notification, Project, ProjectParticipation, Reward, EmailVerification, PasswordResetToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'wallet_address', 'wallet_type', 'bio', 'profile_image',
            'role', 'onboarding_completed', 'onboarding_step',
            'oauth_provider', 'oauth_id',
            'total_points', 'observations_count', 'badges',
            'notification_preferences', 'date_joined'
        ]
        read_only_fields = ['id', 'total_points', 'observations_count', 'badges', 'date_joined', 'oauth_id']


class UserActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for user activity.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = UserActivity
        fields = [
            'id', 'user', 'username', 'activity_type', 'description',
            'points_earned', 'created_at', 'metadata'
        ]
        read_only_fields = ['id', 'user', 'username', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration (Web2).
    
    Handles user registration with email and password only.
    Automatically sends a 6-digit verification code via email after successful registration.
    """
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        
        # Generate username from email prefix
        email = validated_data['email']
        username_base = email.split('@')[0]
        username = username_base
        
        # Ensure username is unique
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{username_base}_{counter}"
            counter += 1
        
        user = User.objects.create(
            username=username,
            email=validated_data['email']
        )
        
        user.set_password(validated_data['password'])
        user.save()
        
        # Create welcome activity
        UserActivity.objects.create(
            user=user,
            activity_type='registration',
            description='Welcome to BioNexus Gaia!',
            points_earned=10
        )
        
        # Send email verification
        self.send_verification_email(user)
        
        return user
    
    def send_verification_email(self, user):
        """Send verification email with 6-digit code."""
        verification = EmailVerification.objects.create(user=user)
        
        subject = 'Verify your BioNexus Gaia account'
        message = f'''
Hello {user.username},

Thank you for registering with BioNexus Gaia!

Your verification code is: {verification.verification_code}

This code will expire in 15 minutes.

Please use this code to verify your email address.

Best regards,
BioNexus Gaia Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            pass


class Web3RegisterSerializer(serializers.Serializer):
    """
    Serializer for Web3 wallet-based registration.
    """
    wallet_address = serializers.CharField(max_length=42)
    wallet_type = serializers.CharField(max_length=20)
    signature = serializers.CharField()
    message = serializers.CharField()
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    
    def validate(self, attrs):
        wallet_address = attrs.get('wallet_address')
        
        # Check if wallet is already registered
        if User.objects.filter(wallet_address=wallet_address).exists():
            raise serializers.ValidationError({"wallet_address": "This wallet is already registered."})
        
        # In a real implementation, verify the signature here
        # This would involve cryptographic validation of the signature against the message
        
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user info.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['wallet_address'] = user.wallet_address
        
        return token


class Web3AuthSerializer(serializers.Serializer):
    """
    Serializer for Web3 wallet authentication.
    """
    wallet_address = serializers.CharField(max_length=42)
    signature = serializers.CharField()
    message = serializers.CharField()
    
    def validate(self, attrs):
        wallet_address = attrs.get('wallet_address')
        
        # Check if wallet exists
        try:
            user = User.objects.get(wallet_address=wallet_address)
        except User.DoesNotExist:
            raise serializers.ValidationError({"wallet_address": "No user found with this wallet."})
        
        # In a real implementation, verify the signature here
        # This would involve cryptographic validation of the signature against the message
        
        attrs['user'] = user
        return attrs


class UserStatsSerializer(serializers.Serializer):
    """
    Serializer for user contribution statistics.
    """
    total_observations = serializers.IntegerField()
    verified_observations = serializers.IntegerField()
    total_missions = serializers.IntegerField()
    completed_missions = serializers.IntegerField()
    total_points = serializers.IntegerField()
    badges = serializers.ListField()
    leaderboard_position = serializers.IntegerField()


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notifications.
    """
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'read', 
            'created_at', 'action_url', 'metadata'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for projects.
    """
    creator_username = serializers.CharField(source='creator.username', read_only=True)
    participant_count = serializers.SerializerMethodField()
    user_joined = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'short_description', 'image',
            'creator', 'creator_username', 'status', 'max_participants',
            'participant_count', 'user_joined', 'start_date', 'end_date',
            'created_at', 'updated_at', 'tags', 'requirements', 'rewards_description'
        ]
        read_only_fields = ['id', 'creator', 'creator_username', 'participant_count', 'user_joined', 'created_at', 'updated_at']
    
    def get_participant_count(self, obj):
        return obj.participants.filter(projectparticipation__is_active=True).count()
    
    def get_user_joined(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.participants.filter(
                id=request.user.id,
                projectparticipation__is_active=True
            ).exists()
        return False


class ProjectParticipationSerializer(serializers.ModelSerializer):
    """
    Serializer for project participation.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    project_title = serializers.CharField(source='project.title', read_only=True)
    
    class Meta:
        model = ProjectParticipation
        fields = [
            'id', 'user', 'username', 'project', 'project_title',
            'joined_at', 'role', 'contributions_count', 'is_active'
        ]
        read_only_fields = ['id', 'username', 'project_title', 'joined_at']


class RewardSerializer(serializers.ModelSerializer):
    """
    Serializer for rewards.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Reward
        fields = [
            'id', 'user', 'username', 'title', 'description', 'reward_type',
            'icon', 'points_value', 'earned_at', 'criteria', 'metadata', 'is_active'
        ]
        read_only_fields = ['id', 'username', 'earned_at']


class GoogleOAuthSerializer(serializers.Serializer):
    """
    Serializer for Google OAuth authentication.
    """
    access_token = serializers.CharField()
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    
    def validate(self, attrs):
        # In a real implementation, validate the Google access token here
        # This would involve calling Google's API to verify the token
        return attrs


class OnboardingSerializer(serializers.ModelSerializer):
    """
    Serializer for user onboarding.
    """
    class Meta:
        model = User
        fields = ['role', 'onboarding_step', 'onboarding_completed']


class EmailVerificationSerializer(serializers.Serializer):
    """
    Serializer for email verification.
    
    Used to verify user's email address using a 6-digit code sent via email.
    The verification code expires after 15 minutes.
    """
    email = serializers.EmailField(help_text="The email address to verify")
    verification_code = serializers.CharField(max_length=6, help_text="6-digit verification code sent via email")
    
    def validate(self, attrs):
        email = attrs.get('email')
        verification_code = attrs.get('verification_code')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User with this email does not exist."})
        
        verification = EmailVerification.objects.filter(
            user=user,
            verification_code=verification_code,
            is_used=False
        ).first()
        
        if not verification:
            raise serializers.ValidationError({"verification_code": "Invalid verification code."})
        
        if verification.is_expired():
            raise serializers.ValidationError({"verification_code": "Verification code has expired."})
        
        attrs['user'] = user
        attrs['verification'] = verification
        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    """
    Serializer for resending verification email.
    
    Used to request a new verification code when the previous one has expired
    or was not received.
    """
    email = serializers.EmailField(help_text="Email address to resend verification code to")
    
    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            if user.email_verified:
                raise serializers.ValidationError("Email is already verified.")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    
    def send_verification_email(self, email):
        """Send new verification email."""
        user = User.objects.get(email=email)
        
        # Deactivate previous verification codes
        EmailVerification.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new verification
        verification = EmailVerification.objects.create(user=user)
        
        subject = 'Verify your BioNexus Gaia account'
        message = f'''
Hello {user.username},

Your new verification code is: {verification.verification_code}

This code will expire in 15 minutes.

Please use this code to verify your email address.

Best regards,
BioNexus Gaia Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            pass


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Serializer for forgot password functionality.
    
    Used to request a password reset email containing a secure reset link.
    The reset token expires after 1 hour.
    """
    email = serializers.EmailField(help_text="Email address to send password reset link to")
    
    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value
    
    def send_reset_email(self, email):
        """Send password reset email."""
        user = User.objects.get(email=email)
        
        # Deactivate previous reset tokens
        PasswordResetToken.objects.filter(user=user, is_used=False).update(is_used=True)
        
        # Create new reset token
        reset_token = PasswordResetToken.objects.create(user=user)
        
        # Create reset link (you'll need to update this with your frontend URL)
        reset_link = f"https://bionexusgaia.com/reset-password?token={reset_token.token}"
        
        subject = 'Reset your BioNexus Gaia password'
        message = f'''
Hello {user.username},

You requested a password reset for your BioNexus Gaia account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
BioNexus Gaia Team
        '''
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            pass


class ResetPasswordSerializer(serializers.Serializer):
    """
    Serializer for resetting password with token.
    
    Used to reset a user's password using a secure token received via email.
    """
    token = serializers.CharField(help_text="Password reset token received via email")
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        help_text="New password (must meet security requirements)"
    )
    confirm_password = serializers.CharField(write_only=True, required=True, help_text="Confirm new password")
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords don't match."})
        
        token = attrs.get('token')
        try:
            reset_token = PasswordResetToken.objects.get(token=token, is_used=False)
            if reset_token.is_expired():
                raise serializers.ValidationError({"token": "Reset token has expired."})
            attrs['reset_token'] = reset_token
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid reset token."})
        
        return attrs


class AcceptTermsSerializer(serializers.Serializer):
    """
    Serializer for accepting terms and conditions.
    
    Used to record user's acceptance of the platform's terms and conditions.
    """
    accept_terms = serializers.BooleanField(help_text="Must be true to accept terms and conditions")
    
    def validate_accept_terms(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms and conditions.")
        return value