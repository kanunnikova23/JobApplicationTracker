"""Fresh start

Revision ID: 94f66eb0ae2b
Revises: 
Create Date: 2025-05-14 12:29:46.591813

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '94f66eb0ae2b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('job_applications',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company', sa.String(length=100), nullable=False),
    sa.Column('position', sa.String(length=100), nullable=False),
    sa.Column('location', sa.String(length=100), nullable=True),
    sa.Column('status', sa.Enum('APPLIED', 'INTERVIEWING', 'OFFERED', 'REJECTED', 'WITHDRAWN', name='application_status'), nullable=True),
    sa.Column('applied_date', sa.Date(), nullable=False),
    sa.Column('link', sa.String(length=2048), nullable=True),
    sa.Column('notes', sa.String(length=500), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_job_applications_id'), 'job_applications', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_job_applications_id'), table_name='job_applications')
    op.drop_table('job_applications')
    # ### end Alembic commands ###
