"""Добавление предметов в таблицу subjects"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20251103_add_subjects"
down_revision = "53750c264573"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Вставка предметов в таблицу subjects"""
    subjects = [
        {"name": "Математика"},
        {"name": "Информатика"},
        {"name": "Физика"},
        {"name": "Химия"},
        {"name": "Биология"},
        {"name": "История"},
        {"name": "География"},
        {"name": "Литература"},
        {"name": "Музыка"},
        {"name": "Обществознание"},
        {"name": "Экономика"},
        {"name": "Английский язык"},
        {"name": "Немецкий язык"},
        {"name": "Испанский язык"},
        {"name": "Китайский язык"},
        {"name": "Другие иностраные языки"},
        {"name": "Python"},
        {"name": "C/C++"},
        {"name": "Java"},
        {"name": "JavaScript/TypeScript"},
        {"name": "HTML/CSS"},
        {"name": "SQL"},
        {"name": "Дизайн"},
        {"name": "Маркетинг"},
    ]
    op.bulk_insert(
        sa.table(
            "subjects",
            sa.column("name", sa.String)
        ),
        subjects
    )


def downgrade() -> None:
    """Удаление предметов"""
