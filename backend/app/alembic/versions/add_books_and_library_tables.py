"""add books and library tables

Revision ID: a1b2c3d4e5f6
Revises: 1a31ce608336
Create Date: 2025-10-29 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '1a31ce608336'
branch_labels = None
depends_on = None


def upgrade():
    # Create book table
    op.create_table('book',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column('author', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('isbn', sqlmodel.sql.sqltypes.AutoString(length=13), nullable=True),
        sa.Column('publisher', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column('published_date', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('categories', sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column('thumbnail_url', sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column('google_books_id', sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column('average_rating', sa.Float(), nullable=True),
        sa.Column('ratings_count', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_book_isbn'), 'book', ['isbn'], unique=False)
    op.create_index(op.f('ix_book_google_books_id'), 'book', ['google_books_id'], unique=False)

    # Create userlibrary table
    op.create_table('userlibrary',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('book_id', sa.Uuid(), nullable=False),
        sa.Column('added_date', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('notes', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(['book_id'], ['book.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('userlibrary')
    op.drop_index(op.f('ix_book_google_books_id'), table_name='book')
    op.drop_index(op.f('ix_book_isbn'), table_name='book')
    op.drop_table('book')
