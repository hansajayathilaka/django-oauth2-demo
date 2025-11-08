# Django OAuth2 REST API

A complete Django application implementing OAuth2 authentication for REST APIs with a user-friendly admin interface for managing client credentials.

## Features

- **OAuth2 Authentication**: Full OAuth2 provider implementation using django-oauth-toolkit
- **Grant Types**: Client Credentials and Refresh Token support
- **Scopes & Permissions**: Granular access control with custom scopes (read, write, admin)
- **REST API**: Protected API endpoints using Django REST Framework
- **Admin Interface**: Easy-to-use Django Admin for generating and managing client IDs and secrets
- **PostgreSQL**: Production-ready database configuration

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 18+

### Installation

1. **Install dependencies**:
```bash
pip install --break-system-packages -r requirements.txt
```

2. **Configure environment variables**:
The `.env` file is already configured with default values:
```
DEBUG=True
SECRET_KEY=django-insecure-change-this-in-production-123456789
DB_NAME=oauth2_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
```

3. **Start PostgreSQL** (if not already running):
```bash
sudo service postgresql start
```

4. **Create the database**:
```bash
psql -U postgres -c "CREATE DATABASE oauth2_db;"
```

5. **Run migrations**:
```bash
python3 manage.py migrate
```

6. **Create a superuser**:
```bash
python3 manage.py createsuperuser
```
Or use the default superuser already created:
- Username: `admin`
- Password: `admin`

7. **Start the development server**:
```bash
python3 manage.py runserver
```

The server will be available at `http://localhost:8000`

## Creating OAuth2 Clients

### Using Django Admin

1. Navigate to `http://localhost:8000/admin/`
2. Login with your superuser credentials (admin/admin)
3. Click on **"Applications"** under the **OAuth2 Provider** section
4. Click **"Add Application"** button
5. Fill in the form:
   - **Name**: A descriptive name for your application
   - **User**: Select the user who owns this application
   - **Client type**: Choose "Confidential" for server-side apps
   - **Authorization grant type**: Choose "Client credentials" or "Authorization code"
   - **Redirect uris**: (Optional, not needed for client credentials)

6. Click **"Save"**
7. The admin will display your **Client ID** and **Client Secret** - save these securely!

## API Endpoints

### Public Endpoints

#### Hello World (No Authentication Required)
```bash
GET http://localhost:8000/api/hello/

# Response:
{
    "message": "Hello, World!",
    "description": "This is a public endpoint that doesn't require authentication."
}
```

### Protected Endpoints (Require OAuth2 Token)

#### Get Access Token

First, obtain an access token using your client credentials:

```bash
curl -X POST http://localhost:8000/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=read write"

# Response:
{
    "access_token": "your-access-token-here",
    "expires_in": 3600,
    "token_type": "Bearer",
    "scope": "read write"
}
```

#### Protected View
```bash
curl -X GET http://localhost:8000/api/protected/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
    "message": "You have successfully authenticated!",
    "user": "admin",
    "client_id": "your-client-id",
    "scopes": "read write"
}
```

#### Scoped Read Endpoint (Requires 'read' scope)
```bash
curl -X GET http://localhost:8000/api/scoped/read/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Response:
{
    "message": "You have read access!",
    "data": [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
        {"id": 3, "name": "Item 3"}
    ]
}
```

#### Scoped Write Endpoint (Requires 'write' scope)
```bash
curl -X POST http://localhost:8000/api/scoped/write/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Item"}'

# Response:
{
    "message": "You have write access!",
    "created": true,
    "data": {"name": "New Item"}
}
```

### Refresh Token Flow

If you have a refresh token, you can get a new access token:

```bash
curl -X POST http://localhost:8000/o/token/ \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

### Revoke Token

```bash
curl -X POST http://localhost:8000/o/revoke_token/ \
  -d "token=YOUR_ACCESS_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET"
```

## Available Scopes

The following scopes are configured:

- **read**: Read-only access to resources
- **write**: Write access to resources
- **admin**: Administrative access

## Project Structure

```
oauth2-demo/
├── manage.py
├── requirements.txt
├── .env
├── README.md
├── oauth2_server/          # Main project directory
│   ├── settings.py         # Django settings with OAuth2 configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py
└── api/                   # API application
    ├── admin.py           # Customized admin for OAuth2 models
    ├── views.py           # API endpoints
    └── urls.py            # API URL routing
```

## Configuration

### OAuth2 Settings

Key OAuth2 configurations in `settings.py`:

```python
OAUTH2_PROVIDER = {
    "ALLOWED_GRANT_TYPES": [
        "client_credentials",
        "refresh_token",
    ],
    "SCOPES": {
        "read": "Read access",
        "write": "Write access",
        "admin": "Admin access",
    },
    "ACCESS_TOKEN_EXPIRE_SECONDS": 3600,  # 1 hour
    "REFRESH_TOKEN_EXPIRE_SECONDS": 86400,  # 24 hours
    "ROTATE_REFRESH_TOKEN": True,
}
```

### REST Framework Settings

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}
```

## Security Notes

1. **Change the SECRET_KEY** in production - use a strong, random value
2. **Use HTTPS** in production to protect tokens in transit
3. **Keep client secrets secure** - never commit them to version control
4. **Set CORS_ALLOW_ALL_ORIGINS to False** in production and configure specific allowed origins
5. **Set DEBUG to False** in production
6. **Use strong passwords** for database and admin accounts

## Testing with curl

Here's a complete example workflow:

```bash
# 1. Get an access token
TOKEN_RESPONSE=$(curl -X POST http://localhost:8000/o/token/ \
  -d "grant_type=client_credentials" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "scope=read write")

# 2. Extract the access token (requires jq)
ACCESS_TOKEN=$(echo $TOKEN_RESPONSE | jq -r '.access_token')

# 3. Use the token to access protected endpoints
curl -X GET http://localhost:8000/api/protected/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"

curl -X GET http://localhost:8000/api/scoped/read/ \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Troubleshooting

### Database connection errors
- Ensure PostgreSQL is running: `sudo service postgresql status`
- Check database credentials in `.env`
- Verify the database exists: `psql -U postgres -l`

### Token validation errors
- Ensure you're sending the token in the Authorization header: `Authorization: Bearer YOUR_TOKEN`
- Check that the token hasn't expired
- Verify the client has the required scopes

### Admin access issues
- Make sure you've created a superuser
- Use credentials: admin/admin (or your custom superuser)

## License

This project is provided as-is for educational and development purposes.
