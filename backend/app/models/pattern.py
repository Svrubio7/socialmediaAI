"""
Pattern and Template models for storing analyzed video patterns and hybrid templates.
"""

from sqlalchemy import Column, String, Float, ForeignKey, Text, Integer, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin


class Pattern(Base, TimestampMixin):
    """Pattern model for storing individual video pattern analysis results."""
    
    __tablename__ = "patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Pattern information
    type = Column(String(100), nullable=False, index=True)  # hook_timing, cut_frequency, text_overlays, etc.
    score = Column(Float, default=0.0, nullable=False, index=True)  # 0-100 score
    
    # Pattern data (flexible JSON structure)
    data = Column(JSONB, nullable=False, default=dict)
    
    # Description
    description = Column(String(500), nullable=True)
    
    # Relationships
    video = relationship("Video", back_populates="patterns")
    
    def __repr__(self):
        return f"<Pattern(id={self.id}, type={self.type}, score={self.score})>"


class VideoTemplate(Base, TimestampMixin):
    """
    Video Template model for storing hybrid templates.
    
    Contains the full structured analysis of a video at 0.2s intervals,
    including visual, audio, and natural language descriptions for each segment.
    """
    
    __tablename__ = "video_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Template metadata
    model_version = Column(String(50), nullable=False, default="gemini-2.0-flash")
    interval_ms = Column(Integer, nullable=False, default=200)  # 200ms = 0.2s intervals
    
    # Video info cache
    duration_seconds = Column(Float, nullable=False)
    total_segments = Column(Integer, nullable=False)
    
    # Quality/performance score
    score = Column(Float, default=0.0, nullable=False, index=True)
    
    # Status
    status = Column(String(50), nullable=False, default="processing")  # processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Full template data (JSONB for efficient querying)
    # Contains: segments[], summary{}
    template_data = Column(JSONB, nullable=False, default=dict)
    
    # Denormalized summary fields for efficient filtering/sorting
    # These are extracted from template_data.summary for query performance
    pacing = Column(String(20), nullable=True, index=True)  # very-fast, fast, moderate, slow, very-slow
    total_cuts = Column(Integer, nullable=True)
    average_shot_duration_ms = Column(Integer, nullable=True)
    hook_duration_ms = Column(Integer, nullable=True)
    music_coverage_percent = Column(Float, nullable=True)
    speech_coverage_percent = Column(Float, nullable=True)
    text_overlay_count = Column(Integer, nullable=True)
    
    # Style tags stored separately for efficient tag-based queries
    style_tags = Column(JSONB, nullable=True, default=list)
    
    # Relationships
    video = relationship("Video", back_populates="templates")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_video_templates_pacing_score', 'pacing', 'score'),
        Index('ix_video_templates_style_tags', 'style_tags', postgresql_using='gin'),
        Index('ix_video_templates_status', 'status'),
    )
    
    def __repr__(self):
        return f"<VideoTemplate(id={self.id}, video_id={self.video_id}, segments={self.total_segments})>"
    
    @classmethod
    def from_hybrid_template(cls, template_dict: dict) -> "VideoTemplate":
        """Create a VideoTemplate instance from a HybridTemplate dictionary."""
        summary = template_dict.get("summary", {})
        
        return cls(
            video_id=template_dict.get("video_id"),
            model_version=template_dict.get("model_version", "gemini-2.0-flash"),
            interval_ms=template_dict.get("interval_ms", 200),
            duration_seconds=template_dict.get("duration_seconds", 0),
            total_segments=len(template_dict.get("segments", [])),
            status="completed",
            template_data=template_dict,
            # Denormalized summary fields
            pacing=summary.get("pacing"),
            total_cuts=summary.get("total_cuts"),
            average_shot_duration_ms=summary.get("average_shot_duration_ms"),
            hook_duration_ms=summary.get("hook_duration_ms"),
            music_coverage_percent=summary.get("music_coverage_percent"),
            speech_coverage_percent=summary.get("speech_coverage_percent"),
            text_overlay_count=summary.get("text_overlay_count"),
            style_tags=summary.get("style_tags", []),
        )
    
    def get_segments(self) -> list:
        """Get all segments from the template data."""
        return self.template_data.get("segments", [])
    
    def get_summary(self) -> dict:
        """Get the summary from the template data."""
        return self.template_data.get("summary", {})
    
    def get_segment_at(self, timestamp_ms: int) -> dict | None:
        """Get the segment at a specific timestamp."""
        segments = self.get_segments()
        for segment in segments:
            if segment.get("timestamp_ms", 0) <= timestamp_ms < segment.get("timestamp_end_ms", 0):
                return segment
        return None
    
    def get_key_moments(self) -> list:
        """Get all key moments from the template."""
        segments = self.get_segments()
        return [s for s in segments if s.get("is_key_moment", False)]


