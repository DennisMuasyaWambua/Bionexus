# BioNexus Gaia Platform

BioNexus Gaia is an AI and blockchain-powered biodiversity conservation platform. The system integrates species identification, citizen science, blockchain data registry, and NFT rewards to revolutionize ecological conservation through transparency and community engagement.

## Setup Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL with PostGIS extension
- Virtual environment (recommended)

### Installation
1. Clone the repository
```bash
git clone [repository-url]
cd bionexus_gaia
```

2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key
DB_NAME=bionexus_gaia
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

5. Apply migrations
```bash
python manage.py migrate
```

6. Create a superuser
```bash
python manage.py createsuperuser
```

7. Run the development server
```bash
python manage.py runserver
```

## API Documentation

The API documentation is available at `/api/schema/swagger/` when the server is running.

### Core API Endpoints

#### Biodiversity Registry APIs
- `POST /api/v1/biodiversity/records/` - Upload biodiversity observation
- `GET /api/v1/biodiversity/records/` - List/search records
- `GET /api/v1/biodiversity/records/{id}/` - Retrieve specific record
- `PUT /api/v1/biodiversity/records/{id}/` - Update record
- `DELETE /api/v1/biodiversity/records/{id}/` - Delete record
- `GET /api/v1/biodiversity/records/export/` - Export data (CSV/JSON)
- `POST /api/v1/biodiversity/records/{id}/validate/` - Blockchain validation

#### AI Species Identification APIs
- `POST /api/v1/ai/identify/` - Species identification from media
- `POST /api/v1/ai/identify/batch/` - Batch identification
- `GET /api/v1/ai/models/info/` - Model info & confidence metrics
- `POST /api/v1/ai/feedback/` - Submit correction feedback
- `GET /api/v1/ai/taxonomy/{species}/` - Taxonomy tree data

#### Citizen Science APIs
- `GET /api/v1/citizen/missions/` - Available missions/quests
- `POST /api/v1/citizen/missions/{id}/join/` - Join mission
- `GET /api/v1/citizen/leaderboard/` - Community leaderboard
- `GET /api/v1/citizen/map/` - Interactive biodiversity map
- `POST /api/v1/citizen/observations/` - Submit geo-tagged observation

#### User Management APIs
- `POST /api/v1/auth/register/` - User registration (Web2)
- `POST /api/v1/auth/login/` - Login endpoint
- `POST /api/v1/auth/wallet-connect/` - Web3 wallet authentication
- `GET /api/v1/users/profile/` - User profile & dashboard
- `PUT /api/v1/users/profile/` - Update profile
- `GET /api/v1/users/stats/` - User contribution statistics

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.