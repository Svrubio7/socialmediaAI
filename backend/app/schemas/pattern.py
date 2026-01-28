"""
Pattern schemas for request/response validation.
Includes hybrid template structure with JSON + natural language descriptions.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum


# =============================================================================
# Enums for structured data
# =============================================================================

class SceneType(str, Enum):
    """Types of scenes/shots in a video."""
    CLOSE_UP = "close-up"
    MEDIUM_SHOT = "medium-shot"
    WIDE_SHOT = "wide-shot"
    EXTREME_CLOSE_UP = "extreme-close-up"
    OVER_SHOULDER = "over-shoulder"
    POV = "pov"
    AERIAL = "aerial"
    CUTAWAY = "cutaway"
    INSERT = "insert"
    B_ROLL = "b-roll"
    TALKING_HEAD = "talking-head"
    PRODUCT_SHOT = "product-shot"
    TEXT_ONLY = "text-only"
    TRANSITION = "transition"
    OTHER = "other"


class CameraMotion(str, Enum):
    """Types of camera movements."""
    STATIC = "static"
    PAN_LEFT = "pan-left"
    PAN_RIGHT = "pan-right"
    TILT_UP = "tilt-up"
    TILT_DOWN = "tilt-down"
    ZOOM_IN = "zoom-in"
    ZOOM_OUT = "zoom-out"
    DOLLY_IN = "dolly-in"
    DOLLY_OUT = "dolly-out"
    TRACKING = "tracking"
    HANDHELD = "handheld"
    CRANE = "crane"
    SHAKE = "shake"
    SLOW_ZOOM = "slow-zoom"


class TransitionType(str, Enum):
    """Types of visual transitions."""
    CUT = "cut"
    FADE_IN = "fade-in"
    FADE_OUT = "fade-out"
    CROSS_DISSOLVE = "cross-dissolve"
    WIPE = "wipe"
    SLIDE = "slide"
    ZOOM_TRANSITION = "zoom-transition"
    WHIP_PAN = "whip-pan"
    FLASH = "flash"
    GLITCH = "glitch"
    MORPH = "morph"
    NONE = "none"


class AudioType(str, Enum):
    """Types of audio content."""
    SPEECH = "speech"
    MUSIC = "music"
    SOUND_EFFECT = "sound-effect"
    AMBIENT = "ambient"
    SILENCE = "silence"
    VOICEOVER = "voiceover"
    MIXED = "mixed"


class AudioTransition(str, Enum):
    """Types of audio transitions."""
    FADE_IN = "fade-in"
    FADE_OUT = "fade-out"
    CROSSFADE = "crossfade"
    CUT = "cut"
    DUCK = "duck"
    SWELL = "swell"
    DROP = "drop"
    NONE = "none"


class PacingType(str, Enum):
    """Overall video pacing."""
    VERY_FAST = "very-fast"  # <1s average shot
    FAST = "fast"  # 1-2s average shot
    MODERATE = "moderate"  # 2-4s average shot
    SLOW = "slow"  # 4-6s average shot
    VERY_SLOW = "very-slow"  # >6s average shot


# =============================================================================
# Visual Segment Schema
# =============================================================================

class VisualSegment(BaseModel):
    """Visual information for a single segment."""
    scene_type: SceneType = Field(description="Type of shot/scene")
    subject: str = Field(description="Main subject in the frame")
    camera_motion: CameraMotion = Field(default=CameraMotion.STATIC)
    transition_in: Optional[TransitionType] = Field(default=None, description="Transition entering this segment")
    transition_out: Optional[TransitionType] = Field(default=None, description="Transition exiting this segment")
    dominant_colors: List[str] = Field(default_factory=list, description="Hex color codes of dominant colors")
    text_overlay: Optional[str] = Field(default=None, description="Any text visible on screen")
    text_position: Optional[str] = Field(default=None, description="Position of text overlay (top, center, bottom)")
    text_style: Optional[str] = Field(default=None, description="Style of text (bold, outlined, animated, etc)")
    brightness: Optional[float] = Field(default=None, ge=0, le=1, description="Relative brightness 0-1")
    composition: Optional[str] = Field(default=None, description="Composition notes (rule of thirds, centered, etc)")
    visual_effects: List[str] = Field(default_factory=list, description="Any visual effects applied")


# =============================================================================
# Audio Segment Schema
# =============================================================================

class AudioSegment(BaseModel):
    """Audio information for a single segment."""
    type: AudioType = Field(description="Primary audio type in this segment")
    volume_level: float = Field(ge=0, le=1, description="Relative volume 0-1")
    music_present: bool = Field(default=False)
    music_genre: Optional[str] = Field(default=None, description="Genre if music present")
    music_energy: Optional[float] = Field(default=None, ge=0, le=1, description="Music energy level 0-1")
    music_bpm: Optional[int] = Field(default=None, description="Estimated BPM if music present")
    sound_effect: Optional[str] = Field(default=None, description="Description of sound effect if present")
    speech_present: bool = Field(default=False)
    speech_tone: Optional[str] = Field(default=None, description="Tone of speech (excited, calm, urgent, etc)")
    speech_pace: Optional[str] = Field(default=None, description="Pace of speech (fast, normal, slow)")
    transition: AudioTransition = Field(default=AudioTransition.NONE)
    beat_drop: bool = Field(default=False, description="Whether there's a beat drop in this segment")
    silence: bool = Field(default=False, description="Whether this segment is silent/near-silent")


# =============================================================================
# Hybrid Segment Schema (Visual + Audio + Description)
# =============================================================================

class HybridSegment(BaseModel):
    """
    A single segment (0.2s) of the video template.
    Combines structured JSON data with natural language description.
    """
    timestamp_ms: int = Field(ge=0, description="Start timestamp in milliseconds")
    timestamp_end_ms: int = Field(ge=0, description="End timestamp in milliseconds")
    visual: VisualSegment = Field(description="Visual analysis for this segment")
    audio: AudioSegment = Field(description="Audio analysis for this segment")
    description: str = Field(
        description="Natural language description of what's happening in this segment. "
                    "Should be detailed enough for an LLM to understand context and recreate similar content."
    )
    is_key_moment: bool = Field(default=False, description="Whether this is a significant moment (hook, transition, climax)")
    key_moment_type: Optional[str] = Field(default=None, description="Type of key moment if applicable")
    
    class Config:
        json_schema_extra = {
            "example": {
                "timestamp_ms": 0,
                "timestamp_end_ms": 200,
                "visual": {
                    "scene_type": "close-up",
                    "subject": "person speaking to camera",
                    "camera_motion": "static",
                    "transition_in": None,
                    "dominant_colors": ["#1a1a1a", "#ffffff"],
                    "text_overlay": "Are you tired of...",
                    "text_position": "bottom",
                    "text_style": "bold-outlined"
                },
                "audio": {
                    "type": "speech",
                    "volume_level": 0.8,
                    "music_present": True,
                    "music_energy": 0.3,
                    "speech_present": True,
                    "speech_tone": "excited",
                    "transition": "fade-in"
                },
                "description": "Opening hook with direct address to camera. Speaker maintains eye contact with an excited expression, dark background creates focus on the subject. Bold text overlay appears with a question format to immediately engage the viewer. Low-energy background music fades in."
            }
        }


# =============================================================================
# Template Summary Schema
# =============================================================================

class TemplateSummary(BaseModel):
    """Summary statistics and analysis of the full video template."""
    total_duration_ms: int = Field(description="Total video duration in milliseconds")
    total_segments: int = Field(description="Total number of segments analyzed")
    total_cuts: int = Field(description="Number of scene cuts/transitions")
    average_shot_duration_ms: int = Field(description="Average duration of each shot")
    hook_duration_ms: int = Field(description="Duration of the opening hook (first attention-grab)")
    hook_description: str = Field(description="Description of the hook technique used")
    pacing: PacingType = Field(description="Overall video pacing")
    style_tags: List[str] = Field(description="Tags describing the video style")
    dominant_colors: List[str] = Field(description="Top 5 dominant colors across the video")
    music_coverage_percent: float = Field(ge=0, le=100, description="Percentage of video with music")
    speech_coverage_percent: float = Field(ge=0, le=100, description="Percentage of video with speech")
    text_overlay_count: int = Field(description="Number of distinct text overlays")
    key_moments: List[Dict[str, Any]] = Field(description="List of key moments with timestamps and descriptions")
    content_structure: str = Field(description="Natural language description of the overall video structure")


# =============================================================================
# Full Hybrid Template Schema
# =============================================================================

class HybridTemplate(BaseModel):
    """
    Full hybrid template for a video.
    Contains both structured JSON data and natural language descriptions
    for each 0.2s segment of the video.
    """
    video_id: str = Field(description="UUID of the analyzed video")
    duration_seconds: float = Field(description="Total duration in seconds")
    interval_ms: int = Field(default=200, description="Analysis interval in milliseconds")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    model_version: str = Field(default="gemini-2.0-flash", description="AI model used for analysis")
    segments: List[HybridSegment] = Field(description="All segments of the video")
    summary: TemplateSummary = Field(description="Summary analysis of the full video")
    
    class Config:
        from_attributes = True


# =============================================================================
# Request/Response Schemas
# =============================================================================

class PatternData(BaseModel):
    """Legacy pattern data schema for backwards compatibility."""
    type: str
    description: Optional[str] = None
    timing: Optional[Dict[str, Any]] = None
    visual_elements: Optional[List[str]] = None
    audio_elements: Optional[List[str]] = None
    additional: Optional[Dict[str, Any]] = None


class PatternResponse(BaseModel):
    """Schema for pattern response."""
    id: UUID
    video_id: UUID
    type: str
    score: float
    data: Dict[str, Any]
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class PatternListResponse(BaseModel):
    """Schema for pattern list response."""
    items: List[PatternResponse]
    total: int


class PatternScoreUpdate(BaseModel):
    """Schema for updating pattern scores."""
    pattern_id: UUID
    new_score: float
    performance_data: Optional[Dict[str, Any]] = None


class TemplateResponse(BaseModel):
    """Schema for template response."""
    id: UUID
    video_id: UUID
    template: HybridTemplate
    score: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class TemplateCreateRequest(BaseModel):
    """Request to create a new template from video analysis."""
    video_id: UUID


class TemplateAnalysisStatus(BaseModel):
    """Status of template analysis job."""
    video_id: UUID
    status: str  # pending, processing, completed, failed
    progress_percent: float = Field(ge=0, le=100)
    estimated_completion_seconds: Optional[int] = None
    error_message: Optional[str] = None


# =============================================================================
# Template Application Schema (for video editing)
# =============================================================================

class TemplateApplicationRequest(BaseModel):
    """Request to apply a template to a new video."""
    source_video_id: UUID = Field(description="Video to edit")
    template_id: UUID = Field(description="Template to apply")
    platform: str = Field(default="tiktok", description="Target platform")
    adapt_duration: bool = Field(default=True, description="Adapt template to match source video duration")
    preserve_audio: bool = Field(default=True, description="Keep original audio from source")
    apply_text_overlays: bool = Field(default=True, description="Apply text overlay patterns")
    apply_transitions: bool = Field(default=True, description="Apply transition patterns")
    custom_text_overlays: Optional[List[Dict[str, Any]]] = Field(default=None, description="Custom text to overlay")


class TemplateApplicationResponse(BaseModel):
    """Response from template application."""
    task_id: str
    status: str
    source_video_id: UUID
    template_id: UUID
    output_video_id: Optional[UUID] = None
    estimated_completion_seconds: Optional[int] = None
