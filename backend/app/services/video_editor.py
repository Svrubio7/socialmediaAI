"""
Video Editing Service - Uses FFmpeg for video processing.
Foundation ops (clip, transform, overlay, etc.) used by UI and MCP.
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import subprocess
import os
import tempfile
import shutil


class VideoEditorService:
    """Service for editing videos using FFmpeg."""

    def __init__(self, temp_dir: Optional[str] = None):
        """Initialize the video editor service."""
        self.temp_dir = temp_dir or tempfile.gettempdir()

    async def apply_script(
        self,
        input_path: str,
        script: Dict[str, Any],
        output_path: str,
    ) -> str:
        """
        Apply script instructions to create edited video.
        
        Args:
            input_path: Path to source video
            script: Script with editing instructions
            output_path: Path for output video
            
        Returns:
            Path to the edited video
        """
        # TODO: Implement actual video editing
        # Parse script and generate FFmpeg commands
        commands = self._script_to_ffmpeg_commands(script, input_path, output_path)
        
        # Execute FFmpeg commands
        # for cmd in commands:
        #     subprocess.run(cmd, check=True)
        
        return output_path

    def _script_to_ffmpeg_commands(
        self,
        script: Dict[str, Any],
        input_path: str,
        output_path: str,
    ) -> List[List[str]]:
        """Convert script instructions to FFmpeg commands."""
        commands = []
        
        # Base command structure
        base_cmd = ["ffmpeg", "-i", input_path]
        
        # Add filters based on script
        filters = []
        
        # Process segments
        for segment in script.get("segments", []):
            start_time = segment.get("start_time", 0)
            end_time = segment.get("end_time", 0)
            
            # Add text overlays if specified
            if segment.get("text_overlay"):
                text = segment["text_overlay"]
                # filters.append(f"drawtext=text='{text}':fontsize=24:fontcolor=white:x=(w-text_w)/2:y=h-50:enable='between(t,{start_time},{end_time})'")
        
        # Build final command
        cmd = base_cmd.copy()
        if filters:
            cmd.extend(["-vf", ",".join(filters)])
        cmd.extend(["-y", output_path])
        
        commands.append(cmd)
        
        return commands

    async def create_platform_version(
        self,
        input_path: str,
        platform: str,
        output_path: str,
    ) -> str:
        """
        Create platform-specific video version.
        
        Args:
            input_path: Path to source video
            platform: Target platform
            output_path: Path for output video
            
        Returns:
            Path to the platform-optimized video
        """
        platform_specs = {
            "tiktok": {
                "width": 1080,
                "height": 1920,
                "max_duration": 60,
                "fps": 30,
                "bitrate": "4M"
            },
            "instagram": {
                "width": 1080,
                "height": 1920,
                "max_duration": 90,
                "fps": 30,
                "bitrate": "4M"
            },
            "youtube_shorts": {
                "width": 1080,
                "height": 1920,
                "max_duration": 60,
                "fps": 30,
                "bitrate": "6M"
            },
            "youtube": {
                "width": 1920,
                "height": 1080,
                "max_duration": None,
                "fps": 30,
                "bitrate": "8M"
            },
            "facebook": {
                "width": 1080,
                "height": 1920,
                "max_duration": 120,
                "fps": 30,
                "bitrate": "4M"
            }
        }
        
        specs = platform_specs.get(platform.lower(), platform_specs["instagram"])
        
        # TODO: Implement actual platform conversion
        # cmd = [
        #     "ffmpeg", "-i", input_path,
        #     "-vf", f"scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2",
        #     "-r", str(specs['fps']),
        #     "-b:v", specs['bitrate'],
        #     "-y", output_path
        # ]
        # subprocess.run(cmd, check=True)
        
        return output_path

    async def extract_segment(
        self,
        input_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
    ) -> str:
        """
        Extract a segment from a video.
        
        Args:
            input_path: Path to source video
            start_time: Start time in seconds
            end_time: End time in seconds
            output_path: Path for output segment
            
        Returns:
            Path to the extracted segment
        """
        duration = end_time - start_time
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy",
            output_path,
        ]
        subprocess.run(cmd, check=True)
        return output_path

    async def add_text_overlay(
        self,
        input_path: str,
        text: str,
        position: str = "center",
        start_time: float = 0,
        end_time: Optional[float] = None,
        output_path: str = None,
    ) -> str:
        """
        Add text overlay to video.
        
        Args:
            input_path: Path to source video
            text: Text to overlay
            position: Position (center, top, bottom)
            start_time: Start time for text
            end_time: End time for text (None for entire video)
            output_path: Path for output video
            
        Returns:
            Path to the video with text overlay
        """
        # TODO: Implement actual text overlay
        output = output_path or input_path.replace(".mp4", "_text.mp4")
        
        positions = {
            "center": "x=(w-text_w)/2:y=(h-text_h)/2",
            "top": "x=(w-text_w)/2:y=50",
            "bottom": "x=(w-text_w)/2:y=h-50"
        }
        
        pos = positions.get(position, positions["center"])
        
        return output

    async def adjust_speed(
        self,
        input_path: str,
        speed_factor: float,
        output_path: str,
    ) -> str:
        """
        Adjust video playback speed.
        
        Args:
            input_path: Path to source video
            speed_factor: Speed multiplier (2.0 = 2x faster, 0.5 = half speed)
            output_path: Path for output video
            
        Returns:
            Path to the speed-adjusted video
        """
        setpts = 1.0 / speed_factor
        vf = f"setpts={setpts}*PTS"
        t = speed_factor
        atempos: List[str] = []
        while t > 2:
            atempos.append("atempo=2")
            t /= 2
        while t < 0.5:
            atempos.append("atempo=0.5")
            t /= 0.5
        atempos.append(f"atempo={t}")
        af = ",".join(atempos)
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "fast", output_path]
        subprocess.run(cmd, check=True)
        return output_path

    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video metadata using ffprobe.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video metadata
        """
        cmd = [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format", "-show_streams",
            video_path,
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)
        except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
            return {"duration": 0, "width": 0, "height": 0, "fps": 0, "codec": "", "bitrate": 0}
        vs = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
        fmt = data.get("format", {})
        rfr = vs.get("r_frame_rate") or "0/1"
        a, b = (int(x) for x in rfr.split("/")) if "/" in rfr else (0, 1)
        fps = (a / b) if b else 0
        return {
            "duration": float(fmt.get("duration", 0)),
            "width": int(vs.get("width", 0)),
            "height": int(vs.get("height", 0)),
            "fps": fps,
            "codec": vs.get("codec_name", ""),
            "bitrate": int(fmt.get("bit_rate", 0)),
        }

    # --- Foundation ops (Phase 2): used by UI and MCP ---

    async def clip_out(self, input_path: str, start: float, end: float, output_path: str) -> str:
        """Remove segment [start, end]; output = before + after concatenated."""
        info = await self.get_video_info(input_path)
        dur = info.get("duration") or 0.0
        if start <= 0 and end >= dur:
            raise ValueError("clip_out would remove entire video")
        before = output_path + ".before.mp4"
        after = output_path + ".after.mp4"
        paths: List[str] = []
        if start > 0:
            await self.extract_segment(input_path, 0.0, start, before)
            paths.append(before)
        if end < dur:
            await self.extract_segment(input_path, end, dur, after)
            paths.append(after)
        if len(paths) == 1:
            shutil.move(paths[0], output_path)
            return output_path
        await self.merge_clips(paths, output_path)
        for p in paths:
            try:
                os.remove(p)
            except OSError:
                pass
        return output_path

    async def trim_clip(self, input_path: str, start: float, end: float, output_path: str) -> str:
        """Trim to [start, end]. Same as extract segment."""
        return await self.extract_segment(input_path, start, end, output_path)

    async def split_clip(
        self,
        input_path: str,
        split_at: float,
        output_left: str,
        output_right: str,
    ) -> Tuple[str, str]:
        """Split at split_at; output two clips."""
        info = await self.get_video_info(input_path)
        dur = info.get("duration") or 0.0
        await self.extract_segment(input_path, 0.0, split_at, output_left)
        await self.extract_segment(input_path, split_at, dur, output_right)
        return (output_left, output_right)

    async def duplicate_clip(self, input_path: str, output_path: str) -> str:
        """Copy clip to output_path."""
        shutil.copy2(input_path, output_path)
        return output_path

    async def merge_clips(self, input_paths: List[str], output_path: str) -> str:
        """Concatenate clips in order."""
        list_path = output_path + ".list"
        with open(list_path, "w") as f:
            for p in input_paths:
                ab = os.path.abspath(p).replace("\\", "/")
                f.write(f"file '{ab}'\n")
        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", output_path]
        subprocess.run(cmd, check=True)
        try:
            os.remove(list_path)
        except OSError:
            pass
        return output_path

    async def replace_clip(
        self,
        timeline_path: str,
        segment_start: float,
        segment_end: float,
        replacement_path: str,
        output_path: str,
    ) -> str:
        """Replace segment [start, end] with replacement clip. Stub: use clip_out + insert + merge."""
        # TODO: extract before, replacement, after; merge_clips
        return output_path

    async def crop_clip(
        self,
        input_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str,
    ) -> str:
        """Crop to region (x,y,width,height)."""
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"crop={width}:{height}:{x}:{y}",
            "-c:a", "copy",
            output_path,
        ]
        subprocess.run(cmd, check=True)
        return output_path

    async def rotate_clip(self, input_path: str, degrees: float, output_path: str) -> str:
        """Rotate clip (90, 180, 270 or arbitrary)."""
        if abs(degrees - 90) < 1:
            vf = "transpose=1"
        elif abs(degrees - 270) < 1:
            vf = "transpose=2"
        elif abs(degrees - 180) < 1:
            vf = "transpose=2,transpose=2"
        else:
            vf = f"rotate={degrees}*PI/180"
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", vf, "-c:a", "copy", output_path]
        subprocess.run(cmd, check=True)
        return output_path

    async def mirror_clip(self, input_path: str, horizontal: bool, output_path: str) -> str:
        """Flip horizontal or vertical."""
        vf = "hflip" if horizontal else "vflip"
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", vf, "-c:a", "copy", output_path]
        subprocess.run(cmd, check=True)
        return output_path

    async def set_clip_speed(self, input_path: str, speed: float, output_path: str) -> str:
        """Uniform speed change (0.25--4)."""
        return await self.adjust_speed(input_path, speed, output_path)

    async def reverse_clip(self, input_path: str, output_path: str) -> str:
        """Reverse playback."""
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", "reverse", "-af", "areverse", output_path]
        subprocess.run(cmd, check=True)
        return output_path

    async def freeze_frame(
        self,
        input_path: str,
        at_time: float,
        duration: float,
        output_path: str,
    ) -> str:
        """Hold frame at at_time for duration seconds."""
        # Extract frame, create still clip, splice. Stub: output = input for now.
        shutil.copy2(input_path, output_path)
        return output_path

    async def set_canvas_size(
        self,
        input_path: str,
        width: int,
        height: int,
        output_path: str,
    ) -> str:
        """Scale and pad to target canvas (aspect ratio preserved)."""
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-c:a", "copy",
            output_path,
        ]
        subprocess.run(cmd, check=True)
        return output_path

    async def insert_video(
        self,
        base_path: str,
        overlay_path: str,
        at_time: float,
        position: str,
        output_path: str,
    ) -> str:
        """Overlay video at at_time, position (e.g. center, top-right). Stub."""
        # TODO: overlay filter with enable='between(t,...)'
        shutil.copy2(base_path, output_path)
        return output_path

    async def insert_image(
        self,
        input_path: str,
        image_path: str,
        at_time: float,
        duration: float,
        position: str,
        output_path: str,
    ) -> str:
        """Overlay image at position for duration. Stub."""
        shutil.copy2(input_path, output_path)
        return output_path

    async def insert_audio(
        self,
        video_path: str,
        audio_path: str,
        at_time: float,
        volume: float,
        output_path: str,
    ) -> str:
        """Mix in audio at at_time. Stub."""
        shutil.copy2(video_path, output_path)
        return output_path

    async def add_sticker(
        self,
        input_path: str,
        image_path: str,
        at_time: float,
        duration: float,
        x: int,
        y: int,
        output_path: str,
    ) -> str:
        """Overlay sticker at (x,y). Stub."""
        shutil.copy2(input_path, output_path)
        return output_path

    async def reorder_layers(self, project_or_path: str, layer_order: List[str]) -> Dict[str, Any]:
        """Reorder layers (project-level). Stub; returns current state."""
        return {"layers": layer_order}

    async def set_layer_visibility(
        self,
        project_or_path: str,
        layer_id: str,
        visible: bool,
    ) -> Dict[str, Any]:
        """Set layer visibility. Stub."""
        return {"layer_id": layer_id, "visible": visible}

    async def export_video(
        self,
        input_path: str,
        output_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fps: Optional[float] = None,
        bitrate: Optional[str] = None,
        format: str = "mp4",
    ) -> str:
        """Render to file. Optional resolution, fps, bitrate."""
        args = ["ffmpeg", "-y", "-i", input_path]
        vf: List[str] = []
        if width and height:
            vf.append(f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2")
        if vf:
            args += ["-vf", ",".join(vf)]
        if fps:
            args += ["-r", str(fps)]
        if bitrate:
            args += ["-b:v", bitrate]
        args += ["-c:a", "copy", output_path]
        subprocess.run(args, check=True)
        return output_path
