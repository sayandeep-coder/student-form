# Student Details Collection API

A production-ready, modular REST API backend built with **Python 3.12+**, **FastAPI**, **Pydantic v2**, **SQLAlchemy 2.x**, **Psycopg 3**, and **Alembic**.

---

## Architecture and Overview

The application follows clean architecture principles with clear separation of concerns:

```text
student-form/
├── app/
│   ├── main.py                     # FastAPI application setup, CORS, and health endpoint
│   ├── core/
│   │   └── config.py               # Pydantic Settings & environment variable validation
│   ├── db/
│   │   ├── base.py                 # SQLAlchemy DeclarativeBase
│   │   └── session.py              # Managed database engine and session factory
│   ├── models/
│   │   └── student.py              # SQLAlchemy ORM Student model
│   ├── schemas/
│   │   └── student.py              # Pydantic v2 request/response schemas with field validation
│   ├── repositories/
│   │   └── student_repository.py   # Raw database queries and entity operations
│   ├── services/
│   │   └── student_service.py      # Business logic and transaction boundary management
│   └── api/
│       └── v1/
│           └── students.py         # Versioned REST API endpoints
├── migrations/
│   ├── env.py                      # Alembic migration runner connected to app configuration
│   ├── script.py.mako              # Revision file template
│   └── versions/
│       └── 001_create_students_table.py  # Initial migration for students table
├── tests/
│   ├── conftest.py                 # Pytest fixtures and isolated testing setup
│   └── test_students.py            # Automated tests covering all operations and validation
├── alembic.ini                     # Alembic configuration
├── .env                            # Local configuration (contains actual database credentials; git-ignored)
├── .env.example                    # Environment template without secrets
├── .gitignore                      # Git ignore file
├── requirements.txt                # Pinned production and test dependencies
└── README.md                       # Complete documentation and setup guide
```

---

## Prerequisites

- **Python 3.12+** (tested on Python 3.13)
- **PostgreSQL 14+** (running locally, via Docker, or on a remote cloud host such as Supabase/Neon/RDS)

---

## 1. Setup Virtual Environment and Dependencies

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 2. Environment Configuration

1. Copy `.env.example` to `.env` if not already created:

```bash
cp .env.example .env
```

2. Open `.env` and replace the placeholder `DATABASE_URL` with your actual PostgreSQL connection string:

```dotenv
APP_NAME=Student Details API
APP_ENV=development
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/students_db
API_V1_PREFIX=/api/v1
```

> **Note**: The driver must be `postgresql+psycopg://` (SQLAlchemy 2.x with Psycopg 3). The application will fail with a clear configuration error if the URL is missing or still contains the placeholder `USERNAME:PASSWORD@HOST`.

---

## 3. Database Migrations with Alembic

Ensure your PostgreSQL database exists and is reachable before applying migrations.

### Apply Migrations to Head

```bash
alembic upgrade head
```

### Check Current Migration Revision

```bash
alembic current
```

Expected output:
```text
001_create_students_table (head)
```

### Verify Schema Alignment

Verify that your ORM models match the database schema with:

```bash
alembic check
```

Expected output:
```text
No new upgrade operations detected.
```

### Future Migrations Workflow

When you modify SQLAlchemy models in `app/models/`:

```bash
# 1. Generate a new revision
alembic revision --autogenerate -m "describe_schema_change"

# 2. Inspect the generated file under migrations/versions/

# 3. Apply the migration
alembic upgrade head

# 4. Roll back one revision if needed
alembic downgrade -1

# 5. View revision history
alembic history
```

---

## 4. Running the Application

Start the development server with hot reload:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- **Interactive Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc Documentation**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **Health Check Endpoint**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 5. API Endpoints