class TemplateSegment(Base, TimestampMixin):
    """
    Individual segment storage for efficient segment-level queries.
    
    This table stores each segment separately for use cases where
    we need to query across segments from multiple templates
    (e.g., "find all hooks with question-format text").
    """
    
    __tablename__ = "template_segments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    template_id = Column(UUID(as_uuid=True), ForeignKey("video_templates.id", ondelete="CASCADE"), nullable=False, index=True)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Timing
    timestamp_ms = Column(Integer, nullable=False, index=True)
    timestamp_end_ms = Column(Integer, nullable=False)
    
    # Denormalized visual fields
    scene_type = Column(String(50), nullable=True, index=True)
    camera_motion = Column(String(50), nullable=True)
    has_text_overlay = Column(Boolean, default=False, index=True)
    text_overlay = Column(Text, nullable=True)
    transition_in = Column(String(50), nullable=True)
    
    # Denormalized audio fields
    audio_type = Column(String(50), nullable=True, index=True)
    music_present = Column(Boolean, default=False, index=True)
    speech_present = Column(Boolean, default=False, index=True)
    
    # Key moment flag
    is_key_moment = Column(Boolean, default=False, index=True)
    key_moment_type = Column(String(50), nullable=True, index=True)
    
    # Natural language description
    description = Column(Text, nullable=True)
    
    # Full segment data (for complete access)
    segment_data = Column(JSONB, nullable=False, default=dict)
    
    # Indexes
    __table_args__ = (
        Index('ix_template_segments_scene_audio', 'scene_type', 'audio_type'),
        Index('ix_template_segments_key_moments', 'is_key_moment', 'key_moment_type'),
        Index('ix_template_segments_template_time', 'template_id', 'timestamp_ms'),
    )
    
    def __repr__(self):
        return f"<TemplateSegment(id={self.id}, timestamp_ms={self.timestamp_ms}, scene={self.scene_type})>"
    
    @classmethod
    def from_segment_dict(
        cls,
        segment: dict,
        template_id: str,
        video_id: str,
    ) -> "TemplateSegment":
        """Create a TemplateSegment from a segment dictionary."""
        visual = segment.get("visual", {})
        audio = segment.get("audio", {})
        
        return cls(
            template_id=template_id,
            video_id=video_id,
            timestamp_ms=segment.get("timestamp_ms", 0),
            timestamp_end_ms=segment.get("timestamp_end_ms", 0),
            scene_type=visual.get("scene_type"),
            camera_motion=visual.get("camera_motion"),
            has_text_overlay=bool(visual.get("text_overlay")),
            text_overlay=visual.get("text_overlay"),
            transition_in=visual.get("transition_in"),
            audio_type=audio.get("type"),
            music_present=audio.get("music_present", False),
            speech_present=audio.get("speech_present", False),
            is_key_moment=segment.get("is_key_moment", False),
            key_moment_type=segment.get("key_moment_type"),
            description=segment.get("description"),
            segment_data=segment,
        )
