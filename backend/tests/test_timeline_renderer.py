from pathlib import Path

import app.services.timeline_renderer as timeline_renderer
from app.services.timeline_renderer import TimelineRenderer, _normalize_transition


class _DummyStorage:
    pass


def test_normalize_transition_stabilized_scope():
    assert _normalize_transition("Cross fade") == "fade"
    assert _normalize_transition("hard wipe") == "wipeleft"
    assert _normalize_transition("Hard wipe right") == "wipeleft"
    assert _normalize_transition("Burn") is None
    assert _normalize_transition("unsupported-transition") is None


def test_render_video_segment_includes_crop_filter(monkeypatch, tmp_path):
    renderer = TimelineRenderer(_DummyStorage(), temp_root=str(tmp_path))
    captured = {"cmd": None}

    def _fake_run(cmd):
        captured["cmd"] = cmd

    monkeypatch.setattr(timeline_renderer, "_has_audio_stream", lambda _path: False)
    monkeypatch.setattr(
        timeline_renderer,
        "_ffprobe_info",
        lambda _path: {"width": 1920, "height": 1080, "duration": 10},
    )
    monkeypatch.setattr(renderer, "_run", _fake_run)

    clip = {
        "duration": 4,
        "trimStart": 0,
        "trimEnd": 4,
        "fitMode": "fit",
        "crop": {"x": 0.1, "y": 0.2, "width": 0.5, "height": 0.4},
        "effects": {"speed": 1.0},
    }
    settings = {"width": 1080, "height": 1920, "fps": 30, "bitrate": "4M"}
    renderer._render_video_segment(clip, "input.mp4", settings, str(tmp_path / "out.mp4"))

    cmd = captured["cmd"]
    assert cmd is not None
    assert "-vf" in cmd
    vf_value = cmd[cmd.index("-vf") + 1]
    assert "crop=" in vf_value


def test_shape_overlay_image_generation(tmp_path):
    renderer = TimelineRenderer(_DummyStorage(), temp_root=str(tmp_path))
    shape_types = ["square", "circle", "outline", "arrow"]
    for shape_type in shape_types:
        output_path = Path(tmp_path) / f"{shape_type}.png"
        renderer._render_shape_overlay(str(output_path), shape_type, 120, 80, "#8f8cae", False)
        assert output_path.exists()
        assert output_path.stat().st_size > 0
