"""add fighter ufc record

Revision ID: 7c2e9a41d3b8
Revises: 515d75cfc2fb
Create Date: 2026-11-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c2e9a41d3b8'
down_revision: Union[str, Sequence[str], None] = '515d75cfc2fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Existing rows are left NULL here; seed_fighters backfills them on its next run.
    op.add_column('fighters', sa.Column('ufc_wins', sa.Integer(), nullable=True))
    op.add_column('fighters', sa.Column('ufc_losses', sa.Integer(), nullable=True))
    op.add_column('fighters', sa.Column('ufc_draws', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('fighters', 'ufc_draws')
    op.drop_column('fighters', 'ufc_losses')
    op.drop_column('fighters', 'ufc_wins')
