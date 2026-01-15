"""Initial database schema

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-15

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('supabase_user_id', postgresql.UUID(as_uuid=True), unique=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_users_supabase_user_id', 'users', ['supabase_user_id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Create videos table
    op.create_table(
        'videos',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('original_filename', sa.String(255), nullable=True),
        sa.Column('storage_path', sa.String(500), nullable=False),
        sa.Column('thumbnail_url', sa.String(500), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('fps', sa.Float(), nullable=True),
        sa.Column('codec', sa.String(50), nullable=True),
        sa.Column('bitrate', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), default='uploaded', nullable=False),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('metadata', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('tags', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_videos_user_id', 'videos', ['user_id'])
    op.create_index('ix_videos_status', 'videos', ['status'])

    # Create patterns table
    op.create_table(
        'patterns',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('score', sa.Float(), default=0.0, nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_patterns_video_id', 'patterns', ['video_id'])
    op.create_index('ix_patterns_type', 'patterns', ['type'])
    op.create_index('ix_patterns_score', 'patterns', ['score'])

    # Create strategies table
    op.create_table(
        'strategies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('video_ids', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('platforms', postgresql.JSONB(), nullable=False, server_default='[]'),
        sa.Column('goals', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('niche', sa.String(100), nullable=True),
        sa.Column('strategy_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('version', sa.Integer(), default=1, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_strategies_user_id', 'strategies', ['user_id'])

    # Create scripts table
    op.create_table(
        'scripts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('concept', sa.String(500), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('target_duration', sa.Integer(), nullable=False),
        sa.Column('pattern_ids', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('script_data', postgresql.JSONB(), nullable=False, server_default='{}'),
        sa.Column('actual_duration', sa.Float(), nullable=True),
        sa.Column('version', sa.Integer(), default=1, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_scripts_user_id', 'scripts', ['user_id'])

    # Create social_accounts table
    op.create_table(
        'social_accounts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('platform_user_id', sa.String(255), nullable=False),
        sa.Column('username', sa.String(255), nullable=True),
        sa.Column('profile_url', sa.String(500), nullable=True),
        sa.Column('access_token_encrypted', sa.String(1000), nullable=False),
        sa.Column('refresh_token_encrypted', sa.String(1000), nullable=True),
        sa.Column('token_expires_at', sa.DateTime(), nullable=True),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_social_accounts_user_id', 'social_accounts', ['user_id'])
    op.create_index('ix_social_accounts_platform', 'social_accounts', ['platform'])

    # Create posts table
    op.create_table(
        'posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('videos.id', ondelete='CASCADE'), nullable=False),
        sa.Column('social_account_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('social_accounts.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('platform_post_id', sa.String(255), nullable=True),
        sa.Column('caption', sa.String(2200), nullable=True),
        sa.Column('hashtags', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('status', sa.String(50), default='scheduled', nullable=False),
        sa.Column('error_message', sa.String(500), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('task_id', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_posts_video_id', 'posts', ['video_id'])
    op.create_index('ix_posts_social_account_id', 'posts', ['social_account_id'])
    op.create_index('ix_posts_platform', 'posts', ['platform'])
    op.create_index('ix_posts_status', 'posts', ['status'])
    op.create_index('ix_posts_scheduled_at', 'posts', ['scheduled_at'])

    # Create analytics table
    op.create_table(
        'analytics',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('posts.id', ondelete='CASCADE'), unique=True, nullable=False),
        sa.Column('views', sa.Integer(), default=0, nullable=False),
        sa.Column('likes', sa.Integer(), default=0, nullable=False),
        sa.Column('comments', sa.Integer(), default=0, nullable=False),
        sa.Column('shares', sa.Integer(), default=0, nullable=False),
        sa.Column('saves', sa.Integer(), default=0, nullable=False),
        sa.Column('engagement_rate', sa.Float(), default=0.0, nullable=False),
        sa.Column('platform_metrics', postgresql.JSONB(), nullable=True, server_default='{}'),
        sa.Column('metrics_history', postgresql.JSONB(), nullable=True, server_default='[]'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index('ix_analytics_post_id', 'analytics', ['post_id'])


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('analytics')
    op.drop_table('posts')
    op.drop_table('social_accounts')
    op.drop_table('scripts')
    op.drop_table('strategies')
    op.drop_table('patterns')
    op.drop_table('videos')
    op.drop_table('users')
