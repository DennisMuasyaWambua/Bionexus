import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user model with additional fields for blockchain wallet integration and OAuth.
    """
    
    ROLE_CHOICES = [
        ('contributor', _('Contributor')),
        ('researcher', _('Researcher')),
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
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    onboarding_completed = models.BooleanField(default=False)
    onboarding_step = models.IntegerField(default=0)
    
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
