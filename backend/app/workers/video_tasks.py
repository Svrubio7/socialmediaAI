"""
Celery tasks for video processing with 0.2s interval frame extraction.
"""

from app.workers.celery_app import celery_app
from typing import Dict, Any, Optional, List, Tuple
import logging
import subprocess
import tempfile
import os
import json
import shutil
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def ensure_temp_dir() -> Path:
    """Ensure the temp processing directory exists."""
    temp_dir = Path(settings.TEMP_PROCESSING_DIR)
    temp_dir.mkdir(parents=True, exist_ok=True)
    return temp_dir


def get_video_info(video_path: str) -> Dict[str, Any]:
    """
    Get video metadata using ffprobe.
    
    Args:
        video_path: Path to the video file
        
    Returns:
        Dictionary with video metadata
    """
    cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        
        video_stream = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "video"),
            {}
        )
        audio_stream = next(
            (s for s in data.get("streams", []) if s.get("codec_type") == "audio"),
            {}
        )
        format_info = data.get("format", {})
        
        return {
            "duration": float(format_info.get("duration", 0)),
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "fps": eval(video_stream.get("r_frame_rate", "0/1")) if video_stream.get("r_frame_rate") else 0,
            "codec": video_stream.get("codec_name", ""),
            "bitrate": int(format_info.get("bit_rate", 0)),
            "has_audio": bool(audio_stream),
            "audio_codec": audio_stream.get("codec_name", ""),
            "audio_sample_rate": int(audio_stream.get("sample_rate", 0)),
        }
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as e:
        logger.error(f"Failed to get video info: {e}")
        return {}


