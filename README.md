# Videoflix Backend

REST API backend for the Videoflix platform, built with Django and Django REST Framework.

## Tech Stack

- **Django 5** + **Django REST Framework**
- **PostgreSQL** — primary database
- **Redis** — caching layer
- **Django RQ** — background processing (FFMPEG conversion)
- **JWT via HTTP-Only Cookies** — authentication
- **Docker** — containerization

## Prerequisites

- Docker & Docker Compose

## Setup

**1. Clone the repository:**

```bash
git clone https://github.com/MalteSchuette/Videoflix.git
cd Videoflix
```

**2. Create the `.env` file:**

```bash
cp .env.template .env
```

Adjust the following values in `.env` as needed:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL credentials |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP configuration |
| `FRONTEND_URL` | Frontend URL (used in email links) |
| `CORS_ALLOWED_ORIGINS` | Allowed frontend origins |
| `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | Admin account credentials |

> **Note:** The template already contains working default values for the database and Redis. You only need to adjust them if you want custom credentials.

**3. Start the containers:**

```bash
docker compose up --build
```

The API is then available at `http://localhost:8000`.

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register/` | Create a new account |
| GET | `/api/activate/<uidb64>/<token>/` | Activate account via email link |
| POST | `/api/login/` | Login — sets JWT cookies |
| POST | `/api/logout/` | Logout — clears JWT cookies |
| POST | `/api/token/refresh/` | Refresh access token |
| POST | `/api/password_reset/` | Request password reset email |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Set new password |

### Video

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/video/` | List all videos |
| GET | `/api/video/<id>/<resolution>/index.m3u8` | HLS playlist (480p / 720p / 1080p) |
| GET | `/api/video/<id>/<resolution>/<segment>/` | HLS video segment |

All video endpoints require a valid JWT cookie.

## Video Processing

Videos are uploaded via the Django admin interface. After upload, an RQ background job automatically starts and uses FFMPEG to generate three HLS versions (480p, 720p, 1080p) and a thumbnail.
