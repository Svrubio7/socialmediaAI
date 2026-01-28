"""Add video templates and template segments tables

Revision ID: 002
Revises: 001
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create video_templates table
    op.create_table(
        'video_templates',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_version', sa.String(50), nullable=False, server_default='gemini-2.0-flash'),
        sa.Column('interval_ms', sa.Integer(), nullable=False, server_default='200'),
        sa.Column('duration_seconds', sa.Float(), nullable=False),
        sa.Column('total_segments', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='processing'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('template_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        # Denormalized summary fields
        sa.Column('pacing', sa.String(20), nullable=True),
        sa.Column('total_cuts', sa.Integer(), nullable=True),
        sa.Column('average_shot_duration_ms', sa.Integer(), nullable=True),
        sa.Column('hook_duration_ms', sa.Integer(), nullable=True),
        sa.Column('music_coverage_percent', sa.Float(), nullable=True),
        sa.Column('speech_coverage_percent', sa.Float(), nullable=True),
        sa.Column('text_overlay_count', sa.Integer(), nullable=True),
        sa.Column('style_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for video_templates
    op.create_index('ix_video_templates_video_id', 'video_templates', ['video_id'])
    op.create_index('ix_video_templates_score', 'video_templates', ['score'])
    op.create_index('ix_video_templates_pacing', 'video_templates', ['pacing'])
    op.create_index('ix_video_templates_status', 'video_templates', ['status'])
    op.create_index('ix_video_templates_pacing_score', 'video_templates', ['pacing', 'score'])
    op.create_index('ix_video_templates_style_tags', 'video_templates', ['style_tags'], postgresql_using='gin')
    
    # Create template_segments table
    op.create_table(
        'template_segments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('template_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('video_id', postgresql.UUID(as_uuid=True), nullable=False),
        # Timing
        sa.Column('timestamp_ms', sa.Integer(), nullable=False),
        sa.Column('timestamp_end_ms', sa.Integer(), nullable=False),
        # Visual fields
        sa.Column('scene_type', sa.String(50), nullable=True),
        sa.Column('camera_motion', sa.String(50), nullable=True),
        sa.Column('has_text_overlay', sa.Boolean(), server_default='false'),
        sa.Column('text_overlay', sa.Text(), nullable=True),
        sa.Column('transition_in', sa.String(50), nullable=True),
        # Audio fields
        sa.Column('audio_type', sa.String(50), nullable=True),
        sa.Column('music_present', sa.Boolean(), server_default='false'),
        sa.Column('speech_present', sa.Boolean(), server_default='false'),
        # Key moment
        sa.Column('is_key_moment', sa.Boolean(), server_default='false'),
        sa.Column('key_moment_type', sa.String(50), nullable=True),
        # Description
        sa.Column('description', sa.Text(), nullable=True),
        # Full segment data
        sa.Column('segment_data', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        # Timestamps
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['template_id'], ['video_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['video_id'], ['videos.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for template_segments
    op.create_index('ix_template_segments_template_id', 'template_segments', ['template_id'])
    op.create_index('ix_template_segments_video_id', 'template_segments', ['video_id'])
    op.create_index('ix_template_segments_timestamp_ms', 'template_segments', ['timestamp_ms'])
    op.create_index('ix_template_segments_scene_type', 'template_segments', ['scene_type'])
    op.create_index('ix_template_segments_audio_type', 'template_segments', ['audio_type'])
    op.create_index('ix_template_segments_has_text', 'template_segments', ['has_text_overlay'])
    op.create_index('ix_template_segments_music', 'template_segments', ['music_present'])
    op.create_index('ix_template_segments_speech', 'template_segments', ['speech_present'])
    op.create_index('ix_template_segments_key_moment', 'template_segments', ['is_key_moment'])
    op.create_index('ix_template_segments_key_type', 'template_segments', ['key_moment_type'])
    op.create_index('ix_template_segments_scene_audio', 'template_segments', ['scene_type', 'audio_type'])
    op.create_index('ix_template_segments_key_moments', 'template_segments', ['is_key_moment', 'key_moment_type'])
    op.create_index('ix_template_segments_template_time', 'template_segments', ['template_id', 'timestamp_ms'])


def downgrade() -> None:
    # Drop template_segments table and indexes
    op.drop_index('ix_template_segments_template_time', table_name='template_segments')
    op.drop_index('ix_template_segments_key_moments', table_name='template_segments')
    op.drop_index('ix_template_segments_scene_audio', table_name='template_segments')
    op.drop_index('ix_template_segments_key_type', table_name='template_segments')
    op.drop_index('ix_template_segments_key_moment', table_name='template_segments')
    op.drop_index('ix_template_segments_speech', table_name='template_segments')
    op.drop_index('ix_template_segments_music', table_name='template_segments')
    op.drop_index('ix_template_segments_has_text', table_name='template_segments')
    op.drop_index('ix_template_segments_audio_type', table_name='template_segments')
    op.drop_index('ix_template_segments_scene_type', table_name='template_segments')
    op.drop_index('ix_template_segments_timestamp_ms', table_name='template_segments')
    op.drop_index('ix_template_segments_video_id', table_name='template_segments')
    op.drop_index('ix_template_segments_template_id', table_name='template_segments')
    op.drop_table('template_segments')
    
    # Drop video_templates table and indexes
    op.drop_index('ix_video_templates_style_tags', table_name='video_templates')
    op.drop_index('ix_video_templates_pacing_score', table_name='video_templates')
    op.drop_index('ix_video_templates_status', table_name='video_templates')
    op.drop_index('ix_video_templates_pacing', table_name='video_templates')
    op.drop_index('ix_video_templates_score', table_name='video_templates')
    op.drop_index('ix_video_templates_video_id', table_name='video_templates')
    op.drop_table('video_templates')
