from rest_framework import serializers
from .models import AIModel, IdentificationFeedback

class AIModelSerializer(serializers.ModelSerializer):
    """
    Serializer for AI models.
    """
    class Meta:
        model = AIModel
        fields = [
            'id', 'name', 'version', 'description', 'model_type',
            'accuracy', 'created_at', 'updated_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class IdentificationFeedbackSerializer(serializers.ModelSerializer):
    """
    Serializer for identification feedback.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = IdentificationFeedback
        fields = [
            'id', 'user', 'user_username', 'biodiversity_record', 
            'ai_model', 'original_prediction', 'corrected_species', 
            'confidence', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        # Set the user from the request
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class IdentificationSerializer(serializers.Serializer):
    """
    Serializer for species identification requests.
    """
    image = serializers.ImageField(required=False)
    audio = serializers.FileField(required=False)
    video = serializers.FileField(required=False)
    latitude = serializers.FloatField(required=False)
    longitude = serializers.FloatField(required=False)
    observation_date = serializers.DateTimeField(required=False)
    
    def validate(self, data):
        """
        Validate that at least one media file is provided.
        """
        if not any(key in data for key in ['image', 'audio', 'video']):
            raise serializers.ValidationError(
                "At least one media file (image, audio, or video) must be provided."
            )
        return data


class TaxonomySerializer(serializers.Serializer):
    """
    Serializer for taxonomy data.
    """
    kingdom = serializers.CharField(required=True)
    phylum = serializers.CharField(required=True)
    class_name = serializers.CharField(required=True)
    order = serializers.CharField(required=True)
    family = serializers.CharField(required=True)
    genus = serializers.CharField(required=True)
    species = serializers.CharField(required=True)
    common_names = serializers.ListField(child=serializers.CharField(), required=True)