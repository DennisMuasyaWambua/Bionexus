import tempfile
import uuid
from io import BytesIO
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image

from .models import BiodiversityRecord

User = get_user_model()


class BiodiversityEndpointsTestCase(TestCase):
    """Test suite for biodiversity API endpoints."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        # Create test biodiversity record
        self.test_record = BiodiversityRecord.objects.create(
            contributor=self.user,
            species_name='Accipiter cooperii',
            common_name='Cooper\'s Hawk',
            location=Point(-122.4194, 37.7749),  # San Francisco coordinates
            location_name='San Francisco, CA',
            observation_date='2024-12-01T10:00:00Z',
            notes='Beautiful hawk spotted in Golden Gate Park',
            is_public=True
        )
    
    def create_test_image(self):
        """Create a test image file for upload."""
        image = Image.new('RGB', (100, 100), color='red')
        image_file = BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        return SimpleUploadedFile(
            name='test_image.jpg',
            content=image_file.read(),
            content_type='image/jpeg'
        )
    
    def test_biodiversity_records_list_public(self):
        """Test listing biodiversity records without authentication."""
        response = self.client.get('/api/v1/biodiversity/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['species_name'], 'Accipiter cooperii')
    
    def test_biodiversity_records_list_authenticated(self):
        """Test listing biodiversity records with authentication."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/v1/biodiversity/records/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_biodiversity_record_success(self):
        """Test creating a new biodiversity record successfully."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'species_name': 'Falco peregrinus',
            'common_name': 'Peregrine Falcon',
            'latitude': 37.7849,
            'longitude': -122.4094,
            'location_name': 'Alcatraz Island',
            'observation_date': '2024-12-02T14:30:00Z',
            'notes': 'Falcon nest observed on cliff face',
            'is_public': True,
            'image': self.create_test_image()
        }
        
        response = self.client.post('/api/v1/biodiversity/records/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['species_name'], 'Falco peregrinus')
        self.assertEqual(response.data['contributor'], self.user.id)
    
    def test_create_biodiversity_record_no_media(self):
        """Test creating biodiversity record fails without media files."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'species_name': 'Falco peregrinus',
            'common_name': 'Peregrine Falcon',
            'latitude': 37.7849,
            'longitude': -122.4094,
            'location_name': 'Alcatraz Island',
            'observation_date': '2024-12-02T14:30:00Z',
            'notes': 'Falcon nest observed on cliff face',
            'is_public': True
        }
        
        response = self.client.post('/api/v1/biodiversity/records/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)
    
    def test_create_biodiversity_record_unauthenticated(self):
        """Test creating biodiversity record fails without authentication."""
        data = {
            'species_name': 'Falco peregrinus',
            'common_name': 'Peregrine Falcon',
            'latitude': 37.7849,
            'longitude': -122.4094,
            'observation_date': '2024-12-02T14:30:00Z',
            'image': self.create_test_image()
        }
        
        response = self.client.post('/api/v1/biodiversity/records/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_biodiversity_record(self):
        """Test retrieving a specific biodiversity record."""
        response = self.client.get(f'/api/v1/biodiversity/records/{self.test_record.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['species_name'], 'Accipiter cooperii')
    
    def test_update_biodiversity_record_owner(self):
        """Test updating biodiversity record by owner."""
        self.client.force_authenticate(user=self.user)
        
        data = {
            'species_name': 'Accipiter cooperii',
            'common_name': 'Cooper\'s Hawk (Adult)',
            'latitude': 37.7749,
            'longitude': -122.4194,
            'observation_date': '2024-12-01T10:00:00Z',
            'notes': 'Beautiful adult hawk spotted in Golden Gate Park',
            'image': self.create_test_image()
        }
        
        response = self.client.put(f'/api/v1/biodiversity/records/{self.test_record.id}/', data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['common_name'], 'Cooper\'s Hawk (Adult)')
    
    def test_delete_biodiversity_record_unauthorized(self):
        """Test deleting biodiversity record by non-owner fails."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        response = self.client.delete(f'/api/v1/biodiversity/records/{self.test_record.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_export_biodiversity_records_csv(self):
        """Test exporting biodiversity records as CSV."""
        # Add an image to the test record to ensure it shows up in exports
        from django.core.files.uploadedfile import SimpleUploadedFile
        self.test_record.image = self.create_test_image()
        self.test_record.save()
        
        # First verify the record exists
        records = BiodiversityRecord.objects.all()
        self.assertEqual(records.count(), 1, "Should have exactly one record")
        
        # Test the list endpoint first to ensure it's working
        list_response = self.client.get('/api/v1/biodiversity/records/')
        print(f"List endpoint status: {list_response.status_code}")
        print(f"List endpoint records: {len(list_response.data.get('results', []))}")
        
        # Export defaults to CSV format
        response = self.client.get('/api/v1/biodiversity/records/export/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment; filename="biodiversity_export.csv"', response['Content-Disposition'])
    
    def test_export_biodiversity_records_json(self):
        """Test exporting biodiversity records as JSON."""
        response = self.client.get('/api/v1/biodiversity/records/export/?format=json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertIn('attachment; filename="biodiversity_export.json"', response['Content-Disposition'])
    
    def test_validate_biodiversity_record(self):
        """Test validating a biodiversity record on blockchain."""
        self.client.force_authenticate(user=self.user)
        
        response = self.client.post(f'/api/v1/biodiversity/records/{self.test_record.id}/validate/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('blockchain_hash', response.data)
        
        # Refresh record from database
        self.test_record.refresh_from_db()
        self.assertTrue(self.test_record.is_verified)
        self.assertIsNotNone(self.test_record.blockchain_hash)
    
    def test_species_list_endpoint(self):
        """Test the species list endpoint."""
        response = self.client.get('/api/v1/biodiversity/species/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['scientific_name'], 'Accipiter cooperii')
        self.assertEqual(response.data['results'][0]['common_name'], 'Cooper\'s Hawk')
        self.assertEqual(response.data['results'][0]['observation_count'], 1)
    
    def test_geographic_filter(self):
        """Test geographic radius filtering."""
        # Search within 10km of San Francisco
        response = self.client.get('/api/v1/biodiversity/records/?lat=37.7749&lng=-122.4194&radius=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Search far away (should return no results)
        response = self.client.get('/api/v1/biodiversity/records/?lat=40.7128&lng=-74.0060&radius=10')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_search_functionality(self):
        """Test search functionality."""
        response = self.client.get('/api/v1/biodiversity/records/?search=hawk')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        response = self.client.get('/api/v1/biodiversity/records/?search=falcon')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)
    
    def test_ordering_functionality(self):
        """Test ordering functionality."""
        # Create another record with different date
        BiodiversityRecord.objects.create(
            contributor=self.user,
            species_name='Buteo jamaicensis',
            common_name='Red-tailed Hawk',
            location=Point(-122.4094, 37.7849),
            observation_date='2024-12-03T10:00:00Z',
            notes='Hawk circling overhead',
            is_public=True
        )
        
        # Test ordering by observation date (newest first)
        response = self.client.get('/api/v1/biodiversity/records/?ordering=-observation_date')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['species_name'], 'Buteo jamaicensis')
        
        # Test ordering by species name
        response = self.client.get('/api/v1/biodiversity/records/?ordering=species_name')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'][0]['species_name'], 'Accipiter cooperii')