def extract_frames_at_interval(
    video_path: str,
    output_dir: str,
    fps: float = 5.0,
    max_frames: int = 1500,
) -> List[Tuple[str, int]]:
    """
    Extract frames from video at specified FPS (0.2s intervals at 5fps).
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save extracted frames
        fps: Frames per second (5.0 = 0.2s intervals)
        max_frames: Maximum number of frames to extract
        
    Returns:
        List of tuples (frame_path, timestamp_ms)
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Get video duration first
    info = get_video_info(video_path)
    duration = info.get("duration", 0)
    
    if duration <= 0:
        logger.error(f"Invalid video duration: {duration}")
        return []
    
    # Calculate total frames and limit if needed
    total_frames = int(duration * fps)
    if total_frames > max_frames:
        logger.warning(f"Video would produce {total_frames} frames, limiting to {max_frames}")
        # Adjust duration to stay within limit
        duration = max_frames / fps
    
    # Extract frames using FFmpeg
    output_pattern = os.path.join(output_dir, "frame_%05d.jpg")
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vf", f"fps={fps}",
        "-t", str(duration),
        "-q:v", "2",  # High quality JPEG
        "-y",  # Overwrite existing files
        output_pattern
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg frame extraction failed: {e.stderr.decode()}")
        return []
    
    # Collect frame paths with timestamps
    frames = []
    interval_ms = int(1000 / fps)  # 200ms for 5fps
    
    for i, frame_file in enumerate(sorted(Path(output_dir).glob("frame_*.jpg"))):
        timestamp_ms = i * interval_ms
        frames.append((str(frame_file), timestamp_ms))
    
    logger.info(f"Extracted {len(frames)} frames at {fps}fps ({interval_ms}ms intervals)")
    return frames


def extract_audio_segments(
    video_path: str,
    output_dir: str,
    segment_duration_ms: int = 200,
    sample_rate: int = 16000,
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract audio and analyze it in segments matching frame intervals.
    
    Args:
        video_path: Path to the video file
        output_dir: Directory to save audio files
        segment_duration_ms: Duration of each segment in milliseconds
        sample_rate: Audio sample rate
        
    Returns:
        Tuple of (full_audio_path, list of segment info dicts)
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Extract full audio as WAV
    audio_path = os.path.join(output_dir, "audio.wav")
    
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",  # No video
        "-acodec", "pcm_s16le",
        "-ac", "1",  # Mono
        "-ar", str(sample_rate),
        "-y",
        audio_path
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.warning(f"Audio extraction failed (video may not have audio): {e}")
        return "", []
    
    if not os.path.exists(audio_path):
        return "", []
    
    # Get audio duration
    info = get_video_info(video_path)
    duration_ms = int(info.get("duration", 0) * 1000)
    
    # Create segment metadata
    segments = []
    segment_idx = 0
    current_ms = 0
    
    while current_ms < duration_ms:
        end_ms = min(current_ms + segment_duration_ms, duration_ms)
        segments.append({
            "index": segment_idx,
            "start_ms": current_ms,
            "end_ms": end_ms,
            "duration_ms": end_ms - current_ms,
        })
        current_ms = end_ms
        segment_idx += 1
    
    logger.info(f"Analyzed audio into {len(segments)} segments of {segment_duration_ms}ms")
    return audio_path, segments


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def extract_frames_task(
    self,
    video_id: str,
    video_path: str,
) -> Dict[str, Any]:
    """
    Extract frames from video at 5fps (0.2s intervals).
    
    Args:
        video_id: ID of the video
        video_path: Path to the video file
        
    Returns:
        Extraction results with frame paths and timestamps
    """
    try:
        logger.info(f"Starting frame extraction for video {video_id}")
        
        # Create temp directory for this video
        temp_dir = ensure_temp_dir()
        video_temp_dir = temp_dir / video_id
        frames_dir = video_temp_dir / "frames"
        
        # Extract frames at configured FPS
        frames = extract_frames_at_interval(
            video_path,
            str(frames_dir),
            fps=settings.FRAME_EXTRACTION_FPS,
            max_frames=settings.MAX_FRAMES_PER_ANALYSIS,
        )
        
        result = {
            "video_id": video_id,
            "status": "completed",
            "frames_dir": str(frames_dir),
            "frame_count": len(frames),
            "interval_ms": settings.FRAME_EXTRACTION_INTERVAL_MS,
            "frames": frames,
        }
        
        logger.info(f"Extracted {len(frames)} frames for video {video_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Frame extraction failed for video {video_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def extract_audio_task(
    self,
    video_id: str,
    video_path: str,
) -> Dict[str, Any]:
    """
    Extract audio from video for analysis.
    
    Args:
        video_id: ID of the video
        video_path: Path to the video file
        
    Returns:
        Audio extraction results
    """
    try:
        logger.info(f"Starting audio extraction for video {video_id}")
        
        # Create temp directory for this video
        temp_dir = ensure_temp_dir()
        video_temp_dir = temp_dir / video_id
        audio_dir = video_temp_dir / "audio"
        
        # Extract audio and create segments
        audio_path, segments = extract_audio_segments(
            video_path,
            str(audio_dir),
            segment_duration_ms=settings.FRAME_EXTRACTION_INTERVAL_MS,
            sample_rate=settings.AUDIO_SAMPLE_RATE,
        )
        
        result = {
            "video_id": video_id,
            "status": "completed",
            "audio_path": audio_path,
            "segment_count": len(segments),
            "segments": segments,
        }
        
        logger.info(f"Extracted audio with {len(segments)} segments for video {video_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Audio extraction failed for video {video_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def analyze_video_patterns(
    self,
    video_id: str,
    video_path: str,
) -> Dict[str, Any]:
    """
    Full video analysis pipeline: extract frames + audio, then analyze with Gemini 2.0.
    
    Args:
        video_id: ID of the video to analyze
        video_path: Path to the video file
        
    Returns:
        Analysis results dictionary with hybrid template
    """
    try:
        logger.info(f"Starting pattern analysis for video {video_id}")
        
        # Create temp directory for this video
        temp_dir = ensure_temp_dir()
        video_temp_dir = temp_dir / video_id
        video_temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Step 1: Get video info
        video_info = get_video_info(video_path)
        logger.info(f"Video info: duration={video_info.get('duration')}s, {video_info.get('width')}x{video_info.get('height')}")
        
        # Step 2: Extract frames at 5fps
        frames_dir = video_temp_dir / "frames"
        frames = extract_frames_at_interval(
            video_path,
            str(frames_dir),
            fps=settings.FRAME_EXTRACTION_FPS,
            max_frames=settings.MAX_FRAMES_PER_ANALYSIS,
        )
        
        # Step 3: Extract audio segments
        audio_dir = video_temp_dir / "audio"
        audio_path, audio_segments = extract_audio_segments(
            video_path,
            str(audio_dir),
            segment_duration_ms=settings.FRAME_EXTRACTION_INTERVAL_MS,
            sample_rate=settings.AUDIO_SAMPLE_RATE,
        )
        
        # Step 4: Analyze with pattern service (will be implemented in pattern_service.py)
        from app.services.pattern_service import PatternService
        
        pattern_service = PatternService(settings.GEMINI_API_KEY)
        template = pattern_service.analyze_video_with_template(
            video_id=video_id,
            frames=frames,
            audio_path=audio_path,
            audio_segments=audio_segments,
            video_info=video_info,
        )
        
        # Step 5: Cleanup temp files
        try:
            shutil.rmtree(video_temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp dir: {e}")
        
        result = {
            "video_id": video_id,
            "status": "completed",
            "template": template,
        }
        
        logger.info(f"Completed pattern analysis for video {video_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Pattern analysis failed for video {video_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def generate_thumbnail(
    self,
    video_id: str,
    video_path: str,
    timestamp: float = 1.0,
) -> Dict[str, Any]:
    """
    Generate thumbnail from video.
    
    Args:
        video_id: ID of the video
        video_path: Path to the video file
        timestamp: Time in seconds to extract thumbnail from
        
    Returns:
        Thumbnail generation result
    """
    try:
        logger.info(f"Generating thumbnail for video {video_id}")
        
        temp_dir = ensure_temp_dir()
        thumbnail_path = temp_dir / f"{video_id}_thumbnail.jpg"
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-ss", str(timestamp),
            "-vframes", "1",
            "-q:v", "2",
            "-y",
            str(thumbnail_path)
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Thumbnail generation failed: {e.stderr.decode()}")
            return {
                "video_id": video_id,
                "status": "failed",
                "error": str(e),
            }
        
        # TODO: Upload to Supabase Storage and get URL
        result = {
            "video_id": video_id,
            "status": "completed",
            "thumbnail_path": str(thumbnail_path),
            "thumbnail_url": None,  # Will be set after upload
        }
        
        logger.info(f"Generated thumbnail for video {video_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Thumbnail generation failed for video {video_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def edit_video(
    self,
    video_id: str,
    video_path: str,
    script_id: Optional[str] = None,
    pattern_ids: Optional[list] = None,
    platform: str = "tiktok",
    output_format: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Edit video based on script or patterns. Uses VideoEditorService.
    """
    try:
        logger.info(f"Starting video editing for video {video_id}")
        import asyncio
        from app.services.video_editor import VideoEditorService

        svc = VideoEditorService()
        # TODO: Load script from DB if script_id; build script dict; call apply_script.
        # TODO: Upload result to storage; create video record.
        output_path = tempfile.mktemp(suffix=".mp4", prefix="edit_")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                svc.create_platform_version(video_path, platform, output_path)
            )
        finally:
            loop.close()
        result = {
            "video_id": video_id,
            "status": "completed",
            "output_video_id": None,
            "output_path": output_path,
        }
        logger.info(f"Completed video editing for video {video_id}")
        return result
    except Exception as exc:
        logger.error(f"Video editing failed for video {video_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def execute_editor_op(
    self,
    video_id: str,
    video_path: str,
    op: str,
    params: Dict[str, Any],
    output_path: str,
) -> Dict[str, Any]:
    """
    Run a single foundation editor op (trim_clip, clip_out, etc.) via VideoEditorService.
    """
    import asyncio
    from app.services.video_editor import VideoEditorService

    try:
        logger.info(f"Running editor op {op} for video {video_id}")
        svc = VideoEditorService()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if op == "trim_clip":
                loop.run_until_complete(
                    svc.trim_clip(video_path, float(params["start"]), float(params["end"]), output_path)
                )
            elif op == "clip_out":
                loop.run_until_complete(
                    svc.clip_out(video_path, float(params["start"]), float(params["end"]), output_path)
                )
            elif op == "duplicate_clip":
                loop.run_until_complete(svc.duplicate_clip(video_path, output_path))
            elif op == "set_clip_speed":
                loop.run_until_complete(
                    svc.set_clip_speed(video_path, float(params.get("speed", 1)), output_path)
                )
            elif op == "reverse_clip":
                loop.run_until_complete(svc.reverse_clip(video_path, output_path))
            elif op == "export_video":
                loop.run_until_complete(
                    svc.export_video(
                        video_path,
                        output_path,
                        width=params.get("width"),
                        height=params.get("height"),
                        fps=params.get("fps"),
                        bitrate=params.get("bitrate"),
                    )
                )
            else:
                raise ValueError(f"Unsupported op: {op}")
        finally:
            loop.close()
        return {"video_id": video_id, "op": op, "output_path": output_path, "status": "completed"}
    except Exception as exc:
        logger.error(f"Editor op {op} failed for {video_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def extract_video_metadata(
    self,
    video_id: str,
    video_path: str,
) -> Dict[str, Any]:
    """
    Extract metadata from video file using ffprobe.
    
    Args:
        video_id: ID of the video
        video_path: Path to the video file
        
    Returns:
        Extracted metadata
    """
    try:
        logger.info(f"Extracting metadata for video {video_id}")
        
        metadata = get_video_info(video_path)
        
        result = {
            "video_id": video_id,
            "status": "completed",
            "metadata": metadata,
        }
        
        logger.info(f"Extracted metadata for video {video_id}")
        return result
        
    except Exception as exc:
        logger.error(f"Metadata extraction failed for video {video_id}: {exc}")
        raise self.retry(exc=exc)


def cleanup_video_temp_files(video_id: str) -> bool:
    """
    Clean up temporary files for a video.
    
    Args:
        video_id: ID of the video
        
    Returns:
        True if cleanup succeeded
    """
    try:
        temp_dir = ensure_temp_dir()
        video_temp_dir = temp_dir / video_id
        
        if video_temp_dir.exists():
            shutil.rmtree(video_temp_dir)
            logger.info(f"Cleaned up temp files for video {video_id}")
            return True
        
        return False
    except Exception as e:
        logger.error(f"Failed to cleanup temp files for video {video_id}: {e}")
        return False

