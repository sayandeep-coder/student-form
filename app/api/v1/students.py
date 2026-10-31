"""API router for student resources."""

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


def get_student_service() -> StudentService:
    """Dependency provider for StudentService."""
    return StudentService()


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Accepts student details, validates fields, persists record, and returns created entity with UUID.",
)
def create_student(
    student_in: StudentCreate,
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    """Create a new student record."""
    return service.create_student(db=db, student_in=student_in)


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a student by ID",
    description="Retrieve a single student record by their unique UUID.",
)
def get_student(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    """Retrieve a student by ID."""
    return service.get_student(db=db, student_id=student_id)


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update a student",
    description="Partially update an existing student record with supplied fields.",
)
def update_student(
    student_id: uuid.UUID,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
) -> StudentResponse:
    """Partially update a student by ID."""
    return service.update_student(
        db=db, student_id=student_id, student_update=student_update
    )


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a student",
    description="Delete a student record by their unique UUID.",
)
def delete_student(
    student_id: uuid.UUID,
    db: Session = Depends(get_db),
    service: StudentService = Depends(get_student_service),
) -> None:
    """Delete a student by ID."""
    service.delete_student(db=db, student_id=student_id)
