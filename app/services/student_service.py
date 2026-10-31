"""Business logic and transaction orchestration for student records."""

import logging
from typing import Optional
import uuid

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.student_repository import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate

logger = logging.getLogger(__name__)


class StudentService:
    """Service layer managing business operations and database transactions for students."""

    def __init__(self, repository: Optional[StudentRepository] = None):
        self.repository = repository or StudentRepository()

    def create_student(self, db: Session, student_in: StudentCreate) -> Student:
        """Create a new student record and commit the transaction."""
        try:
            student = self.repository.create(db, student_in)
            db.commit()
            db.refresh(student)
            logger.info("Successfully created student with id=%s", student.id)
            return student
        except IntegrityError as exc:
            db.rollback()
            logger.warning("Integrity error occurred while creating student: %s", exc.orig if hasattr(exc, "orig") else exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity constraint violation.",
            )
        except SQLAlchemyError as exc:
            db.rollback()
            logger.error("Database error creating student: %s", type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal database error occurred.",
            )

    def get_student(self, db: Session, student_id: uuid.UUID) -> Student:
        """Retrieve a student by UUID or raise 404."""
        student = self.repository.get_by_id(db, student_id)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found.",
            )
        return student

    def update_student(
        self, db: Session, student_id: uuid.UUID, student_update: StudentUpdate
    ) -> Student:
        """Apply partial updates to an existing student."""
        # Reject empty update request
        update_data = student_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one field must be provided for update.",
            )

        student = self.get_student(db, student_id)

        try:
            updated_student = self.repository.update(db, student, update_data)
            db.commit()
            db.refresh(updated_student)
            logger.info("Successfully updated student id=%s", student_id)
            return updated_student
        except IntegrityError as exc:
            db.rollback()
            logger.warning("Integrity error updating student %s: %s", student_id, exc.orig if hasattr(exc, "orig") else exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Database integrity constraint violation.",
            )
        except SQLAlchemyError as exc:
            db.rollback()
            logger.error("Database error updating student %s: %s", student_id, type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal database error occurred.",
            )

    def delete_student(self, db: Session, student_id: uuid.UUID) -> None:
        """Delete an existing student or raise 404."""
        student = self.get_student(db, student_id)
        try:
            self.repository.delete(db, student)
            db.commit()
            logger.info("Successfully deleted student id=%s", student_id)
        except SQLAlchemyError as exc:
            db.rollback()
            logger.error("Database error deleting student %s: %s", student_id, type(exc).__name__)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An internal database error occurred.",
            )
