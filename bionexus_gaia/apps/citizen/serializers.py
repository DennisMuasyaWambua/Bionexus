from rest_framework import serializers
from django.contrib.gis.geos import Polygon
from .models import Mission, MissionParticipation, CitizenObservation
from bionexus_gaia.apps.biodiversity.serializers import BiodiversityRecordSerializer
from bionexus_gaia.apps.biodiversity.models import BiodiversityRecord

class MissionSerializer(serializers.ModelSerializer):
    """
    Serializer for citizen science missions.
    """
    # For handling polygon coordinates
    area_coordinates = serializers.ListField(
        child=serializers.ListField(
            child=serializers.ListField(
                child=serializers.FloatField()
            )
        ),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Mission
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date',
            'target_species', 'location_name', 'area', 'area_coordinates',
            'points_reward', 'badge_reward', 'nft_reward', 'is_active',
            'participants_count', 'observations_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'participants_count', 'observations_count', 'created_at', 'updated_at']
        extra_kwargs = {
            'area': {'read_only': True},
        }
    
    def create(self, validated_data):
        """
        Create a mission with polygon area if provided.
        """
        area_coordinates = validated_data.pop('area_coordinates', None)
        
        if area_coordinates:
            # Create polygon from coordinates
            polygon = Polygon(area_coordinates[0], srid=4326)
            validated_data['area'] = polygon
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Update a mission with polygon area if provided.
        """
        area_coordinates = validated_data.pop('area_coordinates', None)
        
        if area_coordinates:
            # Create polygon from coordinates
            polygon = Polygon(area_coordinates[0], srid=4326)
            instance.area = polygon
        
        return super().update(instance, validated_data)


class MissionParticipationSerializer(serializers.ModelSerializer):
    """
    Serializer for mission participation.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    mission_title = serializers.CharField(source='mission.title', read_only=True)
    
    class Meta:
        model = MissionParticipation
        fields = [
            'id', 'user', 'username', 'mission', 'mission_title',
            'joined_at', 'completed_at', 'observations_count',
            'points_earned', 'is_completed'
        ]
        read_only_fields = [
            'id', 'user', 'username', 'joined_at', 'completed_at',
            'observations_count', 'points_earned', 'is_completed'
        ]
    
    def create(self, validated_data):
        """
        Set the user from the request.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CitizenObservationSerializer(serializers.ModelSerializer):
    """
    Serializer for citizen science observations.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    mission_title = serializers.SerializerMethodField()
    biodiversity_record_data = serializers.SerializerMethodField()
    
    class Meta:
        model = CitizenObservation
        fields = [
            'id', 'biodiversity_record', 'biodiversity_record_data',
            'mission', 'mission_title', 'user', 'username',
            'points_awarded', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'username', 'points_awarded', 'created_at']
    
    def get_mission_title(self, obj):
        if obj.mission:
            return obj.mission.title
        return None
    
    def get_biodiversity_record_data(self, obj):
        return {
            'id': obj.biodiversity_record.id,
            'species_name': obj.biodiversity_record.species_name,
            'common_name': obj.biodiversity_record.common_name,
            'observation_date': obj.biodiversity_record.observation_date,
            'image': obj.biodiversity_record.image.url if obj.biodiversity_record.image else None
        }
    
    def create(self, validated_data):
        """
        Set the user from the request and calculate points.
        """
        validated_data['user'] = self.context['request'].user
        
        # Calculate points based on mission if applicable
        if validated_data.get('mission'):
            mission = validated_data['mission']
            validated_data['points_awarded'] = mission.points_reward
            
            # Update mission participation if exists
            participation, created = MissionParticipation.objects.get_or_create(
                user=validated_data['user'],
                mission=mission,
                defaults={'observations_count': 1, 'points_earned': mission.points_reward}
            )
            
            if not created:
                participation.observations_count += 1
                participation.points_earned += mission.points_reward
                participation.save()
            
            # Update mission stats
            mission.observations_count += 1
            mission.save()
        
        return super().create(validated_data)


class LeaderboardEntrySerializer(serializers.Serializer):
    """
    Serializer for leaderboard entries.
    """
    user_id = serializers.UUIDField()
    username = serializers.CharField()
    total_points = serializers.IntegerField()
    observations_count = serializers.IntegerField()
    missions_completed = serializers.IntegerField()
    rank = serializers.IntegerField()


class MapDataSerializer(serializers.Serializer):
    """
    Serializer for biodiversity map data.
    """
    id = serializers.UUIDField()
    species_name = serializers.CharField()
    common_name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    observation_date = serializers.DateTimeField()
    image_url = serializers.URLField(allow_null=True)
    contributor_username = serializers.CharField()
    is_verified = serializers.BooleanField()