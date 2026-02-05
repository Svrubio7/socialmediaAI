"""
Video editing service backed by FFmpeg/FFprobe.
Provides timeline, transform, overlay and export primitives.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class VideoEditorService:
    """Service for editing videos using FFmpeg."""

    def __init__(self, temp_dir: Optional[str] = None):
        self.temp_dir = temp_dir or tempfile.gettempdir()

    # ---------- Internal helpers ----------

    def _run_command(self, cmd: List[str]) -> None:
        """Run subprocess command and raise readable errors."""
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("FFmpeg/FFprobe is not installed in runtime image") from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            if len(stderr) > 500:
                stderr = stderr[:500] + "..."
            raise RuntimeError(stderr or "Video processing command failed") from exc

    def _has_audio_stream(self, media_path: str) -> bool:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            media_path,
        ]
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return bool((result.stdout or "").strip())
        except Exception:
            return False

    def _overlay_position(self, position: str) -> Tuple[str, str]:
        p = (position or "center").strip().lower()
        if p == "center":
            return "(main_w-overlay_w)/2", "(main_h-overlay_h)/2"
        if p == "top":
            return "(main_w-overlay_w)/2", "40"
        if p == "bottom":
            return "(main_w-overlay_w)/2", "main_h-overlay_h-40"
        if p == "top_left":
            return "40", "40"
        if p == "top_right":
            return "main_w-overlay_w-40", "40"
        if p == "bottom_left":
            return "40", "main_h-overlay_h-40"
        if p == "bottom_right":
            return "main_w-overlay_w-40", "main_h-overlay_h-40"

        # Allow raw "x,y" expression.
        if "," in p:
            xs, ys = p.split(",", 1)
            return xs.strip(), ys.strip()

        return "(main_w-overlay_w)/2", "(main_h-overlay_h)/2"

    def _escape_drawtext(self, value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace(":", "\\:")
            .replace("'", "\\'")
            .replace("%", "\\%")
        )

    # ---------- Legacy scripting hooks ----------

    async def apply_script(
        self,
        input_path: str,
        script: Dict[str, Any],
        output_path: str,
    ) -> str:
        """
        Apply script instructions to create edited video.
        Current implementation executes the first translated command.
        """
        commands = self._script_to_ffmpeg_commands(script, input_path, output_path)
        if not commands:
            raise RuntimeError("Script did not produce FFmpeg commands")
        self._run_command(commands[0])
        return output_path

    def _script_to_ffmpeg_commands(
        self,
        script: Dict[str, Any],
        input_path: str,
        output_path: str,
    ) -> List[List[str]]:
        """Convert script instructions to FFmpeg commands."""
        _ = script
        return [["ffmpeg", "-y", "-i", input_path, "-map", "0:v", "-map", "0:a?", "-c", "copy", output_path]]

    # ---------- Platform/export ----------

    async def create_platform_version(
        self,
        input_path: str,
        platform: str,
        output_path: str,
    ) -> str:
        """Create platform-specific version (resolution, fps, bitrate, max duration)."""
        platform_specs = {
            "tiktok": {"width": 1080, "height": 1920, "max_duration": 60, "fps": 30, "bitrate": "4M"},
            "instagram": {"width": 1080, "height": 1920, "max_duration": 90, "fps": 30, "bitrate": "4M"},
            "youtube_shorts": {"width": 1080, "height": 1920, "max_duration": 60, "fps": 30, "bitrate": "6M"},
            "youtube": {"width": 1920, "height": 1080, "max_duration": None, "fps": 30, "bitrate": "8M"},
            "facebook": {"width": 1080, "height": 1920, "max_duration": 120, "fps": 30, "bitrate": "4M"},
        }
        specs = platform_specs.get(platform.lower(), platform_specs["instagram"])

        vf = (
            f"scale={specs['width']}:{specs['height']}:force_original_aspect_ratio=decrease,"
            f"pad={specs['width']}:{specs['height']}:(ow-iw)/2:(oh-ih)/2"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            vf,
            "-r",
            str(specs["fps"]),
            "-b:v",
            specs["bitrate"],
        ]
        if specs["max_duration"] is not None:
            cmd += ["-t", str(specs["max_duration"])]
        cmd += ["-map", "0:v", "-map", "0:a?", "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", "-movflags", "+faststart", output_path]
        self._run_command(cmd)
        return output_path

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
        """Render to file with optional format, dimensions, fps and bitrate."""
        if format and not output_path.lower().endswith(f".{format.lower()}"):
            output_path = str(Path(output_path).with_suffix(f".{format.lower()}"))

        cmd = ["ffmpeg", "-y", "-i", input_path]
        vf: List[str] = []
        if width and height:
            vf.append(
                f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
            )
        if vf:
            cmd += ["-vf", ",".join(vf)]
        if fps:
            cmd += ["-r", str(fps)]
        if bitrate:
            cmd += ["-b:v", str(bitrate)]

        cmd += ["-map", "0:v", "-map", "0:a?", "-c:v", "libx264", "-preset", "fast", "-c:a", "aac", "-movflags", "+faststart", output_path]
        self._run_command(cmd)
        return output_path

    # ---------- Metadata ----------

    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video metadata using ffprobe."""
        cmd = [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
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

    # ---------- Timeline ops ----------

    async def extract_segment(
        self,
        input_path: str,
        start_time: float,
        end_time: float,
        output_path: str,
    ) -> str:
        duration = max(0.01, end_time - start_time)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-ss",
            str(start_time),
            "-t",
            str(duration),
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c",
            "copy",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def clip_out(self, input_path: str, start: float, end: float, output_path: str) -> str:
        """Remove segment [start, end]; output = before + after concatenated."""
        info = await self.get_video_info(input_path)
        dur = float(info.get("duration") or 0)
        if start <= 0 and end >= dur:
            raise ValueError("clip_out would remove entire video")

        before = output_path + ".before.mp4"
        after = output_path + ".after.mp4"
        parts: List[str] = []

        if start > 0:
            await self.extract_segment(input_path, 0.0, start, before)
            parts.append(before)
        if end < dur:
            await self.extract_segment(input_path, end, dur, after)
            parts.append(after)

        if len(parts) == 1:
            shutil.move(parts[0], output_path)
            return output_path

        await self.merge_clips(parts, output_path)
        for p in parts:
            try:
                os.remove(p)
            except OSError:
                pass
        return output_path

    async def trim_clip(self, input_path: str, start: float, end: float, output_path: str) -> str:
        return await self.extract_segment(input_path, start, end, output_path)

    async def split_clip(
        self,
        input_path: str,
        split_at: float,
        output_left: str,
        output_right: str,
    ) -> Tuple[str, str]:
        info = await self.get_video_info(input_path)
        dur = float(info.get("duration") or 0)
        await self.extract_segment(input_path, 0.0, split_at, output_left)
        await self.extract_segment(input_path, split_at, dur, output_right)
        return (output_left, output_right)

    async def duplicate_clip(self, input_path: str, output_path: str) -> str:
        shutil.copy2(input_path, output_path)
        return output_path

    async def merge_clips(self, input_paths: List[str], output_path: str) -> str:
        list_path = output_path + ".list"
        with open(list_path, "w", encoding="utf-8") as f:
            for p in input_paths:
                ab = os.path.abspath(p).replace("\\", "/")
                f.write(f"file '{ab}'\\n")

        cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", output_path]
        self._run_command(cmd)

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
        """Replace [segment_start, segment_end] with replacement clip."""
        info = await self.get_video_info(timeline_path)
        dur = float(info.get("duration") or 0)

        before = output_path + ".before.mp4"
        after = output_path + ".after.mp4"
        parts: List[str] = []

        if segment_start > 0:
            await self.extract_segment(timeline_path, 0.0, segment_start, before)
            parts.append(before)

        parts.append(replacement_path)

        if segment_end < dur:
            await self.extract_segment(timeline_path, segment_end, dur, after)
            parts.append(after)

        await self.merge_clips(parts, output_path)

        for p in [before, after]:
            try:
                if os.path.exists(p):
                    os.remove(p)
            except OSError:
                pass

        return output_path

    # ---------- Transform ops ----------

    async def crop_clip(
        self,
        input_path: str,
        x: int,
        y: int,
        width: int,
        height: int,
        output_path: str,
    ) -> str:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            f"crop={width}:{height}:{x}:{y}",
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def rotate_clip(self, input_path: str, degrees: float, output_path: str) -> str:
        if abs(degrees - 90) < 1:
            vf = "transpose=1"
        elif abs(degrees - 270) < 1:
            vf = "transpose=2"
        elif abs(degrees - 180) < 1:
            vf = "transpose=2,transpose=2"
        else:
            vf = f"rotate={degrees}*PI/180"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            vf,
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def mirror_clip(self, input_path: str, horizontal: bool, output_path: str) -> str:
        vf = "hflip" if horizontal else "vflip"
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            vf,
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def set_clip_speed(self, input_path: str, speed: float, output_path: str) -> str:
        return await self.adjust_speed(input_path, speed, output_path)

    async def adjust_speed(
        self,
        input_path: str,
        speed_factor: float,
        output_path: str,
    ) -> str:
        speed_factor = max(0.25, min(4.0, float(speed_factor)))
        setpts = 1.0 / speed_factor
        vf = f"setpts={setpts}*PTS"

        cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", vf]

        if self._has_audio_stream(input_path):
            t = speed_factor
            atempos: List[str] = []
            while t > 2:
                atempos.append("atempo=2")
                t /= 2
            while t < 0.5:
                atempos.append("atempo=0.5")
                t /= 0.5
            atempos.append(f"atempo={t}")
            cmd += ["-af", ",".join(atempos), "-c:a", "aac"]
        else:
            cmd += ["-an"]

        cmd += ["-c:v", "libx264", "-preset", "fast", output_path]
        self._run_command(cmd)
        return output_path

    async def reverse_clip(self, input_path: str, output_path: str) -> str:
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", "reverse"]
        if self._has_audio_stream(input_path):
            cmd += ["-af", "areverse", "-c:a", "aac"]
        else:
            cmd += ["-an"]
        cmd += ["-c:v", "libx264", "-preset", "fast", output_path]
        self._run_command(cmd)
        return output_path

    async def freeze_frame(
        self,
        input_path: str,
        at_time: float,
        duration: float,
        output_path: str,
    ) -> str:
        """Insert freeze frame at at_time for duration seconds."""
        info = await self.get_video_info(input_path)
        total = float(info.get("duration") or 0)
        if total <= 0:
            raise ValueError("Input video has invalid duration")

        at_time = max(0.0, min(float(at_time), max(0.0, total - 0.04)))
        duration = max(0.05, float(duration))
        frame_end = min(total, at_time + 0.04)

        if self._has_audio_stream(input_path):
            fc = (
                f"[0:v]trim=0:{at_time},setpts=PTS-STARTPTS[v0];"
                f"[0:v]trim=start={at_time}:end={frame_end},setpts=PTS-STARTPTS,"
                f"tpad=stop_mode=clone:stop_duration={duration}[v1];"
                f"[0:v]trim=start={at_time},setpts=PTS-STARTPTS[v2];"
                f"[v0][v1][v2]concat=n=3:v=1:a=0[v];"
                f"[0:a]atrim=0:{at_time},asetpts=PTS-STARTPTS[a0];"
                f"aevalsrc=0:d={duration}[asil];"
                f"[0:a]atrim=start={at_time},asetpts=PTS-STARTPTS[a2];"
                f"[a0][asil][a2]concat=n=3:v=0:a=1[a]"
            )
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-filter_complex",
                fc,
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                output_path,
            ]
        else:
            fc = (
                f"[0:v]trim=0:{at_time},setpts=PTS-STARTPTS[v0];"
                f"[0:v]trim=start={at_time}:end={frame_end},setpts=PTS-STARTPTS,"
                f"tpad=stop_mode=clone:stop_duration={duration}[v1];"
                f"[0:v]trim=start={at_time},setpts=PTS-STARTPTS[v2];"
                f"[v0][v1][v2]concat=n=3:v=1:a=0[v]"
            )
            cmd = [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-filter_complex",
                fc,
                "-map",
                "[v]",
                "-an",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-movflags",
                "+faststart",
                output_path,
            ]

        self._run_command(cmd)
        return output_path

    async def set_canvas_size(
        self,
        input_path: str,
        width: int,
        height: int,
        output_path: str,
    ) -> str:
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2",
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def adjust_color(
        self,
        input_path: str,
        brightness: float,
        contrast: float,
        saturation: float,
        gamma: float,
        output_path: str,
    ) -> str:
        """Apply color correction similar to filter/tone tools."""
        eq = (
            f"eq=brightness={float(brightness)}:"
            f"contrast={float(contrast)}:"
            f"saturation={float(saturation)}:"
            f"gamma={float(gamma)}"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            eq,
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def fade_in_out(
        self,
        input_path: str,
        fade_in: float,
        fade_out: float,
        output_path: str,
    ) -> str:
        """Apply fade-in/fade-out transitions to clip edges."""
        info = await self.get_video_info(input_path)
        duration = float(info.get("duration") or 0)
        fade_in = max(0.0, float(fade_in))
        fade_out = max(0.0, float(fade_out))
        fade_out_start = max(0.0, duration - fade_out)

        vf = f"fade=t=in:st=0:d={fade_in},fade=t=out:st={fade_out_start}:d={fade_out}"
        cmd = ["ffmpeg", "-y", "-i", input_path, "-vf", vf]

        if self._has_audio_stream(input_path):
            af = f"afade=t=in:st=0:d={fade_in},afade=t=out:st={fade_out_start}:d={fade_out}"
            cmd += ["-af", af, "-c:a", "aac"]
        else:
            cmd += ["-an"]

        cmd += ["-c:v", "libx264", "-preset", "fast", output_path]
        self._run_command(cmd)
        return output_path

    # ---------- Overlay/media ops ----------

    async def add_text_overlay(
        self,
        input_path: str,
        text: str,
        position: str = "center",
        start_time: float = 0,
        end_time: Optional[float] = None,
        output_path: str = "",
    ) -> str:
        output = output_path or input_path.replace(".mp4", "_text.mp4")
        x_expr, y_expr = self._overlay_position(position)
        esc_text = self._escape_drawtext(text)

        if end_time is not None:
            enable = f"between(t,{max(0.0, float(start_time))},{max(float(end_time), float(start_time))})"
        else:
            enable = f"gte(t,{max(0.0, float(start_time))})"

        drawtext = (
            "drawtext="
            f"text='{esc_text}':"
            "fontcolor=white:fontsize=48:"
            "box=1:boxcolor=black@0.35:boxborderw=10:"
            f"x={x_expr}:y={y_expr}:"
            f"enable='{enable}'"
        )

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-vf",
            drawtext,
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output,
        ]
        self._run_command(cmd)
        return output

    async def insert_video(
        self,
        base_path: str,
        overlay_path: str,
        at_time: float,
        position: str,
        output_path: str,
    ) -> str:
        x_expr, y_expr = self._overlay_position(position)
        enable = f"gte(t,{max(0.0, float(at_time))})"
        fc = f"[1:v]setpts=PTS-STARTPTS+{max(0.0, float(at_time))}/TB[ov];[0:v][ov]overlay={x_expr}:{y_expr}:enable='{enable}'[v]"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            base_path,
            "-i",
            overlay_path,
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            output_path,
        ]
        self._run_command(cmd)
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
        x_expr, y_expr = self._overlay_position(position)
        start = max(0.0, float(at_time))
        end = max(start + 0.05, start + float(duration))
        fc = f"[1:v]format=rgba[ov];[0:v][ov]overlay={x_expr}:{y_expr}:enable='between(t,{start},{end})'[v]"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-loop",
            "1",
            "-i",
            image_path,
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            "-shortest",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def insert_audio(
        self,
        video_path: str,
        audio_path: str,
        at_time: float,
        volume: float,
        output_path: str,
    ) -> str:
        if not self._has_audio_stream(audio_path):
            raise ValueError("Provided audio file has no audio stream")

        delay_ms = max(0, int(float(at_time) * 1000))
        gain = max(0.0, float(volume))

        if self._has_audio_stream(video_path):
            fc = (
                f"[1:a]volume={gain},adelay={delay_ms}:all=1[a1];"
                "[0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[a]"
            )
        else:
            fc = f"[1:a]volume={gain},adelay={delay_ms}:all=1[a]"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-filter_complex",
            fc,
            "-map",
            "0:v",
            "-map",
            "[a]",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-shortest",
            output_path,
        ]
        self._run_command(cmd)
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
        start = max(0.0, float(at_time))
        end = max(start + 0.05, start + float(duration))
        fc = f"[1:v]format=rgba[ov];[0:v][ov]overlay={int(x)}:{int(y)}:enable='between(t,{start},{end})'[v]"

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            input_path,
            "-loop",
            "1",
            "-i",
            image_path,
            "-filter_complex",
            fc,
            "-map",
            "[v]",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-c:a",
            "copy",
            "-shortest",
            output_path,
        ]
        self._run_command(cmd)
        return output_path

    async def reorder_layers(self, project_or_path: str, layer_order: List[str]) -> Dict[str, Any]:
        _ = project_or_path
        return {"layers": layer_order}

    async def set_layer_visibility(
        self,
        project_or_path: str,
        layer_id: str,
        visible: bool,
    ) -> Dict[str, Any]:
        _ = project_or_path
        return {"layer_id": layer_id, "visible": visible}
