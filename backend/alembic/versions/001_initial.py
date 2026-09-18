"""Initial migration - Create all tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-09-17 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create accessibility_preferences table
    op.create_table(
        'accessibility_preferences',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('font_scale', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('high_contrast', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dark_mode', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('reduce_motion', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('larger_buttons', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('auto_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('speech_rate', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('voice_navigation', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('simplified_interface', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )

    # Create sessions table
    op.create_table(
        'sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('context_data', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_sessions_user_id', 'sessions', ['user_id'])

    # Create interactions table
    op.create_table(
        'interactions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input_type', sa.Enum('image', 'document', 'form', 'text', 'voice', 'question', name='inputtype'), nullable=False),
        sa.Column('intent', sa.Enum('see_understand', 'read_explain', 'form_assist', 'visual_qa', 'simplify', 'summarize', 'communicate', 'chat', 'unknown', name='intenttype'), nullable=False, server_default='unknown'),
        sa.Column('question', sa.Text(), nullable=True),
        sa.Column('response', sa.Text(), nullable=True),
        sa.Column('structured_response', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('needs_clarification', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('clarification_question', sa.Text(), nullable=True),
        sa.Column('safety_note', sa.Text(), nullable=True),
        sa.Column('request_id', sa.String(length=64), nullable=True),
        sa.Column('processing_time_ms', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_interactions_session_id', 'interactions', ['session_id'])
    op.create_index('ix_interactions_created_at', 'interactions', ['created_at'])

    # Create input_metadata table
    op.create_table(
        'input_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('interaction_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input_type', sa.String(length=32), nullable=False),
        sa.Column('mime_type', sa.String(length=128), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('processing_status', sa.Enum('pending', 'processing', 'completed', 'failed', name='processingstatus'), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('file_reference', sa.String(length=256), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['interaction_id'], ['interactions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_input_metadata_interaction_id', 'input_metadata', ['interaction_id'])


def downgrade() -> None:
    op.drop_table('input_metadata')
    op.drop_table('interactions')
    op.drop_table('sessions')
    op.drop_table('accessibility_preferences')
    op.drop_table('users')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS inputtype')
    op.execute('DROP TYPE IF EXISTS intenttype')
    op.execute('DROP TYPE IF EXISTS processingstatus')