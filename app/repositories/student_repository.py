"""Repository layer for student database access."""

from typing import Any, Dict, Optional
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student
from app.schemas.student import StudentCreate


class StudentRepository:
    """Encapsulates database operations for Student entities."""

    def get_by_id(self, db: Session, student_id: uuid.UUID) -> Optional[Student]:
        """Fetch a student by UUID primary key."""
        stmt = select(Student).where(Student.id == student_id)
        return db.execute(stmt).scalar_one_or_none()

    def create(self, db: Session, student_in: StudentCreate) -> Student:
        """Create a new student instance and add it to the session."""
        db_student = Student(
            full_name=student_in.full_name,
            date_of_birth=student_in.date_of_birth,
            gender=student_in.gender,
            phone_number=student_in.phone_number,
            email=student_in.email,
            current_address=student_in.current_address,
        )
        db.add(db_student)
        return db_student

    def update(
        self, db: Session, db_student: Student, update_data: Dict[str, Any]
    ) -> Student:
        """Apply partial update fields to a student instance."""
        for field, value in update_data.items():
            setattr(db_student, field, value)
        return db_student

    def delete(self, db: Session, db_student: Student) -> None:
        """Remove a student instance from the session."""
        db.delete(db_student)
