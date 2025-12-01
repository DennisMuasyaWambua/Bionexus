import uuid
import random
import string
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class User(AbstractUser):
    """
    Custom user model with additional fields for blockchain wallet integration and OAuth.
    """
    
    ROLE_CHOICES = [
        ('contributor', _('Contributor')),
        ('researcher', _('Researcher')),
        ('expert', _('Expert')),
    ]
    
    AFFILIATION_CHOICES = [
        ('student', _('Student')),
        ('educator_researcher', _('Educator/Researcher')),
        ('policy_maker', _('Policy Maker')),
        ('tech_enthusiast', _('Tech Enthusiast')),
        ('climate_advocate', _('Climate Advocate')),
        ('nature_enthusiast', _('Nature Enthusiast')),
        ('media_personnel', _('Media Personnel')),
    ]
    
    CONTRIBUTION_METHOD_CHOICES = [
        ('species_observation', _('Species Observation')),
        ('habitat_restoration', _('Habitat Restoration')),
        ('climate_advocacy', _('Climate Advocacy')),
        ('eco_photography', _('Eco Photography')),
        ('community_support', _('Community Support')),
    ]
    
    SKILL_LEVEL_CHOICES = [
        ('beginner', _('Beginner')),
        ('enthusiast', _('Enthusiast')),
        ('expert', _('Expert')),
    ]
    
    OAUTH_PROVIDER_CHOICES = [
        ('google', _('Google')),
        ('github', _('GitHub')),
        ('facebook', _('Facebook')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    wallet_address = models.CharField(max_length=42, blank=True, null=True, unique=True)
    wallet_type = models.CharField(max_length=20, blank=True, null=True)  # 'metamask', 'walletconnect', etc.
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # User role and onboarding
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True, default='contributor')
    onboarding_completed = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=0)
    
    # Additional onboarding fields
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    affiliation = models.CharField(max_length=30, choices=AFFILIATION_CHOICES, blank=True, null=True)
    contribution_method = models.JSONField(default=list, blank=True, null=True)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVEL_CHOICES, blank=True, null=True)
    
    # OAuth integration
    oauth_provider = models.CharField(max_length=20, choices=OAUTH_PROVIDER_CHOICES, blank=True, null=True)
    oauth_id = models.CharField(max_length=100, blank=True, null=True)
    
    # User stats
    total_points = models.IntegerField(default=0)
    observations_count = models.IntegerField(default=0)
    badges = models.JSONField(default=list, blank=True, null=True)
    
    # Integration fields
    web3_nonce = models.CharField(max_length=100, blank=True, null=True)  # For Web3 authentication
    
    # User settings
    notification_preferences = models.JSONField(default=dict, blank=True, null=True)
    
    # Email verification
    email_verified = models.BooleanField(default=False)
    
    # Terms acceptance
    terms_accepted = models.BooleanField(default=False)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.username


class UserActivity(models.Model):
    """
    Model for tracking user activity and achievements.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)  # 'observation', 'mission_complete', etc.
    description = models.TextField()
    points_earned = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type} on {self.created_at.date()}"


class Notification(models.Model):
    """
    Model for user notifications.
    """
    NOTIFICATION_TYPES = [
        ('general', _('General')),
        ('achievement', _('Achievement')),
        ('mission', _('Mission')),
        ('observation', _('Observation')),
        ('project', _('Project')),
        ('reward', _('Reward')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='general')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_url = models.URLField(blank=True, null=True)
    metadata = models.JSONField(default=dict, blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class Project(models.Model):
    """
    Model for research projects that users can join.
    """
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('paused', _('Paused')),
        ('draft', _('Draft')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=500)
    image = models.ImageField(upload_to='projects/', blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    participants = models.ManyToManyField(User, through='ProjectParticipation', related_name='joined_projects')
    max_participants = models.IntegerField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.JSONField(default=list, blank=True, null=True)
    requirements = models.TextField(blank=True)
    rewards_description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('project')
        verbose_name_plural = _('projects')
    
    def __str__(self):
        return self.title


class ProjectParticipation(models.Model):
    """
    Model for tracking user participation in projects.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, default='participant')
    contributions_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['user', 'project']
        verbose_name = _('project participation')
        verbose_name_plural = _('project participations')
    
    def __str__(self):
        return f"{self.user.username} - {self.project.title}"


class Reward(models.Model):
    """
    Model for user rewards and achievements.
    """
    REWARD_TYPES = [
        ('badge', _('Badge')),
        ('points', _('Points')),
        ('certificate', _('Certificate')),
        ('nft', _('NFT')),
        ('token', _('Token')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rewards')
    title = models.CharField(max_length=200)
    description = models.TextField()
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPES)
    icon = models.ImageField(upload_to='rewards/', blank=True, null=True)
    points_value = models.IntegerField(default=0)
    earned_at = models.DateTimeField(auto_now_add=True)
    criteria = models.TextField()  # What was accomplished to earn this
    metadata = models.JSONField(default=dict, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-earned_at']
        verbose_name = _('reward')
        verbose_name_plural = _('rewards')
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class EmailVerification(models.Model):
    """
    Model for email verification codes.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verifications')
    verification_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('email verification')
        verbose_name_plural = _('email verifications')
    
    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = self.generate_verification_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def generate_verification_code(self):
        return ''.join(random.choices(string.digits, k=6))
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.user.email} - {self.verification_code}"


class PasswordResetToken(models.Model):
    """
    Model for password reset tokens.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('password reset token')
        verbose_name_plural = _('password reset tokens')
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=1)
        super().save(*args, **kwargs)
    
    def generate_token(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"{self.user.email} - {self.token[:8]}..."


class TermsAndConditions(models.Model):
    """
    Model for managing terms and conditions content and versions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField()  # Keep for backward compatibility
    sections = models.JSONField(default=list, help_text="Structured sections for terms content")
    effective_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_date']
        verbose_name = _('terms and conditions')
        verbose_name_plural = _('terms and conditions')
    
    def __str__(self):
        return f"{self.title} - v{self.version}"
    
    @classmethod
    def get_current_terms(cls):
        """Get the current active terms and conditions."""
        return cls.objects.filter(is_active=True).first()


class UserTermsAcceptance(models.Model):
    """
    Model for tracking user acceptance of specific terms and conditions versions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='terms_acceptances')
    terms_version = models.ForeignKey(TermsAndConditions, on_delete=models.CASCADE, related_name='user_acceptances')
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    
    class Meta:
        unique_together = ['user', 'terms_version']
        ordering = ['-accepted_at']
        verbose_name = _('user terms acceptance')
        verbose_name_plural = _('user terms acceptances')
    
    def __str__(self):
        return f"{self.user.username} - {self.terms_version.version} - {self.accepted_at.date()}"
