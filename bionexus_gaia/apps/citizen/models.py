import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model

User = get_user_model()

class Mission(models.Model):
    """
    Model for citizen science missions/quests.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    # Mission parameters
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(null=True, blank=True)
    target_species = models.JSONField(null=True, blank=True)  # List of target species
    
    # Location (optional bounding box or point)
    location_name = models.CharField(max_length=255, blank=True)
    area = gis_models.PolygonField(geography=True, null=True, blank=True)
    
    # Rewards
    points_reward = models.IntegerField(default=100)
    badge_reward = models.CharField(max_length=255, blank=True)
    nft_reward = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Stats
    participants_count = models.PositiveIntegerField(default=0)
    observations_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]
    
    def __str__(self):
        return self.title


class MissionParticipation(models.Model):
    """
    Model for tracking user participation in missions.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mission_participations')
    mission = models.ForeignKey(Mission, on_delete=models.CASCADE, related_name='participations')
    joined_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    observations_count = models.PositiveIntegerField(default=0)
    points_earned = models.IntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'mission']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.mission.title}"


class CitizenObservation(models.Model):
    """
    Model for citizen science observations (reference to BiodiversityRecord).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    biodiversity_record = models.ForeignKey(
        'biodiversity.BiodiversityRecord',
        on_delete=models.CASCADE,
        related_name='citizen_observations'
    )
    mission = models.ForeignKey(
        Mission,
        on_delete=models.SET_NULL,
        related_name='observations',
        null=True,
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citizen_observations')
    points_awarded = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Observation by {self.user.username} for {self.mission.title if self.mission else 'No Mission'}"
