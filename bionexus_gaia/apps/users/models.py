import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom user model with additional fields for blockchain wallet integration.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    wallet_address = models.CharField(max_length=42, blank=True, null=True, unique=True)
    wallet_type = models.CharField(max_length=20, blank=True, null=True)  # 'metamask', 'walletconnect', etc.
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
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
