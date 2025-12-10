from rest_framework import serializers
from django.contrib.gis.geos import Point
from .models import BiodiversityRecord

class BiodiversityRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for BiodiversityRecord model with support for geospatial data.
    """
    # Add fields for handling location coordinates
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    
    # Read-only fields calculated by the system
    blockchain_hash = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    contributor_username = serializers.CharField(source='contributor.username', read_only=True)
    
    class Meta:
        model = BiodiversityRecord
        fields = [
            'id', 'contributor', 'contributor_username', 'species_name', 'common_name',
            'image', 'audio', 'video', 'location', 'latitude', 'longitude', 'location_name',
            'observation_date', 'notes', 'is_public', 'ai_prediction', 'ai_confidence',
            'blockchain_hash', 'is_verified', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'contributor', 'blockchain_hash', 'is_verified', 'created_at', 'updated_at']
        extra_kwargs = {
            'location': {'read_only': True},
            'image': {'required': False},
            'observation_date': {'required': True},
        }
    
    def validate(self, attrs):
        """
        Ensure at least one media file is provided and required fields are present.
        """
        # Ensure at least one media file is provided
        if not any([attrs.get('image'), attrs.get('audio'), attrs.get('video')]):
            raise serializers.ValidationError({
                'non_field_errors': ['At least one media file (image, audio, or video) must be provided.']
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Custom create method to handle geospatial Point creation from lat/long.
        """
        # Extract latitude and longitude
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        
        # Create Point object
        location = Point(longitude, latitude, srid=4326)
        validated_data['location'] = location
        
        # Set the contributor to the current user
        validated_data['contributor'] = self.context['request'].user
        
        # Create the record
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Custom update method to handle geospatial Point update from lat/long.
        """
        # Update location if provided
        if 'latitude' in validated_data and 'longitude' in validated_data:
            latitude = validated_data.pop('latitude')
            longitude = validated_data.pop('longitude')
            instance.location = Point(longitude, latitude, srid=4326)
        
        # Update the record
        return super().update(instance, validated_data)
    
    def to_representation(self, instance):
        """
        Add latitude and longitude to the output representation.
        """
        representation = super().to_representation(instance)
        # Add coordinates to the representation for easier client-side handling
        if instance.location:
            representation['latitude'] = instance.location.y
            representation['longitude'] = instance.location.x
        return representation


class BiodiversityRecordExportSerializer(serializers.ModelSerializer):
    """
    Serializer for exporting biodiversity records (CSV/JSON).
    """
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    contributor = serializers.CharField(source='contributor.username')
    
    class Meta:
        model = BiodiversityRecord
        fields = [
            'id', 'contributor', 'species_name', 'common_name',
            'latitude', 'longitude', 'location_name', 'observation_date',
            'notes', 'ai_confidence', 'is_verified', 'created_at'
        ]
    
    def get_latitude(self, obj):
        if obj.location:
            return obj.location.y
        return None
    
    def get_longitude(self, obj):
        if obj.location:
            return obj.location.x
        return None