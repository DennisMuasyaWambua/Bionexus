import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AIModel(models.Model):
    """
    Model for AI models metadata and metrics.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=20)
    description = models.TextField()
    model_type = models.CharField(max_length=50)  # 'image', 'audio', 'both'
    accuracy = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} v{self.version}"


class IdentificationFeedback(models.Model):
    """
    Model for storing user feedback on AI identifications.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='identification_feedback')
    biodiversity_record = models.ForeignKey(
        'biodiversity.BiodiversityRecord',
        on_delete=models.CASCADE,
        related_name='identification_feedback'
    )
    ai_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='feedback')
    original_prediction = models.JSONField()
    corrected_species = models.CharField(max_length=255)
    confidence = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Feedback by {self.user.username} on {self.biodiversity_record.id}"
