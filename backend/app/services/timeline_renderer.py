"""
Timeline renderer for editor projects.
Builds a base video track, then applies graphics and audio layers.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageColor, ImageDraw


def _as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None:
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def _clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def _hex_to_ffmpeg_color(color: str, alpha: float = 1.0) -> str:
    """Convert hex/rgb color string to ffmpeg-compatible color."""
    if not color:
        return f"black@{alpha}"
    c = color.strip().lower()
    if c.startswith("rgb(") and c.endswith(")"):
        parts = c[4:-1].split(",")
        if len(parts) >= 3:
            r, g, b = [int(p.strip()) for p in parts[:3]]
            return f"0x{r:02x}{g:02x}{b:02x}@{alpha}"
    if c.startswith("rgba(") and c.endswith(")"):
        parts = c[5:-1].split(",")
        if len(parts) >= 4:
            r, g, b = [int(p.strip()) for p in parts[:3]]
            a = float(parts[3].strip())
            return f"0x{r:02x}{g:02x}{b:02x}@{_clamp(a, 0.0, 1.0)}"
    if c.startswith("#"):
        c = c[1:]
    if len(c) == 3:
        c = "".join([ch * 2 for ch in c])
    if len(c) == 6:
        return f"0x{c}@{_clamp(alpha, 0.0, 1.0)}"
    return f"{color}@{_clamp(alpha, 0.0, 1.0)}"


def _build_interp_expr(frames: List[Tuple[float, float]], default_value: float) -> str:
    if not frames:
        return str(default_value)
    frames = sorted(frames, key=lambda item: item[0])
    expr = str(default_value)
    for i in range(len(frames) - 1):
        t0, v0 = frames[i]
        t1, v1 = frames[i + 1]
        if abs(t1 - t0) < 0.0001:
            continue
        expr = (
            f"if(between(t,{t0:.3f},{t1:.3f}),"
            f"{v0:.4f}+({v1 - v0:.4f})*(t-{t0:.3f})/({t1 - t0:.3f}),{expr})"
        )
    last_t, last_v = frames[-1]
    expr = f"if(gte(t,{last_t:.3f}),{last_v:.4f},{expr})"
    return expr


def _quote_expr(expr: str) -> str:
    return f"'{expr}'"


def _ffprobe_info(path: str) -> Dict[str, Any]:
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except Exception:
        return {}
    streams = data.get("streams", [])
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
    fmt = data.get("format", {})
    rfr = video_stream.get("r_frame_rate") or "0/1"
    if "/" in rfr:
        num, den = rfr.split("/", 1)
        try:
            fps = float(num) / float(den) if float(den) else 0
        except Exception:
            fps = 0
    else:
        fps = _as_float(rfr, 0.0)
    return {
        "duration": _as_float(fmt.get("duration"), 0.0),
        "width": _as_int(video_stream.get("width"), 0),
        "height": _as_int(video_stream.get("height"), 0),
        "fps": fps,
    }


def _has_audio_stream(path: str) -> bool:
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
        path,
    ]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return bool((result.stdout or "").strip())
    except Exception:
        return False


def _atempo_chain(speed: float) -> str:
    speed = _clamp(speed, 0.25, 4.0)
    parts: List[str] = []
    while speed > 2:
        parts.append("atempo=2.0")
        speed /= 2.0
    while speed < 0.5:
        parts.append("atempo=0.5")
        speed /= 0.5
    parts.append(f"atempo={speed:.3f}")
    return ",".join(parts)


PRESET_SPECS: Dict[str, Dict[str, Any]] = {
    "tiktok": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "4M"},
    "instagram": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "4M"},
    "reels": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "4M"},
    "youtube_shorts": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "6M"},
    "youtube": {"width": 1920, "height": 1080, "fps": 30, "bitrate": "8M"},
    "facebook": {"width": 1080, "height": 1920, "fps": 30, "bitrate": "4M"},
}


def _normalize_transition(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    key = str(name).strip().lower()
    mapping = {
        "cross fade": "fade",
        "crossfade": "fade",
        "fade": "fade",
        "hard wipe": "wipeleft",
        "hard wipe left": "wipeleft",
        "hard wipe right": "wipeleft",
        "hard wipe up": "wipeleft",
        "hard wipe down": "wipeleft",
        "wipe left": "wipeleft",
        "wipe right": "wipeleft",
        "wipe up": "wipeleft",
        "wipe down": "wipeleft",
    }
    return mapping.get(key)


class TimelineRenderer:
    def __init__(self, storage, temp_root: Optional[str] = None) -> None:
        self.storage = storage
        self.temp_root = Path(temp_root or tempfile.gettempdir()).resolve()
        self.temp_root.mkdir(parents=True, exist_ok=True)
        self.last_debug_trace: Dict[str, Any] = {}

    def _run(self, cmd: List[str]) -> None:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except FileNotFoundError as exc:
            raise RuntimeError("FFmpeg/FFprobe is not installed in runtime image") from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or "").strip()
            if len(stderr) > 500:
                stderr = stderr[:500] + "..."
            raise RuntimeError(stderr or "Video processing command failed") from exc

    def _scale_filter(self, fit_mode: str, width: int, height: int) -> str:
        if not width or not height:
            return ""
        mode = (fit_mode or "fit").lower()
        if mode == "fill":
            return f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}"
        if mode == "stretch":
            return f"scale={width}:{height}"
        return (
            f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
        )

    def _render_blank_segment(self, duration: float, settings: Dict[str, Any], output_path: str) -> None:
        width = int(settings["width"])
        height = int(settings["height"])
        fps = settings.get("fps") or 30
        bitrate = settings.get("bitrate")
        duration = max(0.05, float(duration))
        cmd = [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"color=c=black:s={width}x{height}:r={fps}:d={duration}",
            "-f",
            "lavfi",
            "-i",
            f"anullsrc=channel_layout=stereo:sample_rate=44100:d={duration}",
            "-shortest",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
        ]
        if bitrate:
            cmd += ["-b:v", str(bitrate)]
        cmd += [
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path,
        ]
        self._run(cmd)

    def _render_video_segment(
        self,
        clip: Dict[str, Any],
        input_path: str,
        settings: Dict[str, Any],
        output_path: str,
        fade_in_override: Optional[float] = None,
        fade_out_override: Optional[float] = None,
    ) -> float:
        duration = max(0.05, _as_float(clip.get("duration"), 0.0))
        trim_start = _as_float(clip.get("trimStart"), 0.0)
        trim_end = clip.get("trimEnd")
        speed = _clamp(_as_float((clip.get("effects") or {}).get("speed"), 1.0), 0.25, 4.0)

        source_duration = duration * speed
        if trim_end is not None:
            trim_end_val = _as_float(trim_end, trim_start + source_duration)
            source_duration = max(0.05, trim_end_val - trim_start)

        output_duration = max(0.05, source_duration / speed)
        has_audio = _has_audio_stream(input_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(trim_start),
            "-t",
            str(source_duration),
            "-i",
            input_path,
        ]

        if not has_audio:
            cmd += [
                "-f",
                "lavfi",
                "-i",
                f"anullsrc=channel_layout=stereo:sample_rate=44100:d={output_duration}",
            ]

        vf: List[str] = []
        af: List[str] = []

        crop_cfg = clip.get("crop") or {}
        if isinstance(crop_cfg, dict):
            src_info = _ffprobe_info(input_path)
            src_width = _as_int(src_info.get("width"), 0)
            src_height = _as_int(src_info.get("height"), 0)
            if src_width > 1 and src_height > 1:
                crop_x = _clamp(_as_float(crop_cfg.get("x"), 0.0), 0.0, 1.0)
                crop_y = _clamp(_as_float(crop_cfg.get("y"), 0.0), 0.0, 1.0)
                crop_w = _clamp(_as_float(crop_cfg.get("width"), 1.0), 0.05, 1.0)
                crop_h = _clamp(_as_float(crop_cfg.get("height"), 1.0), 0.05, 1.0)
                px_w = max(2, int(round(src_width * crop_w)))
                px_h = max(2, int(round(src_height * crop_h)))
                px_x = int(round(src_width * crop_x))
                px_y = int(round(src_height * crop_y))
                px_x = max(0, min(px_x, src_width - px_w))
                px_y = max(0, min(px_y, src_height - px_h))
                if px_w < src_width or px_h < src_height or px_x > 0 or px_y > 0:
                    vf.append(f"crop={px_w}:{px_h}:{px_x}:{px_y}")

        scale = self._scale_filter(clip.get("fitMode") or "fit", settings["width"], settings["height"])
        if scale:
            vf.append(scale)

        rotation = _as_float(clip.get("rotation"), 0.0)
        if abs(rotation) > 0.01:
            vf.append(f"rotate={rotation}*PI/180")

        effects = clip.get("effects") or {}
        brightness = _as_float(effects.get("brightness"), 0.0)
        contrast = _as_float(effects.get("contrast"), 1.0)
        saturation = _as_float(effects.get("saturation"), 1.0)
        gamma = _as_float(effects.get("gamma"), 1.0)
        hue = _as_float(effects.get("hue"), 0.0)
        blur = _as_float(effects.get("blur"), 0.0)
        opacity = _clamp(_as_float(effects.get("opacity"), 1.0), 0.0, 1.0)

        if any(abs(val) > 0.001 for val in [brightness, contrast - 1.0, saturation - 1.0, gamma - 1.0]):
            vf.append(
                f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}:gamma={gamma}"
            )
        if abs(hue) > 0.001:
            vf.append(f"hue=h={hue}")
        if blur > 0.1:
            vf.append(f"boxblur=luma_radius={blur}")
        if opacity < 1.0:
            vf.append(f"format=rgba,colorchannelmixer=aa={opacity}")

        if abs(speed - 1.0) > 0.001:
            vf.append(f"setpts={1.0 / speed}*PTS")
            if has_audio:
                af.append(_atempo_chain(speed))

        fade_in = _as_float(effects.get("fadeIn"), 0.0) if fade_in_override is None else float(fade_in_override)
        fade_out = _as_float(effects.get("fadeOut"), 0.0) if fade_out_override is None else float(fade_out_override)
        audio_fade_in = _as_float(effects.get("audioFadeIn"), fade_in)
        audio_fade_out = _as_float(effects.get("audioFadeOut"), fade_out)
        volume = _as_float(effects.get("volume"), 1.0)
        if has_audio and abs(volume - 1.0) > 0.001:
            af.append(f"volume={volume}")
        if fade_in > 0:
            vf.append(f"fade=t=in:st=0:d={fade_in}")
            if has_audio:
                af.append(f"afade=t=in:st=0:d={audio_fade_in}")
        if fade_out > 0:
            fade_start = max(0.0, output_duration - fade_out)
            vf.append(f"fade=t=out:st={fade_start}:d={fade_out}")
            if has_audio:
                af.append(f"afade=t=out:st={fade_start}:d={audio_fade_out}")

        if settings.get("fps"):
            cmd += ["-r", str(settings["fps"])]

        if vf:
            cmd += ["-vf", ",".join(vf)]
        if af:
            cmd += ["-af", ",".join(af)]

        if has_audio:
            cmd += ["-map", "0:v", "-map", "0:a?"]
        else:
            cmd += ["-map", "0:v", "-map", "1:a"]

        cmd += [
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
        ]
        if settings.get("bitrate"):
            cmd += ["-b:v", str(settings.get("bitrate"))]
        cmd += [
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path,
        ]
        self._run(cmd)
        return output_duration

    def _concat_segments(self, inputs: List[str], output_path: str) -> None:
        list_path = str(Path(output_path).with_suffix(".list"))
        with open(list_path, "w", encoding="utf-8") as handle:
            for p in inputs:
                ab = os.path.abspath(p).replace("\\", "/")
                handle.write(f"file '{ab}'\n")
        try:
            cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path, "-c", "copy", output_path]
            self._run(cmd)
        except Exception:
            cmd = [
                "ffmpeg",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                list_path,
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
            self._run(cmd)
        finally:
            try:
                os.remove(list_path)
            except OSError:
                pass

    def _merge_with_transition(
        self,
        first_path: str,
        first_duration: float,
        second_path: str,
        second_duration: float,
        transition: str,
        duration: float,
        output_path: str,
        fps: float,
        bitrate: Optional[str],
    ) -> float:
        transition = transition or "fade"
        duration = max(0.01, float(duration))
        offset = max(0.0, float(first_duration) - duration)
        def _build_cmd(trans: str) -> List[str]:
            base_cmd = [
                "ffmpeg",
                "-y",
                "-i",
                first_path,
                "-i",
                second_path,
                "-filter_complex",
                (
                    f"[0:v][1:v]xfade=transition={trans}:duration={duration}:offset={offset}[v];"
                    f"[0:a][1:a]acrossfade=d={duration}:c1=tri:c2=tri[a]"
                ),
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-c:v",
                "libx264",
                "-preset",
                "fast",
                "-pix_fmt",
                "yuv420p",
            ]
            if fps:
                base_cmd += ["-r", str(fps)]
            if bitrate:
                base_cmd += ["-b:v", str(bitrate)]
            base_cmd += [
                "-c:a",
                "aac",
                "-movflags",
                "+faststart",
                output_path,
            ]
            return base_cmd

        try:
            self._run(_build_cmd(transition))
        except RuntimeError:
            if transition != "fade":
                self._run(_build_cmd("fade"))
            else:
                raise
        return max(0.01, first_duration + second_duration - duration)

    def _overlay_image(
        self,
        base_path: str,
        image_path: str,
        start: float,
        end: float,
        x_expr: str,
        y_expr: str,
        width: int,
        height: int,
        opacity_expr: str,
        fit_mode: str,
        rotation: float,
        blend_mode: str,
        canvas_width: int,
        canvas_height: int,
        output_path: str,
    ) -> None:
        enable = f"between(t,{start},{end})"
        xq = _quote_expr(x_expr)
        yq = _quote_expr(y_expr)
        scale = self._scale_filter(fit_mode, width, height) or f"scale={width}:{height}"
        overlay_chain = f"[1:v]setpts=PTS-STARTPTS+{start}/TB,{scale},format=rgba"
        if abs(rotation) > 0.01:
            overlay_chain += f",rotate={rotation}*PI/180"
        if opacity_expr != "1" and opacity_expr != "1.0":
            overlay_chain += f",colorchannelmixer=aa={_quote_expr(opacity_expr)}"

        if blend_mode and blend_mode != "normal" and canvas_width and canvas_height:
            overlay_chain += f",pad={canvas_width}:{canvas_height}:{xq}:{yq}:color=0x00000000"
            fc = (
                f"{overlay_chain}[ov];"
                f"[0:v][ov]blend=all_mode={blend_mode}:all_opacity=1:enable='{enable}'[v]"
            )
        else:
            fc = (
                f"{overlay_chain}[ov];"
                f"[0:v][ov]overlay={xq}:{yq}:enable='{enable}'[v]"
            )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            base_path,
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
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path,
        ]
        self._run(cmd)

    def _overlay_video(
        self,
        base_path: str,
        overlay_path: str,
        start: float,
        end: float,
        x_expr: str,
        y_expr: str,
        width: int,
        height: int,
        opacity_expr: str,
        fit_mode: str,
        rotation: float,
        blend_mode: str,
        canvas_width: int,
        canvas_height: int,
        output_path: str,
    ) -> None:
        enable = f"between(t,{start},{end})"
        xq = _quote_expr(x_expr)
        yq = _quote_expr(y_expr)
        scale = self._scale_filter(fit_mode, width, height) or f"scale={width}:{height}"
        overlay_chain = f"[1:v]setpts=PTS-STARTPTS+{start}/TB,{scale},format=rgba"
        if abs(rotation) > 0.01:
            overlay_chain += f",rotate={rotation}*PI/180"
        if opacity_expr != "1" and opacity_expr != "1.0":
            overlay_chain += f",colorchannelmixer=aa={_quote_expr(opacity_expr)}"

        if blend_mode and blend_mode != "normal" and canvas_width and canvas_height:
            overlay_chain += f",pad={canvas_width}:{canvas_height}:{xq}:{yq}:color=0x00000000"
            fc = (
                f"{overlay_chain}[ov];"
                f"[0:v][ov]blend=all_mode={blend_mode}:all_opacity=1:enable='{enable}'[v]"
            )
        else:
            fc = (
                f"{overlay_chain}[ov];"
                f"[0:v][ov]overlay={xq}:{yq}:enable='{enable}'[v]"
            )

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
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path,
        ]
        self._run(cmd)

    def _overlay_text(
        self,
        base_path: str,
        text: str,
        start: float,
        end: float,
        x: int,
        y: int,
        font_size: int,
        color: str,
        opacity: float,
        output_path: str,
    ) -> None:
        esc_text = (
            (text or "").replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace("%", "\\%")
        )
        enable = f"between(t,{start},{end})"
        if "@" not in color:
            color = f"{color}@{_clamp(opacity, 0.0, 1.0)}"
        drawtext = (
            "drawtext="
            f"text='{esc_text}':"
            f"fontcolor={color}:fontsize={font_size}:"
            "box=1:boxcolor=black@0.35:boxborderw=10:"
            f"x={x}:y={y}:"
            f"enable='{enable}'"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            base_path,
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
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path,
        ]
        self._run(cmd)

    def _parse_rgba(self, color: str, alpha: float = 1.0) -> Tuple[int, int, int, int]:
        try:
            r, g, b = ImageColor.getrgb(color or "#8f8cae")
        except Exception:
            r, g, b = (143, 140, 174)
        a = int(_clamp(alpha, 0.0, 1.0) * 255)
        return (r, g, b, a)

    def _render_shape_overlay(
        self,
        output_path: str,
        shape_type: str,
        width: int,
        height: int,
        color: str,
        outline: bool,
    ) -> None:
        w = max(2, int(width))
        h = max(2, int(height))
        rgba = self._parse_rgba(color, 1.0)
        image = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        stroke_width = max(2, min(w, h) // 20)
        inset = max(1, stroke_width // 2)
        bounds = [inset, inset, w - inset - 1, h - inset - 1]
        kind = (shape_type or "").strip().lower()

        if kind == "circle":
            draw.ellipse(bounds, fill=rgba, outline=self._parse_rgba("#ffffff", 0.9) if outline else None, width=stroke_width if outline else 0)
        elif kind == "outline":
            draw.rectangle(bounds, outline=rgba, width=stroke_width)
        elif kind == "arrow":
            points = [
                (0, int(h * 0.22)),
                (int(w * 0.66), int(h * 0.22)),
                (int(w * 0.66), 0),
                (w - 1, int(h * 0.5)),
                (int(w * 0.66), h - 1),
                (int(w * 0.66), int(h * 0.78)),
                (0, int(h * 0.78)),
            ]
            draw.polygon(points, fill=rgba)
            if outline:
                draw.line(points + [points[0]], fill=self._parse_rgba("#ffffff", 0.9), width=max(1, stroke_width // 2))
        else:
            if outline:
                draw.rectangle(bounds, fill=rgba, outline=self._parse_rgba("#ffffff", 0.9), width=max(1, stroke_width // 2))
            else:
                draw.rectangle(bounds, fill=rgba)

        image.save(output_path, format="PNG")

    def _overlay_shape(
        self,
        base_path: str,
        start: float,
        end: float,
        x: int,
        y: int,
        width: int,
        height: int,
        color: str,
        outline: bool,
        opacity: float,
        output_path: str,
    ) -> None:
        enable = f"between(t,{start},{end})"
        thickness = 2 if outline else "fill"
        if "@" not in color:
            color = f"{color}@{_clamp(opacity, 0.0, 1.0)}"
        drawbox = (
            f"drawbox=x={x}:y={y}:w={width}:h={height}:color={color}:t={thickness}:"
            f"enable='{enable}'"
        )
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            base_path,
            "-vf",
            drawbox,
            "-map",
            "0:v",
            "-map",
            "0:a?",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-movflags",
            "+faststart",
            output_path,
        ]
        self._run(cmd)

    def _trim_audio(
        self,
        audio_path: str,
        start: float,
        duration: float,
        volume: float,
        fade_in: float,
        fade_out: float,
        output_path: str,
    ) -> None:
        duration = max(0.05, float(duration))
        filters: List[str] = []
        if abs(volume - 1.0) > 0.001:
            filters.append(f"volume={volume}")
        if fade_in > 0:
            filters.append(f"afade=t=in:st=0:d={fade_in}")
        if fade_out > 0:
            fade_start = max(0.0, duration - fade_out)
            filters.append(f"afade=t=out:st={fade_start}:d={fade_out}")
        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(max(0.0, start)),
            "-t",
            str(duration),
            "-i",
            audio_path,
            "-vn",
        ]
        if filters:
            cmd += ["-af", ",".join(filters)]
        cmd += ["-c:a", "aac", output_path]
        self._run(cmd)

    def _mix_audio(
        self,
        video_path: str,
        audio_path: str,
        at_time: float,
        volume: float,
        output_path: str,
    ) -> None:
        if not _has_audio_stream(audio_path):
            raise RuntimeError("Provided audio file has no audio stream")

        delay_ms = max(0, int(float(at_time) * 1000))
        gain = max(0.0, float(volume))

        if _has_audio_stream(video_path):
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
            output_path,
        ]
        self._run(cmd)

    def render(
        self,
        state: Dict[str, Any],
        video_map: Dict[str, Any],
        asset_map: Dict[str, Any],
        output_path: str,
        output_settings: Dict[str, Any],
    ) -> None:
        tracks = state.get("tracks") or []
        clips = [clip for track in tracks for clip in (track.get("clips") or [])]

        video_clips = [c for c in clips if c.get("type") == "video" and c.get("sourceId")]
        graphics_clips = [c for c in clips if c.get("type") in {"image", "text", "shape"}]
        audio_clips = [c for c in clips if c.get("type") == "audio" and c.get("sourceId")]
        debug_enabled = str(os.getenv("EDITOR_PARITY_DEBUG", "")).strip().lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        debug_trace: Dict[str, Any] = {
            "enabled": debug_enabled,
            "output_settings": dict(output_settings or {}),
            "normalized_clips": [],
            "transition_decisions": [],
            "overlap_to_overlay": [],
            "merge_sequence": [],
        }

        if not video_clips and not graphics_clips and not audio_clips:
            raise RuntimeError("Project has no clips to export")

        def _clip_layer(clip: Dict[str, Any]) -> int:
            return _as_int(clip.get("layer"), 1)

        def _clip_group(clip: Dict[str, Any]) -> str:
            group = clip.get("layerGroup")
            if isinstance(group, str) and group:
                return group
            if clip.get("type") == "audio":
                return "audio"
            if clip.get("type") == "video":
                return "video"
            return "graphics"

        def _clip_snapshot(clip: Dict[str, Any]) -> Dict[str, Any]:
            start = _as_float(clip.get("startTime"), 0.0)
            duration = max(0.0, _as_float(clip.get("duration"), 0.0))
            end = start + duration
            return {
                "id": str(clip.get("id") or ""),
                "type": str(clip.get("type") or ""),
                "group": _clip_group(clip),
                "layer": _clip_layer(clip),
                "start": start,
                "duration": duration,
                "end": end,
                "effects": dict(clip.get("effects") or {}),
            }

        base_layer = min((_clip_layer(c) for c in video_clips), default=1)
        base_video_clips = [c for c in video_clips if _clip_layer(c) == base_layer]
        overlay_video_clips = [c for c in video_clips if _clip_layer(c) != base_layer]
        if debug_enabled:
            debug_trace["normalized_clips"] = [_clip_snapshot(clip) for clip in clips]
            debug_trace["base_layer"] = base_layer

        width = _as_int(output_settings.get("width"), 0)
        height = _as_int(output_settings.get("height"), 0)
        fps = output_settings.get("fps")
        bitrate = output_settings.get("bitrate")
        preset = (output_settings.get("preset") or "").strip().lower()
        if preset in PRESET_SPECS:
            spec = PRESET_SPECS[preset]
            width = width or spec.get("width")
            height = height or spec.get("height")
            fps = fps or spec.get("fps")
            bitrate = bitrate or spec.get("bitrate")

        if (not width or not height) and video_clips:
            first = video_clips[0]
            src_id = str(first.get("sourceId"))
            if src_id in video_map:
                src_path = self.storage.resolve_for_processing(video_map[src_id].storage_path)
                info = _ffprobe_info(src_path)
                width = width or _as_int(info.get("width"), 1920)
                height = height or _as_int(info.get("height"), 1080)
                fps = fps or info.get("fps")

        width = width or 1920
        height = height or 1080
        fps = fps or 30

        settings = {"width": width, "height": height, "fps": fps, "bitrate": bitrate}

        temp_dir = Path(tempfile.mkdtemp(prefix="timeline_", dir=str(self.temp_root)))

        # Build base video timeline (video clips + gaps).
        cursor = 0.0
        clip_entries: List[Tuple[float, Dict[str, Any]]] = []
        for clip in base_video_clips:
            try:
                start = _as_float(clip.get("startTime"), 0.0)
                clip_entries.append((start, clip))
            except Exception:
                continue
        clip_entries.sort(key=lambda item: item[0])

        # Determine timeline end (include graphics/audio).
        def _clip_end(c: Dict[str, Any]) -> float:
            return _as_float(c.get("startTime"), 0.0) + max(0.0, _as_float(c.get("duration"), 0.0))

        timeline_end = 0.0
        for c in clips:
            timeline_end = max(timeline_end, _clip_end(c))

        # Precompute transitions between adjacent clips.
        transitions: Dict[int, Tuple[str, float]] = {}
        for idx in range(len(clip_entries) - 1):
            prev_start, prev_clip = clip_entries[idx]
            next_start, next_clip = clip_entries[idx + 1]
            prev_end = prev_start + max(0.0, _as_float(prev_clip.get("duration"), 0.0))
            gap = next_start - prev_end
            gap_frames = int(round(gap * float(settings.get("fps") or 30)))
            decision: Dict[str, Any] = {
                "index": idx,
                "from_clip_id": str(prev_clip.get("id") or ""),
                "to_clip_id": str(next_clip.get("id") or ""),
                "gap_seconds": gap,
                "gap_frames": gap_frames,
            }
            if gap_frames != 0:
                decision["accepted"] = False
                decision["reason"] = "gap_not_adjacent_frames"
                if debug_enabled:
                    debug_trace["transition_decisions"].append(decision)
                continue
            prev_effects = prev_clip.get("effects") or {}
            transition_with = str(prev_effects.get("transitionWith") or "").strip()
            next_clip_id = str(next_clip.get("id") or "").strip()
            raw_transition = prev_effects.get("transition")
            if transition_with and next_clip_id and transition_with != next_clip_id:
                raw_transition = None
            trans_name = _normalize_transition(raw_transition)
            duration = _as_float(prev_effects.get("transitionDuration"), 0.0)
            if not trans_name or duration <= 0:
                decision["accepted"] = False
                decision["reason"] = "missing_or_invalid_transition"
                decision["normalized_transition"] = trans_name
                decision["duration"] = duration
                if debug_enabled:
                    debug_trace["transition_decisions"].append(decision)
                continue
            max_dur = min(
                max(0.2, _as_float(prev_clip.get("duration"), 0.0)),
                max(0.2, _as_float(next_clip.get("duration"), 0.0)),
            )
            duration = min(duration, max_dur)
            transitions[idx] = (trans_name, duration)
            decision["accepted"] = True
            decision["reason"] = "ok"
            decision["normalized_transition"] = trans_name
            decision["duration"] = duration
            decision["max_duration"] = max_dur
            if debug_enabled:
                debug_trace["transition_decisions"].append(decision)

        entries: List[Dict[str, Any]] = []
        overlap_clips: List[Dict[str, Any]] = []
        if not clip_entries:
            blank = temp_dir / "base_blank.mp4"
            self._render_blank_segment(max(1.0, timeline_end), settings, str(blank))
            entries.append({"path": str(blank), "duration": max(1.0, timeline_end), "clip": None})
        else:
            for idx, (start, clip) in enumerate(clip_entries):
                if start < cursor - 0.01:
                    overlap_clips.append(clip)
                    if debug_enabled:
                        debug_trace["overlap_to_overlay"].append(
                            {
                                "clip_id": str(clip.get("id") or ""),
                                "start": start,
                                "cursor": cursor,
                                "reason": "start_before_cursor",
                            }
                        )
                    continue

                if start > cursor + 0.01:
                    gap_path = temp_dir / f"gap_{len(entries)}.mp4"
                    gap_dur = start - cursor
                    self._render_blank_segment(gap_dur, settings, str(gap_path))
                    entries.append({"path": str(gap_path), "duration": gap_dur, "clip": None})
                    if debug_enabled:
                        debug_trace["merge_sequence"].append(
                            {
                                "kind": "gap",
                                "duration": gap_dur,
                                "start": cursor,
                                "end": start,
                            }
                        )
                    cursor = start

                clip_id = str(clip.get("sourceId"))
                video = video_map.get(clip_id)
                if not video:
                    raise RuntimeError(f"Missing source video {clip_id}")

                input_path = self.storage.resolve_for_processing(video.storage_path)
                seg_path = temp_dir / f"clip_{len(entries)}.mp4"

                fade_in_override = 0.0 if (idx - 1) in transitions else None
                fade_out_override = 0.0 if idx in transitions else None

                out_dur = self._render_video_segment(
                    clip,
                    input_path,
                    settings,
                    str(seg_path),
                    fade_in_override=fade_in_override,
                    fade_out_override=fade_out_override,
                )
                entries.append({"path": str(seg_path), "duration": out_dur, "clip": clip, "transition": transitions.get(idx)})
                if debug_enabled:
                    debug_trace["merge_sequence"].append(
                        {
                            "kind": "clip",
                            "clip_id": str(clip.get("id") or ""),
                            "duration": out_dur,
                            "transition_out": transitions.get(idx),
                        }
                    )
                cursor += out_dur

            if timeline_end > cursor + 0.01:
                gap_path = temp_dir / f"gap_tail.mp4"
                gap_dur = timeline_end - cursor
                self._render_blank_segment(gap_dur, settings, str(gap_path))
                entries.append({"path": str(gap_path), "duration": gap_dur, "clip": None})
                if debug_enabled:
                    debug_trace["merge_sequence"].append(
                        {
                            "kind": "gap_tail",
                            "duration": gap_dur,
                            "start": cursor,
                            "end": timeline_end,
                        }
                    )

        # Merge entries, applying transitions between adjacent clips when present.
        base_path = entries[0]["path"]
        base_duration = float(entries[0]["duration"])
        for idx in range(1, len(entries)):
            next_entry = entries[idx]
            next_path = next_entry["path"]
            next_duration = float(next_entry["duration"])
            transition = entries[idx - 1].get("transition")
            out_path = str(temp_dir / f"base_merge_{idx}.mp4")
            if transition:
                trans_name, trans_dur = transition
                if debug_enabled:
                    debug_trace["merge_sequence"].append(
                        {
                            "kind": "transition_merge",
                            "index": idx,
                            "transition": trans_name,
                            "duration": trans_dur,
                            "first_duration": base_duration,
                            "second_duration": next_duration,
                        }
                    )
                base_duration = self._merge_with_transition(
                    base_path,
                    base_duration,
                    next_path,
                    next_duration,
                    trans_name,
                    trans_dur,
                    out_path,
                    fps=settings.get("fps") or 30,
                    bitrate=settings.get("bitrate"),
                )
                base_path = out_path
            else:
                if debug_enabled:
                    debug_trace["merge_sequence"].append(
                        {
                            "kind": "concat",
                            "index": idx,
                            "first_duration": base_duration,
                            "second_duration": next_duration,
                        }
                    )
                self._concat_segments([base_path, next_path], out_path)
                base_duration += next_duration
                base_path = out_path

        if overlap_clips:
            overlay_video_clips.extend(overlap_clips)

        # Apply overlays (video + graphics).
        current_path = base_path
        overlay_index = 0
        overlay_items = overlay_video_clips + graphics_clips
        blend_modes_allowed = {
            "normal",
            "multiply",
            "screen",
            "overlay",
            "darken",
            "lighten",
            "hardlight",
            "softlight",
            "difference",
            "exclusion",
        }

        def _overlay_sort_key(clip: Dict[str, Any]):
            group = _clip_group(clip)
            base = 0 if group == "video" else 1000 if group == "graphics" else 2000
            return (base + _clip_layer(clip), _as_float(clip.get("startTime"), 0.0))

        overlay_sorted = sorted(overlay_items, key=_overlay_sort_key)
        for clip in overlay_sorted:
            start = _as_float(clip.get("startTime"), 0.0)
            end = start + max(0.05, _as_float(clip.get("duration"), 0.0))
            position = clip.get("position") or {}
            size = clip.get("size") or {}
            x = int(width * (_as_float(position.get("x"), 0.0) / 100.0))
            y = int(height * (_as_float(position.get("y"), 0.0) / 100.0))
            w = max(1, int(width * (_as_float(size.get("width"), 100.0) / 100.0)))
            h = max(1, int(height * (_as_float(size.get("height"), 100.0) / 100.0)))

            effects = clip.get("effects") or {}
            opacity = _clamp(_as_float(effects.get("opacity"), 1.0), 0.0, 1.0)
            rotation = _as_float(clip.get("rotation"), 0.0)
            fit_mode = str(clip.get("fitMode") or "fit")
            blend_mode = str(effects.get("blendMode") or "normal").lower()
            if blend_mode in {"soft-light", "soft_light"}:
                blend_mode = "softlight"
            if blend_mode in {"hard-light", "hard_light"}:
                blend_mode = "hardlight"
            if blend_mode not in blend_modes_allowed:
                blend_mode = "normal"

            keyframes = clip.get("keyframes") or []
            pos_frames_x: List[Tuple[float, float]] = []
            pos_frames_y: List[Tuple[float, float]] = []
            opacity_frames: List[Tuple[float, float]] = []
            for kf in keyframes:
                if not isinstance(kf, dict):
                    continue
                t = _as_float(kf.get("time"), 0.0)
                if not kf.get("absolute"):
                    t += start
                pos = kf.get("position") or {}
                if isinstance(pos, dict):
                    if pos.get("x") is not None:
                        pos_frames_x.append((t, width * (_as_float(pos.get("x"), 0.0) / 100.0)))
                    if pos.get("y") is not None:
                        pos_frames_y.append((t, height * (_as_float(pos.get("y"), 0.0) / 100.0)))
                if kf.get("opacity") is not None:
                    opacity_frames.append((t, _clamp(_as_float(kf.get("opacity"), opacity), 0.0, 1.0)))

            x_expr = _build_interp_expr(pos_frames_x, float(x))
            y_expr = _build_interp_expr(pos_frames_y, float(y))
            opacity_expr = _build_interp_expr(opacity_frames, opacity)

            out_path = str(temp_dir / f"overlay_{overlay_index}.mp4")
            overlay_index += 1

            if clip.get("type") == "video":
                clip_id = str(clip.get("sourceId"))
                video = video_map.get(clip_id)
                if not video:
                    continue
                input_path = self.storage.resolve_for_processing(video.storage_path)
                seg_path = str(temp_dir / f"overlay_src_{overlay_index}.mp4")
                seg_duration = self._render_video_segment(clip, input_path, settings, seg_path)
                self._overlay_video(
                    current_path,
                    seg_path,
                    start,
                    start + seg_duration,
                    x_expr,
                    y_expr,
                    w,
                    h,
                    opacity_expr,
                    fit_mode,
                    rotation,
                    blend_mode,
                    width,
                    height,
                    out_path,
                )
                current_path = out_path
                volume = _as_float(effects.get("volume"), 1.0)
                if volume > 0:
                    try:
                        audio_out = str(temp_dir / f"audio_mix_overlay_{overlay_index}.mp4")
                        self._mix_audio(
                            video_path=current_path,
                            audio_path=seg_path,
                            at_time=start,
                            volume=volume,
                            output_path=audio_out,
                        )
                        current_path = audio_out
                    except Exception:
                        pass
                continue

            if clip.get("type") == "image":
                asset = asset_map.get(str(clip.get("sourceId")))
                if not asset:
                    continue
                image_path = self.storage.resolve_for_processing(asset.storage_path)
                self._overlay_image(
                    current_path,
                    image_path,
                    start,
                    end,
                    x_expr,
                    y_expr,
                    w,
                    h,
                    opacity_expr,
                    fit_mode,
                    rotation,
                    blend_mode,
                    width,
                    height,
                    out_path,
                )
            elif clip.get("type") == "text":
                text = str(clip.get("text") or clip.get("label") or "Text")
                color = _hex_to_ffmpeg_color((clip.get("style") or {}).get("color") or "#ffffff", opacity)
                font_size = max(14, int(h * 0.6))
                self._overlay_text(current_path, text, start, end, x, y, font_size, color, opacity, out_path)
            elif clip.get("type") == "shape":
                style = clip.get("style") or {}
                shape_type = str(style.get("shapeType") or clip.get("label") or "square").strip().lower()
                color = str(style.get("color") or "#8f8cae")
                outline = bool(style.get("outline"))
                shape_path = str(temp_dir / f"shape_{overlay_index}.png")
                self._render_shape_overlay(shape_path, shape_type, w, h, color, outline)
                self._overlay_image(
                    current_path,
                    shape_path,
                    start,
                    end,
                    x_expr,
                    y_expr,
                    w,
                    h,
                    opacity_expr,
                    "stretch",
                    rotation,
                    blend_mode,
                    width,
                    height,
                    out_path,
                )
            else:
                continue

            current_path = out_path

        # Apply audio overlays.
        audio_sorted = sorted(audio_clips, key=lambda c: _as_float(c.get("startTime"), 0.0))
        audio_index = 0
        for clip in audio_sorted:
            source_id = str(clip.get("sourceId"))
            # Skip audio that references source videos (base audio already included).
            if source_id in video_map:
                continue
            asset = asset_map.get(source_id)
            if not asset:
                continue
            audio_path = self.storage.resolve_for_processing(asset.storage_path)
            start = _as_float(clip.get("startTime"), 0.0)
            duration = max(0.05, _as_float(clip.get("duration"), 0.0))
            trim_start = _as_float(clip.get("trimStart"), 0.0)
            effects = clip.get("effects") or {}
            volume = _as_float(effects.get("volume"), 1.0)
            fade_in = _as_float(effects.get("audioFadeIn"), _as_float(effects.get("fadeIn"), 0.0))
            fade_out = _as_float(effects.get("audioFadeOut"), _as_float(effects.get("fadeOut"), 0.0))

            if volume <= 0:
                continue

            trimmed_audio = str(temp_dir / f"audio_{audio_index}.m4a")
            audio_index += 1
            self._trim_audio(
                audio_path,
                trim_start,
                duration,
                volume,
                fade_in,
                fade_out,
                trimmed_audio,
            )

            out_path = str(temp_dir / f"audio_mix_{audio_index}.mp4")
            self._mix_audio(
                video_path=current_path,
                audio_path=trimmed_audio,
                at_time=start,
                volume=1.0,
                output_path=out_path,
            )
            current_path = out_path

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        if os.path.abspath(current_path) != os.path.abspath(output_path):
            shutil.copy2(current_path, output_path)

        if debug_enabled:
            debug_trace["final_output_path"] = output_path
            debug_trace["final_timeline_duration"] = base_duration
            debug_trace["overlay_count"] = len(overlay_sorted)
            debug_trace["audio_overlay_count"] = len(audio_sorted)
            self.last_debug_trace = debug_trace
            trace_path = f"{output_path}.parity.trace.json"
            with open(trace_path, "w", encoding="utf-8") as trace_file:
                json.dump(debug_trace, trace_file, indent=2)
