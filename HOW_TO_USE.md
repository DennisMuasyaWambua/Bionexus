# BioNexus Gaia Platform - How to Use

This guide provides comprehensive instructions for using the BioNexus Gaia API, including setting up the environment, authentication, and working with the different API modules.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Working with Biodiversity Records](#working-with-biodiversity-records)
4. [AI Species Identification](#ai-species-identification)
5. [Citizen Science Features](#citizen-science-features)
6. [User Management](#user-management)
7. [Using the Postman Collection](#using-the-postman-collection)
8. [Web3 Integration](#web3-integration)
9. [API Permissions](#api-permissions)
10. [Error Handling](#error-handling)
11. [PostGIS Spatial Features](#postgis-spatial-features)
12. [Advanced Usage](#advanced-usage)

## Getting Started

### Prerequisites

Before using the BioNexus Gaia API, ensure you have the following:

- Python 3.8+ with pip
- PostgreSQL database with PostGIS extension
- Git for version control
- Postman (optional, for API testing)

### Installation

1. Clone the repository and navigate to the project directory:
   ```bash
   git clone [repository-url]
   cd bionexus_gaia
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy the example environment file and update it with your own settings:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred editor
   ```

5. Run migrations:
   ```bash
   python manage.py migrate
   ```

6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Access the API documentation at:
   ```
   http://localhost:8000/api/schema/swagger/
   ```

## Authentication

The BioNexus Gaia platform supports two authentication methods:

### Email/Password Authentication

1. **Register a new account**:
   ```http
   POST /api/v1/auth/register/
   ```
   ```json
   {
       "username": "your_username",
       "email": "your.email@example.com",
       "password": "YourSecurePassword123",
       "password2": "YourSecurePassword123",
       "first_name": "Your",
       "last_name": "Name"
   }
   ```

2. **Login to get JWT tokens**:
   ```http
   POST /api/v1/auth/login/
   ```
   ```json
   {
       "username": "your_username",
       "password": "YourSecurePassword123"
   }
   ```
   This returns access and refresh tokens:
   ```json
   {
       "access": "eyJ0eXAiOiJKV...",
       "refresh": "eyJ0eXAiOiJKV..."
   }
   ```

3. **Use the JWT token in subsequent requests**:
   Add the token to the Authorization header:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV...
   ```

4. **Refresh an expired token**:
   ```http
   POST /api/v1/auth/token/refresh/
   ```
   ```json
   {
       "refresh": "eyJ0eXAiOiJKV..."
   }
   ```

### Web3 Wallet Authentication

1. **Register with a blockchain wallet**:
   ```http
   POST /api/v1/auth/wallet-register/
   ```
   ```json
   {
       "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
       "wallet_type": "metamask",
       "signature": "0x...",
       "message": "I want to register with BioNexus Gaia with address 0x1234567890abcdef1234567890abcdef12345678",
       "username": "wallet_user",
       "email": "wallet@example.com"
   }
   ```

2. **Authenticate with a wallet**:
   ```http
   POST /api/v1/auth/wallet-connect/
   ```
   ```json
   {
       "wallet_address": "0x1234567890abcdef1234567890abcdef12345678",
       "signature": "0x...",
       "message": "I want to connect to BioNexus Gaia with address 0x1234567890abcdef1234567890abcdef12345678"
   }
   ```
   
## Working with Biodiversity Records

Biodiversity records are the core data of the platform. They represent observations of species in the field.

### Creating a Biodiversity Record

To create a new biodiversity record with PostGIS spatial data, make a multipart form POST request:

```http
POST /api/v1/biodiversity/records/
Content-Type: application/json
Authorization: Bearer your_access_token
```

**JSON Payload Example:**
```json
{
    "species_name": "Pinus sylvestris",
    "common_name": "Scots Pine",
    "latitude": 60.1695,
    "longitude": 24.9354,
    "location_name": "Helsinki Central Park",
    "observation_date": "2024-01-15T14:30:00Z",
    "notes": "Large specimen near the walking trail",
    "is_public": true,
    "ai_prediction": "Pinus sylvestris",
    "ai_confidence": 0.95
}
```

**Response:**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "contributor": "user123",
    "contributor_username": "naturalist_joe",
    "species_name": "Pinus sylvestris",
    "common_name": "Scots Pine",
    "location": "POINT(24.9354 60.1695)",
    "latitude": 60.1695,
    "longitude": 24.9354,
    "location_name": "Helsinki Central Park",
    "observation_date": "2024-01-15T14:30:00Z",
    "is_verified": false,
    "created_at": "2024-01-15T14:35:22Z"
}
```

Required fields:
- `latitude`: Geographical coordinate (WGS84 decimal degrees, e.g., 60.1695)
- `longitude`: Geographical coordinate (WGS84 decimal degrees, e.g., 24.9354)
- `observation_date`: ISO format date-time (e.g., 2023-06-15T14:30:00Z)

Optional fields:
- `species_name`: Scientific name (e.g., "Pinus sylvestris")
- `common_name`: Common name (e.g., "Scots Pine")
- `location_name`: Text description of location (e.g., "Helsinki Central Park")
- `notes`: Additional observations
- `is_public`: Boolean (default: true)
- `image`: File upload of the observed species
- `audio`: File upload (audio recording)
- `video`: File upload (video recording)
- `ai_prediction`: AI-suggested species name
- `ai_confidence`: AI confidence score (0.0-1.0)

**Note:** Coordinates are automatically converted to PostGIS Point geometry with SRID 4326 (WGS84).

### Listing and Filtering Records

```http
GET /api/v1/biodiversity/records/
```

**Basic Listing:**
```http
GET /api/v1/biodiversity/records/
```

**Spatial Filtering (PostGIS Proximity Search):**
```http
GET /api/v1/biodiversity/records/?lat=60.1695&lng=24.9354&radius=5
```

**Response Example:**
```json
{
    "count": 25,
    "next": "http://example.com/api/v1/biodiversity/records/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "species_name": "Pinus sylvestris",
            "common_name": "Scots Pine",
            "location": "POINT(24.9354 60.1695)",
            "latitude": 60.1695,
            "longitude": 24.9354,
            "location_name": "Helsinki Central Park",
            "observation_date": "2024-01-15T14:30:00Z",
            "is_verified": false,
            "contributor_username": "naturalist_joe"
        }
    ]
}
```

Available filters:
- `species_name`: Filter by scientific name
- `common_name`: Filter by common name
- `location_name`: Filter by location
- `observation_date_min`: Filter by date (from)
- `observation_date_max`: Filter by date (to)
- `is_verified`: Filter by blockchain verification status
- `contributor_id`: Filter by user ID

**PostGIS Spatial Filters:**
- `lat`: Latitude for proximity search (decimal degrees)
- `lng`: Longitude for proximity search (decimal degrees) 
- `radius`: Search radius in kilometers (used with lat/lng)

### Exporting Spatial Data

Export biodiversity records with geographic coordinates:

```http
GET /api/v1/biodiversity/records/export/?format=json
```

**JSON Export Response:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "contributor": "naturalist_joe",
        "species_name": "Pinus sylvestris",
        "common_name": "Scots Pine",
        "latitude": 60.1695,
        "longitude": 24.9354,
        "location_name": "Helsinki Central Park",
        "observation_date": "2024-01-15T14:30:00Z",
        "notes": "Large specimen near the walking trail",
        "ai_confidence": 0.95,
        "is_verified": false,
        "created_at": "2024-01-15T14:35:22Z"
    }
]
```

**CSV Export:** Contains the same data in comma-separated format, suitable for GIS software import.

Available formats:
- `csv`: Comma-separated values (includes latitude/longitude columns)
- `json`: JSON format with spatial coordinates

**Note:** Exported data includes extracted latitude/longitude coordinates from PostGIS Point geometry for easy use in GIS applications and mapping tools.

### Blockchain Validation

To validate a record on the blockchain:

```http
POST /api/v1/biodiversity/records/{record_id}/validate/
```

This adds the record data to the blockchain for immutable verification.

## AI Species Identification

The platform provides AI-powered species identification from media files.

### Identifying a Species

```http
POST /api/v1/ai/identify/
```

Required parameters (at least one):
- `image`: Image file
- `audio`: Audio file
- `video`: Video file

Optional parameters:
- `latitude`: Geographic coordinate
- `longitude`: Geographic coordinate
- `save_record`: Boolean, whether to create a biodiversity record (default: false)

### Batch Identification

For processing multiple files at once:

```http
POST /api/v1/ai/identify/batch/
```

```json
[
    {
        "image": "https://example.com/image1.jpg"
    },
    {
        "audio": "https://example.com/audio1.mp3",
        "latitude": 40.7128,
        "longitude": -74.0060
    }
]
```

### Providing Feedback on AI Predictions

If the AI makes an incorrect identification, you can provide feedback:

```http
POST /api/v1/ai/feedback/
```

```json
{
    "biodiversity_record": "record_uuid",
    "ai_model": "model_uuid",
    "original_prediction": {
        "species": "Quercus rubra",
        "confidence": 0.92
    },
    "corrected_species": "Quercus alba",
    "notes": "This is actually a white oak, not a red oak."
}
```

### Getting Taxonomy Information

```http
GET /api/v1/ai/taxonomy/{species_name}/
```

## Citizen Science Features

The citizen science module allows users to participate in biodiversity missions and contribute to conservation efforts. Missions support PostGIS polygon boundaries for defining geographic areas.

### Creating a Mission (Admin Only)

Create a new mission with a geographic boundary:

```http
POST /api/v1/citizen/missions/
Content-Type: application/json
Authorization: Bearer admin_access_token
```

**JSON Payload:**
```json
{
    "title": "Urban Wildlife Survey - Helsinki",
    "description": "Document wildlife species in urban Helsinki parks",
    "start_date": "2024-03-01T00:00:00Z",
    "end_date": "2024-03-31T23:59:59Z",
    "target_species": ["Sciurus vulgaris", "Corvus cornix", "Turdus pilaris"],
    "location_name": "Helsinki Metropolitan Area",
    "area_coordinates": [
        [
            [24.9100, 60.1500],
            [25.0000, 60.1500],
            [25.0000, 60.2000],
            [24.9100, 60.2000],
            [24.9100, 60.1500]
        ]
    ],
    "points_reward": 50,
    "badge_reward": "Urban Explorer",
    "nft_reward": "helsinki_wildlife_2024",
    "is_active": true
}
```

**Response:**
```json
{
    "id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Urban Wildlife Survey - Helsinki",
    "description": "Document wildlife species in urban Helsinki parks",
    "start_date": "2024-03-01T00:00:00Z",
    "end_date": "2024-03-31T23:59:59Z",
    "target_species": ["Sciurus vulgaris", "Corvus cornix", "Turdus pilaris"],
    "location_name": "Helsinki Metropolitan Area",
    "area": "POLYGON((24.91 60.15, 25.0 60.15, 25.0 60.2, 24.91 60.2, 24.91 60.15))",
    "points_reward": 50,
    "is_active": true,
    "participants_count": 0,
    "observations_count": 0,
    "created_at": "2024-02-15T10:00:00Z"
}
```

**Note:** The `area_coordinates` field accepts GeoJSON-style polygon coordinates and is converted to PostGIS Polygon geometry with SRID 4326.

### Joining a Mission

1. List available missions:
   ```http
   GET /api/v1/citizen/missions/?is_active=true
   ```

2. Get mission details:
   ```http
   GET /api/v1/citizen/missions/{mission_id}/
   ```

3. Join a mission:
   ```http
   POST /api/v1/citizen/missions/{mission_id}/join/
   ```

**Join Response:**
```json
{
    "id": "770e8400-e29b-41d4-a716-446655440002",
    "user": "user123",
    "username": "naturalist_joe",
    "mission": "660e8400-e29b-41d4-a716-446655440001",
    "mission_title": "Urban Wildlife Survey - Helsinki",
    "joined_at": "2024-02-20T14:30:00Z",
    "completed_at": null,
    "observations_count": 0,
    "points_earned": 0,
    "is_completed": false
}
```

### Submitting Observations for Missions

Link a biodiversity record to a mission for points and participation:

```http
POST /api/v1/citizen/observations/
Content-Type: application/json
Authorization: Bearer your_access_token
```

**JSON Payload:**
```json
{
    "biodiversity_record": "550e8400-e29b-41d4-a716-446655440000",
    "mission": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response:**
```json
{
    "id": "880e8400-e29b-41d4-a716-446655440003",
    "biodiversity_record": "550e8400-e29b-41d4-a716-446655440000",
    "biodiversity_record_data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "species_name": "Pinus sylvestris",
        "common_name": "Scots Pine",
        "observation_date": "2024-01-15T14:30:00Z",
        "image": "https://example.com/media/biodiversity/image_123.jpg"
    },
    "mission": "660e8400-e29b-41d4-a716-446655440001",
    "mission_title": "Urban Wildlife Survey - Helsinki",
    "user": "user123",
    "username": "naturalist_joe",
    "points_awarded": 50,
    "created_at": "2024-02-20T15:00:00Z"
}
```

### Checking the Leaderboard

```http
GET /api/v1/citizen/leaderboard/?period=all
```

Available periods:
- `all`: All time
- `month`: Current month
- `week`: Current week

### Viewing the Interactive Biodiversity Map

Get spatial data for map visualization with PostGIS coordinates:

```http
GET /api/v1/citizen/map/
```

**Response:**
```json
[
    {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "species_name": "Pinus sylvestris",
        "common_name": "Scots Pine",
        "latitude": 60.1695,
        "longitude": 24.9354,
        "observation_date": "2024-01-15T14:30:00Z",
        "image_url": "https://example.com/media/biodiversity/image_123.jpg",
        "contributor_username": "naturalist_joe",
        "is_verified": false
    },
    {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "species_name": "Sciurus vulgaris",
        "common_name": "Red Squirrel",
        "latitude": 60.1720,
        "longitude": 24.9400,
        "observation_date": "2024-01-16T09:15:00Z",
        "image_url": "https://example.com/media/biodiversity/image_124.jpg",
        "contributor_username": "wildlife_watcher",
        "is_verified": true
    }
]
```

This returns geospatial data extracted from PostGIS Point geometry for display on interactive maps. Limited to 1000 records for performance.

## User Management

### Viewing and Updating Your Profile

1. Get your profile:
   ```http
   GET /api/v1/users/profile/
   ```

2. Update your profile:
   ```http
   PUT /api/v1/users/profile/
   ```

   ```json
   {
       "bio": "I'm passionate about conservation and biodiversity.",
       "first_name": "Updated",
       "last_name": "Name",
       "notification_preferences": {
           "email_notifications": true,
           "mission_updates": true
       }
   }
   ```

### Getting User Statistics

```http
GET /api/v1/users/stats/
```

This returns user contribution statistics:
- Total observations
- Verified observations
- Total missions
- Completed missions
- Total points
- Badges
- Leaderboard position

### Viewing Activity History

```http
GET /api/v1/users/activities/
```

## Using the Postman Collection

A Postman collection is provided to make API testing easier:

1. Import the `BioNexus_Gaia_API.postman_collection.json` file into Postman
2. Set the `base_url` variable to your server address (default: http://localhost:8000)
3. Follow these steps to test the API:
   - Register a user or login
   - Copy the returned access token to the `access_token` collection variable
   - Copy the refresh token to the `refresh_token` collection variable
   - Use the other endpoints with authentication already set up

## Web3 Integration

The platform integrates with blockchain technology for both authentication and data verification.

### Web3 Authentication Flow

1. User connects their Web3 wallet (MetaMask, WalletConnect, etc.)
2. Platform generates a message for the user to sign
3. User signs the message with their private key
4. Platform verifies the signature against the wallet address
5. If valid, the platform issues a JWT token for API access

### Record Verification Flow

1. User creates a biodiversity record
2. User requests blockchain verification
3. Record data is hashed and sent to the blockchain
4. Blockchain returns a transaction hash
5. Record is marked as verified with the blockchain hash

## API Permissions

The BioNexus Gaia API implements the following permission model:

| Endpoint | Anonymous | Authenticated | Record Owner | Admin |
|----------|-----------|---------------|--------------|-------|
| List Records | Public only | Public + Own | Public + Own | All |
| Create Record | No | Yes | Yes | Yes |
| Update Record | No | Own only | Own only | All |
| Delete Record | No | Own only | Own only | All |
| View Missions | Public only | All | All | All |
| Create Mission | No | No | No | Yes |
| Join Mission | No | Yes | Yes | Yes |
| Submit Feedback | No | Yes | Yes | Yes |

## Error Handling

The API uses standard HTTP status codes:

- 200: OK - The request succeeded
- 201: Created - A new resource was created
- 400: Bad Request - The request was invalid
- 401: Unauthorized - Authentication is required
- 403: Forbidden - The user does not have permission
- 404: Not Found - The resource does not exist
- 500: Internal Server Error - Something went wrong on the server

Error responses include a JSON object with details:

```json
{
    "detail": "Error message",
    "code": "error_code",
    "errors": {
        "field_name": [
            "Field-specific error message"
        ]
    }
}
```

## PostGIS Spatial Features

The BioNexus Gaia platform leverages PostGIS for advanced geospatial functionality. All spatial data uses the WGS84 coordinate system (SRID 4326).

### Supported Spatial Data Types

1. **Point Geometry**: Used for biodiversity record locations
   - Stored as PostGIS `POINT(longitude, latitude)`
   - Accessible as separate `latitude` and `longitude` fields in API responses
   - Supports distance-based queries and proximity searches

2. **Polygon Geometry**: Used for citizen science mission boundaries  
   - Stored as PostGIS `POLYGON` with coordinate rings
   - Created from GeoJSON-style coordinate arrays
   - Defines geographic areas for mission participation

### Spatial Query Operations

**Proximity Search:**
```http
GET /api/v1/biodiversity/records/?lat=60.1695&lng=24.9354&radius=5
```
Returns all records within 5 kilometers of the specified coordinates using PostGIS distance calculations.

**Geographic Filtering:**
- Radius searches use PostGIS `ST_DWithin` function
- Distance calculations are performed on the Earth's surface (geography=True)
- Supports kilometer-based radius filtering for intuitive distance queries

### Coordinate System Details

- **SRID**: 4326 (World Geodetic System 1984)
- **Format**: Decimal degrees (e.g., latitude: 60.1695, longitude: 24.9354)
- **Range**: Latitude: -90 to 90, Longitude: -180 to 180
- **Precision**: Stored with full double precision for accurate location data

### GIS Integration

Exported data includes coordinate fields suitable for:
- QGIS and ArcGIS import
- Google Maps and OpenStreetMap integration  
- GeoJSON format conversion
- Shapefile generation

## Advanced Usage

### Filtering Biodiversity Records by Geographic Area

```http
GET /api/v1/biodiversity/records/?lat=40.7128&lng=-74.0060&radius=10
```

This returns records within 10 kilometers of the specified coordinates using PostGIS spatial indexing for optimal performance.

### Creating and Using AI Model Feedback Loop

1. Identify a species using the AI
2. Create a biodiversity record
3. If identification is incorrect, submit feedback
4. The platform uses this feedback to improve the AI models

### Implementing Custom Citizen Science Missions

Administrators can create custom missions targeting specific:
- Geographic areas
- Species of interest
- Time periods
- Conservation goals

Users can join these missions and earn points for their contributions.

---

For more detailed technical information, refer to the API documentation at `/api/schema/swagger/` when the server is running.

For additional support, contact the BioNexus Gaia development team.