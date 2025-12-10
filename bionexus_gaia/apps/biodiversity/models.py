import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model

User = get_user_model()

class BiodiversityRecord(models.Model):
    """
    Model for storing biodiversity observations with geospatial data, media files,
    and blockchain verification metadata.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    contributor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='biodiversity_records')
    species_name = models.CharField(max_length=255, blank=True)
    common_name = models.CharField(max_length=255, blank=True)
    
    # Media files
    image = models.ImageField(upload_to='biodiversity/images/', blank=True, null=True)
    audio = models.FileField(upload_to='biodiversity/audio/', blank=True, null=True)
    video = models.FileField(upload_to='biodiversity/videos/', blank=True, null=True)
    
    # Location data (PostGIS)
    location = gis_models.PointField(geography=True)
    location_name = models.CharField(max_length=255, blank=True)
    
    # Metadata
    observation_date = models.DateTimeField()
    notes = models.TextField(blank=True)
    is_public = models.BooleanField(default=True)
    
    # AI & Blockchain
    ai_prediction = models.JSONField(blank=True, null=True)
    ai_confidence = models.FloatField(blank=True, null=True)
    blockchain_hash = models.CharField(max_length=66, blank=True)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-observation_date']
        indexes = [
            models.Index(fields=['species_name']),
            models.Index(fields=['observation_date']),
            models.Index(fields=['contributor']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_public']),
        ]
    
    def __str__(self):
        return f"{self.species_name or 'Unknown'} observed by {self.contributor.username} on {self.observation_date.date()}"
