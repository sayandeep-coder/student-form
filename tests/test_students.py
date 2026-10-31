"""Automated tests for Student Details Collection API."""

from datetime import date, timedelta
from unittest.mock import MagicMock
import uuid

from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.students import get_student_service
from app.main import app
from app.services.student_service import StudentService


VALID_STUDENT_PAYLOAD = {
    "full_name": "Rahul Sharma",
    "date_of_birth": "2005-06-15",
    "gender": "Male",
    "phone_number": "+919876543210",
    "email": "Rahul.Sharma@Example.com",
    "current_address": "Kolkata, West Bengal, India",
}


def test_health_check(client: TestClient):
    """Test health check endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_name" in data
    assert "database" in data


def test_create_student_success(client: TestClient):
    """Test successful student creation with all fields."""
    response = client.post("/api/v1/students", json=VALID_STUDENT_PAYLOAD)
    assert response.status_code == 201
    data = response.json()

    assert "id" in data
    assert data["full_name"] == "Rahul Sharma"
    assert data["date_of_birth"] == "2005-06-15"
    assert data["gender"] == "Male"
    assert data["phone_number"] == "+919876543210"
    # Email normalized to lowercase
    assert data["email"] == "rahul.sharma@example.com"
    assert data["current_address"] == "Kolkata, West Bengal, India"
    assert "created_at" in data
    assert "updated_at" in data


def test_create_student_optional_fields_omitted(client: TestClient):
    """Test student creation when optional fields (dob, gender) are omitted."""
    payload = {
        "full_name": "Priya Patel",
        "phone_number": "+91-9876543211",
        "email": "priya.patel@example.com",
        "current_address": "Ahmedabad, Gujarat, India",
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["date_of_birth"] is None
    assert data["gender"] is None
    assert data["full_name"] == "Priya Patel"


def test_create_student_missing_required_fields(client: TestClient):
    """Test validation failure when required fields are missing."""
    incomplete_payload = {
        "full_name": "Rahul Sharma",
        # missing phone_number, email, current_address
    }
    response = client.post("/api/v1/students", json=incomplete_payload)
    assert response.status_code == 422
    errors = response.json().get("detail", [])
    missing_fields = {e["loc"][-1] for e in errors}
    assert "phone_number" in missing_fields
    assert "email" in missing_fields
    assert "current_address" in missing_fields


def test_create_student_blank_full_name_and_address(client: TestClient):
    """Test validation failure when full_name or address is blank / whitespace."""
    payload = {
        **VALID_STUDENT_PAYLOAD,
        "full_name": "   ",
        "current_address": "   ",
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 422
    errors = str(response.json())
    assert "Full name cannot be blank" in errors
    assert "Current address cannot be blank" in errors


def test_create_student_invalid_email(client: TestClient):
    """Test validation failure with malformed email."""
    payload = {
        **VALID_STUDENT_PAYLOAD,
        "email": "not-an-email",
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 422


def test_create_student_invalid_phone_number(client: TestClient):
    """Test validation failure with malformed or too short phone numbers."""
    # Letters in phone
    payload1 = {**VALID_STUDENT_PAYLOAD, "phone_number": "123-abc-7890"}
    res1 = client.post("/api/v1/students", json=payload1)
    assert res1.status_code == 422

    # Too short (< 7 digits)
    payload2 = {**VALID_STUDENT_PAYLOAD, "phone_number": "12345"}
    res2 = client.post("/api/v1/students", json=payload2)
    assert res2.status_code == 422


def test_create_student_future_date_of_birth(client: TestClient):
    """Test validation failure when date of birth is in the future."""
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    payload = {
        **VALID_STUDENT_PAYLOAD,
        "date_of_birth": tomorrow,
    }
    response = client.post("/api/v1/students", json=payload)
    assert response.status_code == 422
    assert "Date of birth cannot be in the future" in str(response.json())


def test_get_student_existing(client: TestClient):
    """Test retrieving an existing student by UUID."""
    create_res = client.post("/api/v1/students", json=VALID_STUDENT_PAYLOAD)
    student_id = create_res.json()["id"]

    get_res = client.get(f"/api/v1/students/{student_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == student_id
    assert get_res.json()["email"] == "rahul.sharma@example.com"


def test_get_student_nonexistent(client: TestClient):
    """Test retrieving a nonexistent student UUID returns 404."""
    nonexistent_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/students/{nonexistent_id}")
    assert response.status_code == 404
    assert response.json()["detail"] == "Student not found."


def test_get_student_invalid_uuid(client: TestClient):
    """Test requesting with a non-UUID parameter returns 422."""
    response = client.get("/api/v1/students/not-a-valid-uuid")
    assert response.status_code == 422


def test_update_student_selected_fields(client: TestClient):
    """Test partial update of selected student fields."""
    create_res = client.post("/api/v1/students", json=VALID_STUDENT_PAYLOAD)
    student_id = create_res.json()["id"]

    update_payload = {
        "full_name": "Rahul S. Sharma",
        "current_address": "Mumbai, Maharashtra, India",
    }
    patch_res = client.patch(f"/api/v1/students/{student_id}", json=update_payload)
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["full_name"] == "Rahul S. Sharma"
    assert data["current_address"] == "Mumbai, Maharashtra, India"
    # Unchanged fields remain
    assert data["phone_number"] == "+919876543210"


def test_update_student_reject_empty_patch(client: TestClient):
    """Test that an empty update request is rejected with 400 Bad Request."""
    create_res = client.post("/api/v1/students", json=VALID_STUDENT_PAYLOAD)
    student_id = create_res.json()["id"]

    empty_patch = {}
    patch_res = client.patch(f"/api/v1/students/{student_id}", json=empty_patch)
    assert patch_res.status_code == 400
    assert "At least one field must be provided" in patch_res.json()["detail"]


def test_update_student_nonexistent(client: TestClient):
    """Test updating a nonexistent student returns 404."""
    nonexistent_id = str(uuid.uuid4())
    patch_res = client.patch(
        f"/api/v1/students/{nonexistent_id}",
        json={"full_name": "Nonexistent Person"},
    )
    assert patch_res.status_code == 404


def test_update_student_invalid_email(client: TestClient):
    """Test updating with an invalid email returns 422."""
    create_res = client.post("/api/v1/students", json=VALID_STUDENT_PAYLOAD)
    student_id = create_res.json()["id"]

    patch_res = client.patch(
        f"/api/v1/students/{student_id}", json={"email": "invalid-email"}
    )
    assert patch_res.status_code == 422


def test_delete_student_success(client: TestClient):
    """Test deleting an existing student returns 204 No Content."""
    create_res = client.post("/api/v1/students", json=VALID_STUDENT_PAYLOAD)
    student_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/students/{student_id}")
    assert del_res.status_code == 204

    # Verify student is now 404
    get_res = client.get(f"/api/v1/students/{student_id}")
    assert get_res.status_code == 404


def test_delete_student_nonexistent(client: TestClient):
    """Test deleting a nonexistent student returns 404."""
    nonexistent_id = str(uuid.uuid4())
    del_res = client.delete(f"/api/v1/students/{nonexistent_id}")
    assert del_res.status_code == 404


from app.repositories.student_repository import StudentRepository


def test_database_integrity_error_handling(client: TestClient):
    """Test that database integrity errors are handled cleanly and return 400."""
    mock_repo = MagicMock(spec=StudentRepository)
    mock_repo.create.side_effect = IntegrityError(
        statement="INSERT INTO students ...",
        params={},
        orig=Exception("mocked unique or check constraint violation"),
    )
    mock_service = StudentService(repository=mock_repo)

    app.dependency_overrides[get_student_service] = lambda: mock_service

    try:
        response = client.post("/api/v1/students", json=VALID_STUDENT_PAYLOAD)
        assert response.status_code == 400
        assert "integrity" in response.json()["detail"].lower()
        # Internal credentials or stack traces must never be leaked
        assert "password" not in response.text.lower()
        assert "traceback" not in response.text.lower()
    finally:
        app.dependency_overrides.pop(get_student_service, None)

