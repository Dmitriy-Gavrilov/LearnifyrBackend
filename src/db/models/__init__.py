"""Инициализация моделей"""

from .base import Base

from .application import Application
from .matches import Match
from .review import Review
from .student import Student
from .subject import Subject
from .teacher import Teacher
from .token import Token

from .association_tables import (
    hidden_applications,
    hidden_teachers
)

__all__ = [
    "Base",
    "Application",
    "Match",
    "Review",
    "Student",
    "Subject",
    "Teacher",
    "Token",
    "hidden_applications",
    "hidden_teachers",
]
