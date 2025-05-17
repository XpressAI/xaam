"""initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2025-05-12 18:33:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create enum types
    op.execute("CREATE TYPE agent_type AS ENUM ('WORKER', 'JUDGE')")
    op.execute("CREATE TYPE task_status AS ENUM ('CREATED', 'STAKED', 'IN_PROGRESS', 'SUBMITTED', 'JUDGED', 'COMPLETED')")
    op.execute("CREATE TYPE deliverable_status AS ENUM ('SUBMITTED', 'JUDGED', 'ACCEPTED', 'REJECTED')")
    op.execute("CREATE TYPE stake_status AS ENUM ('ACTIVE', 'RETURNED', 'FORFEITED')")
    
    # Create agents table
    op.create_table('agents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('agent_type', sa.Enum('WORKER', 'JUDGE', name='agent_type'), nullable=False),
        sa.Column('wallet_address', sa.String(), nullable=False),
        sa.Column('public_key', sa.String(), nullable=False),
        sa.Column('reputation_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('completed_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('successful_tasks', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('wallet_address')
    )
    
    # Create judges table
    op.create_table('judges',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('specialization', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create tasks table
    op.create_table('tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('nft_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('summary', sa.String(), nullable=False),
        sa.Column('encrypted_payload_url', sa.String(), nullable=False),
        sa.Column('encryption_key', sa.String(), nullable=True),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.Enum('CREATED', 'STAKED', 'IN_PROGRESS', 'SUBMITTED', 'JUDGED', 'COMPLETED', name='task_status'), nullable=False, server_default='CREATED'),
        sa.Column('deadline', sa.DateTime(), nullable=False),
        sa.Column('reward_amount', sa.Float(), nullable=False),
        sa.Column('reward_currency', sa.String(), nullable=False, server_default='USDC'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create task_judge_association table
    op.create_table('task_judge_association',
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('judge_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['judge_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('task_id', 'judge_id')
    )
    
    # Create deliverables table
    op.create_table('deliverables',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('encrypted_content_url', sa.String(), nullable=False),
        sa.Column('encryption_keys', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('submission_time', sa.DateTime(), nullable=False),
        sa.Column('scores', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('feedback', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.Enum('SUBMITTED', 'JUDGED', 'ACCEPTED', 'REJECTED', name='deliverable_status'), nullable=False, server_default='SUBMITTED'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create stakes table
    op.create_table('stakes',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'RETURNED', 'FORFEITED', name='stake_status'), nullable=False, server_default='ACTIVE'),
        sa.Column('staked_at', sa.DateTime(), nullable=False),
        sa.Column('released_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create wallets table
    op.create_table('wallets',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('address', sa.String(), nullable=False),
        sa.Column('agent_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('sol_balance', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('usdc_balance', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('nfts', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('address'),
        sa.UniqueConstraint('agent_id')
    )


def downgrade():
    # Drop tables
    op.drop_table('wallets')
    op.drop_table('stakes')
    op.drop_table('deliverables')
    op.drop_table('task_judge_association')
    op.drop_table('tasks')
    op.drop_table('judges')
    op.drop_table('agents')
    
    # Drop enum types
    op.execute("DROP TYPE stake_status")
    op.execute("DROP TYPE deliverable_status")
    op.execute("DROP TYPE task_status")
    op.execute("DROP TYPE agent_type")