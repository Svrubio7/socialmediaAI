"""
Pattern Analysis Service - Uses Gemini 2.0 Flash for video pattern extraction.
Generates hybrid templates with structured JSON + natural language descriptions.
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import base64
import asyncio
from pathlib import Path
from datetime import datetime
import logging

from app.core.config import settings
from app.schemas.pattern import (
    HybridTemplate,
    HybridSegment,
    VisualSegment,
    AudioSegment,
    TemplateSummary,
    SceneType,
    CameraMotion,
    TransitionType,
    AudioType,
    AudioTransition,
    PacingType,
)

logger = logging.getLogger(__name__)


class PatternService:
    """Service for analyzing video patterns using Gemini 2.0 Flash."""

    def __init__(self, gemini_api_key: str):
        """Initialize the pattern service with Gemini API key."""
        self.api_key = gemini_api_key
        self._client = None
        self._model = None

    @property
    def client(self):
        """Lazy load Gemini client."""
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self._client = genai
        return self._client

    @property
    def model(self):
        """Get the Gemini 2.0 Flash model."""
        if self._model is None:
            self._model = self.client.GenerativeModel(settings.GEMINI_MODEL)
        return self._model

    def _load_image_as_base64(self, image_path: str) -> Optional[str]:
        """Load an image file and return as base64 string."""
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode("utf-8")
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            return None

    def _build_segment_analysis_prompt(self, segment_index: int, total_segments: int) -> str:
        """Build prompt for analyzing a batch of frames."""
        return f"""Analyze these video frames (segment {segment_index + 1} of {total_segments}) and provide detailed analysis.

For EACH frame, provide a JSON object with this EXACT structure:
{{
    "visual": {{
        "scene_type": "one of: close-up, medium-shot, wide-shot, extreme-close-up, over-shoulder, pov, aerial, cutaway, insert, b-roll, talking-head, product-shot, text-only, transition, other",
        "subject": "main subject description",
        "camera_motion": "one of: static, pan-left, pan-right, tilt-up, tilt-down, zoom-in, zoom-out, dolly-in, dolly-out, tracking, handheld, crane, shake, slow-zoom",
        "transition_in": "one of: cut, fade-in, fade-out, cross-dissolve, wipe, slide, zoom-transition, whip-pan, flash, glitch, morph, none OR null",
        "dominant_colors": ["#hex1", "#hex2"],
        "text_overlay": "visible text or null",
        "text_position": "top/center/bottom or null",
        "brightness": 0.0-1.0,
        "visual_effects": ["effect1", "effect2"]
    }},
    "audio_inference": {{
        "likely_type": "speech/music/sound-effect/ambient/silence/voiceover/mixed",
        "speech_present": true/false,
        "music_present": true/false,
        "estimated_energy": 0.0-1.0
    }},
    "description": "Detailed natural language description of what's happening in this frame. Be specific about actions, expressions, movements, and context."
}}

Return a JSON array with one object per frame. Focus on:
1. Visual composition and framing
2. Subject actions and expressions
3. Text overlays and graphics
4. Transitions between frames
5. Overall visual style and energy"""

    def _build_summary_prompt(self) -> str:
        """Build prompt for generating video summary."""
        return """Based on all the segment analyses provided, generate a comprehensive summary of the video.

Return a JSON object with this EXACT structure:
{
    "total_cuts": <number of scene changes>,
    "average_shot_duration_ms": <average shot length>,
    "hook_duration_ms": <how long until the hook captures attention>,
    "hook_description": "description of the hook technique used",
    "pacing": "one of: very-fast, fast, moderate, slow, very-slow",
    "style_tags": ["tag1", "tag2", "tag3"],
    "dominant_colors": ["#hex1", "#hex2", "#hex3", "#hex4", "#hex5"],
    "music_coverage_percent": 0-100,
    "speech_coverage_percent": 0-100,
    "text_overlay_count": <number>,
    "key_moments": [
        {"timestamp_ms": 0, "type": "hook", "description": "..."},
        {"timestamp_ms": 3000, "type": "transition", "description": "..."}
    ],
    "content_structure": "Natural language description of the overall video structure, flow, and storytelling approach."
}

