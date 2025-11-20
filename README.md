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

## Key Features

### 🔐 Multi-Modal Authentication
- **Web2**: Traditional email/password authentication
- **Web3**: Wallet-based authentication (MetaMask, WalletConnect)
- **OAuth**: Google OAuth integration for seamless login
- **JWT**: Secure token-based authentication

### 👤 User Onboarding & Role Management
- **Role-based System**: Contributors, Researchers, Experts
- **Guided Onboarding**: 5-step personalized setup process
- **Profile Management**: Complete user profile with stats and achievements

### 🔔 Real-time Notifications
- **Activity Tracking**: Real-time updates on user actions
- **Project Updates**: Notifications for project activities
- **Achievement Alerts**: Rewards and badge notifications
- **Mark as Read**: Granular notification management

### 📊 Projects & Collaboration
- **Research Projects**: Create and join collaborative research initiatives
- **Participant Management**: Track contributions and roles
- **Project Analytics**: Monitor participation and progress
- **Role-specific Actions**: Different capabilities based on user role

### 🏆 Rewards & Gamification
- **Point System**: Earn points for various activities
- **Badges & Achievements**: Unlock rewards for milestones
- **Leaderboards**: Community ranking and competition
- **NFT Integration**: Blockchain-based rewards (planned)

### 🎯 Personalized Dashboard
- **User Statistics**: Personal contribution metrics
- **Activity Feed**: Recent actions and achievements
- **Suggested Actions**: Role-based recommendations
- **Global Insights**: Community and platform statistics

### 🔍 Advanced Search
- **Global Search**: Search across users, projects, observations
- **Smart Suggestions**: Trending topics and popular searches
- **Contextual Results**: Personalized search results
- **Real-time Filtering**: Dynamic content discovery

### 📱 Modern API Design
- **RESTful Architecture**: Standard HTTP methods and status codes
- **Comprehensive Documentation**: Auto-generated OpenAPI/Swagger docs
- **Postman Collection**: Ready-to-use API collection
- **Error Handling**: Detailed error responses and validation

## API Documentation

The API documentation is available at `/api/schema/swagger/` when the server is running.

### Core API Endpoints

#### Authentication APIs
- `POST /api/v1/auth/register/` - User registration (Web2)
- `POST /api/v1/auth/login/` - Login endpoint
- `POST /api/v1/auth/google/` - Google OAuth authentication
- `POST /api/v1/auth/wallet-register/` - Web3 wallet registration
- `POST /api/v1/auth/wallet-connect/` - Web3 wallet authentication
- `POST /api/v1/auth/token/refresh/` - JWT token refresh

#### User Management APIs
- `GET /api/v1/users/profile/` - User profile & dashboard
- `PUT /api/v1/users/profile/` - Update profile
- `GET /api/v1/users/stats/` - User contribution statistics
- `GET /api/v1/users/activities/` - User activity history
- `GET /api/v1/users/onboarding/` - Get onboarding status and steps
- `POST /api/v1/users/onboarding/` - Update onboarding progress

#### Notifications APIs
- `GET /api/v1/users/notifications/` - List user notifications
- `POST /api/v1/users/notifications/{id}/mark_read/` - Mark notification as read
- `POST /api/v1/users/notifications/mark_all_read/` - Mark all notifications as read
- `POST /api/v1/users/notifications/` - Create notification
- `PUT /api/v1/users/notifications/{id}/` - Update notification
- `DELETE /api/v1/users/notifications/{id}/` - Delete notification

#### Projects APIs
- `GET /api/v1/users/projects/` - List active projects
- `POST /api/v1/users/projects/` - Create new project
- `GET /api/v1/users/projects/{id}/` - Get project details
- `PUT /api/v1/users/projects/{id}/` - Update project
- `DELETE /api/v1/users/projects/{id}/` - Delete project
- `POST /api/v1/users/projects/{id}/join/` - Join a project
- `POST /api/v1/users/projects/{id}/leave/` - Leave a project

#### Rewards APIs
- `GET /api/v1/users/rewards/` - List user rewards and achievements
- `GET /api/v1/users/rewards/{id}/` - Get specific reward details

#### Dashboard APIs
- `GET /api/v1/dashboard/` - Dashboard overview with personalized data

#### Search APIs
- `GET /api/v1/search/?q={query}` - Global search across all content
- `GET /api/v1/search/suggestions/` - Get search suggestions and trending topics

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

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.