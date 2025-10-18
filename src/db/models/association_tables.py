"""Промежуточные таблицы для связи Many-to-Many"""

from sqlalchemy import Table, Column, ForeignKey
from src.db.models.base import Base

# Репетитор-Предмет
teacher_subjects = Table(
    "teacher_subjects",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
    Column("subject_id", ForeignKey("subjects.id"), primary_key=True),
)

# Скрытые заявки
hidden_applications = Table(
    "hidden_applications",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("application_id", ForeignKey("applications.id"), primary_key=True),
)

# Скрытые репетиторы
hidden_teachers = Table(
    "hidden_teachers",
    Base.metadata,
    Column("student_id", ForeignKey("students.id"), primary_key=True),
    Column("teacher_id", ForeignKey("teachers.id"), primary_key=True),
)