Analyze patterns like:
- Hook effectiveness and timing
- Pacing and rhythm
- Visual consistency
- Text usage patterns
- Transition styles
- Overall engagement strategy"""

    async def analyze_frames_batch(
        self,
        frames: List[Tuple[str, int]],
        batch_size: int = 25,
    ) -> List[Dict[str, Any]]:
        """
        Analyze frames in batches using Gemini 2.0 Flash.
        
        Args:
            frames: List of (frame_path, timestamp_ms) tuples
            batch_size: Number of frames per API call
            
        Returns:
            List of analysis results for each frame
        """
        all_results = []
        total_batches = (len(frames) + batch_size - 1) // batch_size
        
        for batch_idx in range(0, len(frames), batch_size):
            batch = frames[batch_idx:batch_idx + batch_size]
            batch_num = batch_idx // batch_size + 1
            
            logger.info(f"Analyzing batch {batch_num}/{total_batches} ({len(batch)} frames)")
            
            # Prepare images for this batch
            content_parts = []
            
            # Add prompt
            prompt = self._build_segment_analysis_prompt(batch_idx, len(frames))
            content_parts.append(prompt)
            
            # Add images
            for frame_path, timestamp_ms in batch:
                try:
                    # Load image
                    img_data = self._load_image_as_base64(frame_path)
                    if img_data:
                        content_parts.append({
                            "mime_type": "image/jpeg",
                            "data": img_data
                        })
                        content_parts.append(f"[Frame at {timestamp_ms}ms]")
                except Exception as e:
                    logger.error(f"Failed to load frame {frame_path}: {e}")
            
            # Call Gemini API
            try:
                response = await asyncio.to_thread(
                    self.model.generate_content,
                    content_parts,
                    generation_config={
                        "temperature": 0.2,
                        "top_p": 0.8,
                        "max_output_tokens": 8192,
                    }
                )
                
                # Parse response
                response_text = response.text
                
                # Try to extract JSON from response
                try:
                    # Handle potential markdown code blocks
                    if "```json" in response_text:
                        response_text = response_text.split("```json")[1].split("```")[0]
                    elif "```" in response_text:
                        response_text = response_text.split("```")[1].split("```")[0]
                    
                    batch_results = json.loads(response_text)
                    
                    # Add timestamps to results
                    for i, result in enumerate(batch_results):
                        if batch_idx + i < len(frames):
                            result["timestamp_ms"] = frames[batch_idx + i][1]
                    
                    all_results.extend(batch_results)
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON from batch {batch_num}: {e}")
                    # Create placeholder results for failed batch
                    for frame_path, timestamp_ms in batch:
                        all_results.append({
                            "timestamp_ms": timestamp_ms,
                            "visual": {
                                "scene_type": "other",
                                "subject": "analysis failed",
                                "camera_motion": "static",
                            },
                            "audio_inference": {
                                "likely_type": "mixed",
                                "speech_present": False,
                                "music_present": False,
                                "estimated_energy": 0.5,
                            },
                            "description": "Frame analysis failed - placeholder",
                        })
                        
            except Exception as e:
                logger.error(f"Gemini API call failed for batch {batch_num}: {e}")
                # Create placeholder results
                for frame_path, timestamp_ms in batch:
                    all_results.append({
                        "timestamp_ms": timestamp_ms,
                        "visual": {
                            "scene_type": "other",
                            "subject": "analysis failed",
                            "camera_motion": "static",
                        },
                        "audio_inference": {
                            "likely_type": "mixed",
                            "speech_present": False,
                            "music_present": False,
                            "estimated_energy": 0.5,
                        },
                        "description": "API call failed - placeholder",
                    })
        
        return all_results

    def _convert_to_hybrid_segment(
        self,
        analysis: Dict[str, Any],
        interval_ms: int = 200,
    ) -> HybridSegment:
        """Convert raw analysis to HybridSegment schema."""
        timestamp_ms = analysis.get("timestamp_ms", 0)
        visual_data = analysis.get("visual", {})
        audio_data = analysis.get("audio_inference", {})
        
        # Map scene type
        scene_type_map = {
            "close-up": SceneType.CLOSE_UP,
            "medium-shot": SceneType.MEDIUM_SHOT,
            "wide-shot": SceneType.WIDE_SHOT,
            "extreme-close-up": SceneType.EXTREME_CLOSE_UP,
            "over-shoulder": SceneType.OVER_SHOULDER,
            "pov": SceneType.POV,
            "aerial": SceneType.AERIAL,
            "cutaway": SceneType.CUTAWAY,
            "insert": SceneType.INSERT,
            "b-roll": SceneType.B_ROLL,
            "talking-head": SceneType.TALKING_HEAD,
            "product-shot": SceneType.PRODUCT_SHOT,
            "text-only": SceneType.TEXT_ONLY,
            "transition": SceneType.TRANSITION,
        }
        
        camera_motion_map = {
            "static": CameraMotion.STATIC,
            "pan-left": CameraMotion.PAN_LEFT,
            "pan-right": CameraMotion.PAN_RIGHT,
            "tilt-up": CameraMotion.TILT_UP,
            "tilt-down": CameraMotion.TILT_DOWN,
            "zoom-in": CameraMotion.ZOOM_IN,
            "zoom-out": CameraMotion.ZOOM_OUT,
            "dolly-in": CameraMotion.DOLLY_IN,
            "dolly-out": CameraMotion.DOLLY_OUT,
            "tracking": CameraMotion.TRACKING,
            "handheld": CameraMotion.HANDHELD,
            "crane": CameraMotion.CRANE,
            "shake": CameraMotion.SHAKE,
            "slow-zoom": CameraMotion.SLOW_ZOOM,
        }
        
        transition_map = {
            "cut": TransitionType.CUT,
            "fade-in": TransitionType.FADE_IN,
            "fade-out": TransitionType.FADE_OUT,
            "cross-dissolve": TransitionType.CROSS_DISSOLVE,
            "wipe": TransitionType.WIPE,
            "slide": TransitionType.SLIDE,
            "zoom-transition": TransitionType.ZOOM_TRANSITION,
            "whip-pan": TransitionType.WHIP_PAN,
            "flash": TransitionType.FLASH,
            "glitch": TransitionType.GLITCH,
            "morph": TransitionType.MORPH,
            "none": TransitionType.NONE,
        }
        
        audio_type_map = {
            "speech": AudioType.SPEECH,
            "music": AudioType.MUSIC,
            "sound-effect": AudioType.SOUND_EFFECT,
            "ambient": AudioType.AMBIENT,
            "silence": AudioType.SILENCE,
            "voiceover": AudioType.VOICEOVER,
            "mixed": AudioType.MIXED,
        }
        
        # Build visual segment
        visual = VisualSegment(
            scene_type=scene_type_map.get(visual_data.get("scene_type", "").lower(), SceneType.OTHER),
            subject=visual_data.get("subject", "unknown"),
            camera_motion=camera_motion_map.get(visual_data.get("camera_motion", "").lower(), CameraMotion.STATIC),
            transition_in=transition_map.get(visual_data.get("transition_in", "").lower() if visual_data.get("transition_in") else None),
            dominant_colors=visual_data.get("dominant_colors", []),
            text_overlay=visual_data.get("text_overlay"),
            text_position=visual_data.get("text_position"),
            text_style=visual_data.get("text_style"),
            brightness=visual_data.get("brightness"),
            composition=visual_data.get("composition"),
            visual_effects=visual_data.get("visual_effects", []),
        )
        
        # Build audio segment (inferred from visual analysis)
        audio = AudioSegment(
            type=audio_type_map.get(audio_data.get("likely_type", "").lower(), AudioType.MIXED),
            volume_level=audio_data.get("estimated_energy", 0.5),
            music_present=audio_data.get("music_present", False),
            speech_present=audio_data.get("speech_present", False),
            transition=AudioTransition.NONE,
        )
        
        # Detect key moments
        is_key_moment = False
        key_moment_type = None
        
        if timestamp_ms < 3000:  # First 3 seconds = potential hook
            is_key_moment = True
            key_moment_type = "hook"
        elif visual_data.get("transition_in") and visual_data.get("transition_in") != "cut":
            is_key_moment = True
            key_moment_type = "transition"
        
        return HybridSegment(
            timestamp_ms=timestamp_ms,
            timestamp_end_ms=timestamp_ms + interval_ms,
            visual=visual,
            audio=audio,
            description=analysis.get("description", "No description available"),
            is_key_moment=is_key_moment,
            key_moment_type=key_moment_type,
        )

    async def generate_summary(
        self,
        segments: List[HybridSegment],
        video_info: Dict[str, Any],
    ) -> TemplateSummary:
        """Generate summary analysis from all segments."""
        
        # Prepare summary of segments for the API
        segment_summaries = []
        for i, seg in enumerate(segments[:50]):  # First 50 segments for context
            segment_summaries.append({
                "timestamp_ms": seg.timestamp_ms,
                "scene_type": seg.visual.scene_type.value,
                "subject": seg.visual.subject,
                "has_text": bool(seg.visual.text_overlay),
                "description": seg.description[:200],
            })
        
        prompt = f"""Analyze this video based on the segment data provided:

