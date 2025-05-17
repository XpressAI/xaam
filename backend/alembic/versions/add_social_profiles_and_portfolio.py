"""add social profiles and portfolio

Revision ID: add_social_profiles_and_portfolio
Revises: initial_migration
Create Date: 2025-05-16 17:26:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_social_profiles_and_portfolio'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Add social_profiles and portfolio_url columns to agents table
    op.add_column('agents', sa.Column('social_profiles', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('agents', sa.Column('portfolio_url', sa.String(), nullable=True))


def downgrade():
    # Drop social_profiles and portfolio_url columns from agents table
    op.drop_column('agents', 'portfolio_url')
    op.drop_column('agents', 'social_profiles')