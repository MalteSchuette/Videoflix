# Videoflix Backend

REST-API Backend für die Videoflix-Plattform. Gebaut mit Django und Django REST Framework.

## Tech Stack

- **Django 5** + **Django REST Framework**
- **PostgreSQL** — Hauptdatenbank
- **Redis** — Caching Layer
- **Django RQ** — Hintergrundverarbeitung (FFMPEG-Konvertierung)
- **JWT via HTTP-Only Cookies** — Authentifizierung
- **Docker** — Containerisierung

## Voraussetzungen

- Docker & Docker Compose

## Setup

**1. `.env` Datei anlegen:**

```bash
cp .env.template .env
```

Folgende Werte in der `.env` anpassen:

| Variable | Beschreibung |
|----------|-------------|
| `SECRET_KEY` | Django Secret Key |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL Zugangsdaten |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP-Konfiguration |
| `FRONTEND_URL` | URL des Frontends (für E-Mail-Links) |
| `CORS_ALLOWED_ORIGINS` | Erlaubte Frontend-Origins |
| `DJANGO_SUPERUSER_EMAIL`, `DJANGO_SUPERUSER_PASSWORD` | Admin-Account |

**2. Container starten:**

```bash
docker compose up --build
```

Die API ist danach erreichbar unter `http://localhost:8000`.

## API Endpoints

### Authentication

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| POST | `/api/register/` | Neuen Account anlegen |
| GET | `/api/activate/<uidb64>/<token>/` | Account per E-Mail aktivieren |
| POST | `/api/login/` | Login — setzt JWT-Cookies |
| POST | `/api/logout/` | Logout — löscht JWT-Cookies |
| POST | `/api/token/refresh/` | Access-Token erneuern |
| POST | `/api/password_reset/` | Passwort-Reset-E-Mail anfordern |
| POST | `/api/password_confirm/<uidb64>/<token>/` | Neues Passwort setzen |

### Video

| Method | Endpoint | Beschreibung |
|--------|----------|--------------|
| GET | `/api/video/` | Liste aller Videos |
| GET | `/api/video/<id>/<resolution>/index.m3u8` | HLS-Playlist (480p / 720p / 1080p) |
| GET | `/api/video/<id>/<resolution>/<segment>/` | HLS-Videosegment |

Alle Video-Endpoints erfordern einen gültigen JWT-Cookie.

## Video-Verarbeitung

Videos werden über das Django Admin-Interface hochgeladen. Nach dem Upload startet automatisch ein RQ-Hintergrundjob, der per FFMPEG drei HLS-Versionen (480p, 720p, 1080p) sowie ein Thumbnail erzeugt.