Video Info:
- Duration: {video_info.get('duration', 0)} seconds
- Resolution: {video_info.get('width', 0)}x{video_info.get('height', 0)}
- Total segments analyzed: {len(segments)}

Sample segments:
{json.dumps(segment_summaries, indent=2)}

{self._build_summary_prompt()}"""

        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "max_output_tokens": 4096,
                }
            )
            
            response_text = response.text
            
            # Extract JSON
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0]
            
            summary_data = json.loads(response_text)
            
            # Map pacing
            pacing_map = {
                "very-fast": PacingType.VERY_FAST,
                "fast": PacingType.FAST,
                "moderate": PacingType.MODERATE,
                "slow": PacingType.SLOW,
                "very-slow": PacingType.VERY_SLOW,
            }
            
            return TemplateSummary(
                total_duration_ms=int(video_info.get("duration", 0) * 1000),
                total_segments=len(segments),
                total_cuts=summary_data.get("total_cuts", 0),
                average_shot_duration_ms=summary_data.get("average_shot_duration_ms", 2000),
                hook_duration_ms=summary_data.get("hook_duration_ms", 3000),
                hook_description=summary_data.get("hook_description", "No hook detected"),
                pacing=pacing_map.get(summary_data.get("pacing", "").lower(), PacingType.MODERATE),
                style_tags=summary_data.get("style_tags", []),
                dominant_colors=summary_data.get("dominant_colors", []),
                music_coverage_percent=summary_data.get("music_coverage_percent", 0),
                speech_coverage_percent=summary_data.get("speech_coverage_percent", 0),
                text_overlay_count=summary_data.get("text_overlay_count", 0),
                key_moments=summary_data.get("key_moments", []),
                content_structure=summary_data.get("content_structure", "Structure not analyzed"),
            )
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            
            # Calculate basic stats from segments
            cuts = sum(1 for s in segments if s.visual.transition_in and s.visual.transition_in != TransitionType.NONE)
            text_count = sum(1 for s in segments if s.visual.text_overlay)
            music_segments = sum(1 for s in segments if s.audio.music_present)
            speech_segments = sum(1 for s in segments if s.audio.speech_present)
            
            return TemplateSummary(
                total_duration_ms=int(video_info.get("duration", 0) * 1000),
                total_segments=len(segments),
                total_cuts=cuts,
                average_shot_duration_ms=2000,
                hook_duration_ms=3000,
                hook_description="Analysis failed - default hook",
                pacing=PacingType.MODERATE,
                style_tags=["unanalyzed"],
                dominant_colors=[],
                music_coverage_percent=(music_segments / len(segments) * 100) if segments else 0,
                speech_coverage_percent=(speech_segments / len(segments) * 100) if segments else 0,
                text_overlay_count=text_count,
                key_moments=[],
                content_structure="Summary generation failed - structure unknown",
            )

    def analyze_video_with_template(
        self,
        video_id: str,
        frames: List[Tuple[str, int]],
        audio_path: str,
        audio_segments: List[Dict[str, Any]],
        video_info: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Main entry point: Analyze video and generate hybrid template.
        
        Args:
            video_id: ID of the video
            frames: List of (frame_path, timestamp_ms) tuples
            audio_path: Path to extracted audio file
            audio_segments: List of audio segment metadata
            video_info: Video metadata
            
        Returns:
            HybridTemplate as dictionary
        """
        import asyncio
        
        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Analyze frames
            logger.info(f"Analyzing {len(frames)} frames for video {video_id}")
            raw_analyses = loop.run_until_complete(
                self.analyze_frames_batch(frames, batch_size=25)
            )
            
            # Convert to hybrid segments
            interval_ms = settings.FRAME_EXTRACTION_INTERVAL_MS
            segments = [
                self._convert_to_hybrid_segment(analysis, interval_ms)
                for analysis in raw_analyses
            ]
            
            # Generate summary
            logger.info(f"Generating summary for video {video_id}")
            summary = loop.run_until_complete(
                self.generate_summary(segments, video_info)
            )
            
            # Build template
            template = HybridTemplate(
                video_id=video_id,
                duration_seconds=video_info.get("duration", 0),
                interval_ms=interval_ms,
                created_at=datetime.utcnow(),
                model_version=settings.GEMINI_MODEL,
                segments=segments,
                summary=summary,
            )
            
            logger.info(f"Generated hybrid template with {len(segments)} segments for video {video_id}")
            return template.model_dump()
            
        finally:
            loop.close()

    async def calculate_pattern_score(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any],
        performance_data: Optional[Dict[str, Any]] = None,
    ) -> float:
        """
        Calculate a score for a pattern based on its characteristics and performance.
        
        Args:
            pattern_type: Type of pattern
            pattern_data: Pattern details
            performance_data: Optional performance metrics
            
        Returns:
            Score from 0-100
        """
        base_score = 50.0
        
        if performance_data:
            # Adjust score based on performance
            engagement_rate = performance_data.get("engagement_rate", 0)
            if engagement_rate > 10:
                base_score += 30
            elif engagement_rate > 5:
                base_score += 20
            elif engagement_rate > 2:
                base_score += 10
            
            # Views impact
            views = performance_data.get("views", 0)
            if views > 100000:
                base_score += 15
            elif views > 10000:
                base_score += 10
            elif views > 1000:
                base_score += 5
        
        return min(100.0, max(0.0, base_score))

    def compare_templates(
        self,
        template1: HybridTemplate,
        template2: HybridTemplate,
    ) -> Dict[str, Any]:
        """
        Compare two templates and return similarity metrics.
        
        Args:
            template1: First template
            template2: Second template
            
        Returns:
            Comparison results with similarity scores
        """
        # Compare summaries
        pacing_match = template1.summary.pacing == template2.summary.pacing
        style_overlap = len(set(template1.summary.style_tags) & set(template2.summary.style_tags))
        
        # Compare segment patterns
        scene_types_1 = [s.visual.scene_type for s in template1.segments]
        scene_types_2 = [s.visual.scene_type for s in template2.segments]
        
        # Simple similarity based on scene type distribution
        from collections import Counter
        dist1 = Counter(scene_types_1)
        dist2 = Counter(scene_types_2)
        
        all_types = set(dist1.keys()) | set(dist2.keys())
        similarity = sum(
            min(dist1.get(t, 0), dist2.get(t, 0)) 
            for t in all_types
        ) / max(len(scene_types_1), len(scene_types_2), 1)
        
        return {
            "pacing_match": pacing_match,
            "style_tag_overlap": style_overlap,
            "scene_type_similarity": similarity,
            "overall_similarity": (
                (0.3 if pacing_match else 0) +
                (0.3 * min(style_overlap / 3, 1)) +
                (0.4 * similarity)
            ),
        }
