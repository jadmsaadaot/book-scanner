"""fix added_date and add unique constraint

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2025-11-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'b2c3d4e5f6g7'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Add unique constraint on google_books_id in book table
    op.create_unique_constraint('uq_book_google_books_id', 'book', ['google_books_id'])

    # Add composite index on userlibrary (user_id, book_id) for faster lookups
    op.create_index('ix_userlibrary_user_book', 'userlibrary', ['user_id', 'book_id'], unique=False)

    # Change added_date from string to timestamp
    # First, add a new column with the correct type
    op.add_column('userlibrary', sa.Column('added_date_new', sa.DateTime(), nullable=True))

    # For existing rows, set added_date_new to current timestamp
    # (since the old added_date values are UUIDs and can't be converted to dates)
    op.execute("UPDATE userlibrary SET added_date_new = NOW()")

    # Drop the old column
    op.drop_column('userlibrary', 'added_date')

    # Rename the new column to added_date
    op.alter_column('userlibrary', 'added_date_new', new_column_name='added_date', nullable=False)


def downgrade():
    # Revert added_date to string type
    op.add_column('userlibrary', sa.Column('added_date_old', sa.String(), nullable=True))
    op.execute("UPDATE userlibrary SET added_date_old = added_date::text")
    op.drop_column('userlibrary', 'added_date')
    op.alter_column('userlibrary', 'added_date_old', new_column_name='added_date', nullable=False)

    # Drop composite index
    op.drop_index('ix_userlibrary_user_book', table_name='userlibrary')

    # Drop unique constraint
    op.drop_constraint('uq_book_google_books_id', 'book', type_='unique')
