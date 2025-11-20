from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import UserActivity, Notification, Project, ProjectParticipation, Reward

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
        fields = [
            'username', 'password', 'password2', 'email', 
            'first_name', 'last_name', 'bio', 'profile_image'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            bio=validated_data.get('bio', ''),
            profile_image=validated_data.get('profile_image', None)
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
        
        return user


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