All resource routes are prefixed under `/api/v1`.

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/health` | Service and database connectivity check | `200 OK` |
| `POST` | `/api/v1/students` | Create a new student record | `201 Created` |
| `GET` | `/api/v1/students/{student_id}` | Retrieve a student record by UUID | `200 OK` / `404 Not Found` |
| `PATCH` | `/api/v1/students/{student_id}` | Partially update a student record | `200 OK` / `400 Bad Request` / `404 Not Found` |
| `DELETE` | `/api/v1/students/{student_id}` | Delete a student record | `204 No Content` / `404 Not Found` |

### Field Constraints & Validation Rules

- `full_name`: Required string, max length 150. Surrounding whitespace is trimmed; empty strings are rejected.
- `date_of_birth`: Optional date (format `YYYY-MM-DD`). Dates in the future are rejected.
- `gender`: Optional string, max length 30. Empty strings are converted to `None`.
- `phone_number`: Required string, max length 20. Must contain between 7 and 15 digits; preserves international dialing prefix (`+`), spaces, hyphens, and parentheses.
- `email`: Required valid email address. Automatically normalized to lowercase and trimmed.
- `current_address`: Required text, max length 1000. Surrounding whitespace is trimmed; empty strings are rejected.
- `StudentUpdate`: Allows partial updates. Rejects an empty update payload (`{}`) with HTTP 400 Bad Request. Disallows setting required fields to `null`.

---

## 6. Example Requests and Responses

### Create Student

**Request**:
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/students" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Rahul Sharma",
    "date_of_birth": "2005-06-15",
    "gender": "Male",
    "phone_number": "+919876543210",
    "email": "Rahul@Example.com",
    "current_address": "Kolkata, West Bengal, India"
  }'
```

**Response (`201 Created`)**:
```json
{
  "id": "e6f1a8c3-4d2b-42b6-9bf6-b51e5cfcb7c4",
  "full_name": "Rahul Sharma",
  "date_of_birth": "2005-06-15",
  "gender": "Male",
  "phone_number": "+919876543210",
  "email": "rahul@example.com",
  "current_address": "Kolkata, West Bengal, India",
  "created_at": "2026-10-31T12:00:00Z",
  "updated_at": "2026-10-31T12:00:00Z"
}
```

### Retrieve Student

```bash
curl -X GET "http://127.0.0.1:8000/api/v1/students/e6f1a8c3-4d2b-42b6-9bf6-b51e5cfcb7c4"
```

### Update Student (Partial)

```bash
curl -X PATCH "http://127.0.0.1:8000/api/v1/students/e6f1a8c3-4d2b-42b6-9bf6-b51e5cfcb7c4" \
  -H "Content-Type: application/json" \
  -d '{
    "current_address": "Mumbai, Maharashtra, India"
  }'
```

### Delete Student

```bash
curl -X DELETE "http://127.0.0.1:8000/api/v1/students/e6f1a8c3-4d2b-42b6-9bf6-b51e5cfcb7c4"
```

---

## 7. Automated Testing

Run the automated test suite with pytest:

```bash
pytest -v
```

By default, tests run against an isolated in-memory SQLite database (`TEST_DATABASE_URL=sqlite:///:memory:`).

To run the test suite against an isolated PostgreSQL test database:

```bash
TEST_DATABASE_URL="postgresql+psycopg://username:password@localhost:5432/test_students_db" pytest -v
```

---

## 8. Production Deployment Considerations

1. **Disable Interactive API Docs**:
   Set `APP_ENV=production` in your environment or `.env`. This automatically disables `/docs`, `/redoc`, and `/openapi.json`.

2. **CORS Restrictions**:
   Set `CORS_ORIGINS` to explicit domain names, e.g.:
   ```dotenv
   CORS_ORIGINS=https://portal.example.com,https://admin.example.com
   ```

3. **Production ASGI Server**:
   Run with multiple workers behind a reverse proxy (e.g. Nginx or Traefik):
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
   ```

4. **Network Controls**:
   Because authentication is omitted by design, endpoints should be placed behind appropriate network security controls (such as an API Gateway, VPN, or private subnet) when handling personal data.