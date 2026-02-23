from pathlib import Path
import json

import app.services.timeline_renderer as timeline_renderer
from app.services.timeline_renderer import TimelineRenderer, _normalize_transition


class _DummyStorage:
    def resolve_for_processing(self, path: str) -> str:
        return path


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


def test_render_writes_debug_trace_when_enabled(monkeypatch, tmp_path):
    renderer = TimelineRenderer(_DummyStorage(), temp_root=str(tmp_path))

    def _touch(path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b"0")

    monkeypatch.setenv("EDITOR_PARITY_DEBUG", "1")
    monkeypatch.setattr(timeline_renderer, "_has_audio_stream", lambda _path: False)
    monkeypatch.setattr(
        timeline_renderer,
        "_ffprobe_info",
        lambda _path: {"width": 1920, "height": 1080, "duration": 10, "fps": 30},
    )
    monkeypatch.setattr(
        renderer,
        "_render_video_segment",
        lambda clip, _input, _settings, output_path, **_kwargs: (_touch(output_path), float(clip.get("duration", 1.0)))[1],
    )
    monkeypatch.setattr(
        renderer,
        "_render_blank_segment",
        lambda _duration, _settings, output_path: _touch(output_path),
    )
    monkeypatch.setattr(
        renderer,
        "_merge_with_transition",
        lambda _a, a_dur, _b, b_dur, _name, dur, output_path, **_kwargs: (_touch(output_path), float(a_dur + b_dur - dur))[1],
    )
    monkeypatch.setattr(
        renderer,
        "_concat_segments",
        lambda _inputs, output_path: _touch(output_path),
    )

    src1 = str(tmp_path / "src1.mp4")
    src2 = str(tmp_path / "src2.mp4")
    Path(src1).write_bytes(b"src1")
    Path(src2).write_bytes(b"src2")

    state = {
        "tracks": [
            {
                "id": "track-video",
                "clips": [
                    {
                        "id": "clip-a",
                        "type": "video",
                        "sourceId": "v1",
                        "startTime": 0,
                        "duration": 2.0,
                        "layer": 1,
                        "layerGroup": "video",
                        "effects": {
                            "transition": "Cross fade",
                            "transitionDuration": 0.5,
                            "transitionWith": "clip-b",
                        },
                    },
                    {
                        "id": "clip-b",
                        "type": "video",
                        "sourceId": "v2",
                        "startTime": 2.0,
                        "duration": 2.0,
                        "layer": 1,
                        "layerGroup": "video",
                    },
                ],
            }
        ]
    }
    video_map = {
        "v1": type("Video", (), {"storage_path": src1})(),
        "v2": type("Video", (), {"storage_path": src2})(),
    }
    output_path = str(tmp_path / "out.mp4")

    renderer.render(
        state=state,
        video_map=video_map,
        asset_map={},
        output_path=output_path,
        output_settings={"width": 1920, "height": 1080, "fps": 30, "bitrate": "4M"},
    )

    trace_path = Path(f"{output_path}.parity.trace.json")
    assert trace_path.exists()
    trace_data = json.loads(trace_path.read_text(encoding="utf-8"))
    assert trace_data["enabled"] is True
    assert any(item.get("accepted") for item in trace_data["transition_decisions"])
    assert any(item.get("kind") == "transition_merge" for item in trace_data["merge_sequence"])


def test_transition_detection_rejects_one_frame_gap(monkeypatch, tmp_path):
    renderer = TimelineRenderer(_DummyStorage(), temp_root=str(tmp_path))

    def _touch(path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(b"0")

    monkeypatch.setenv("EDITOR_PARITY_DEBUG", "1")
    monkeypatch.setattr(timeline_renderer, "_has_audio_stream", lambda _path: False)
    monkeypatch.setattr(
        timeline_renderer,
        "_ffprobe_info",
        lambda _path: {"width": 1920, "height": 1080, "duration": 10, "fps": 30},
    )
    monkeypatch.setattr(
        renderer,
        "_render_video_segment",
        lambda clip, _input, _settings, output_path, **_kwargs: (_touch(output_path), float(clip.get("duration", 1.0)))[1],
    )
    monkeypatch.setattr(renderer, "_render_blank_segment", lambda _duration, _settings, output_path: _touch(output_path))
    monkeypatch.setattr(
        renderer,
        "_merge_with_transition",
        lambda _a, a_dur, _b, b_dur, _name, dur, output_path, **_kwargs: (_touch(output_path), float(a_dur + b_dur - dur))[1],
    )
    monkeypatch.setattr(renderer, "_concat_segments", lambda _inputs, output_path: _touch(output_path))

    src1 = str(tmp_path / "src1.mp4")
    src2 = str(tmp_path / "src2.mp4")
    Path(src1).write_bytes(b"src1")
    Path(src2).write_bytes(b"src2")

    one_frame = 1 / 30
    state = {
        "tracks": [
            {
                "id": "track-video",
                "clips": [
                    {
                        "id": "clip-a",
                        "type": "video",
                        "sourceId": "v1",
                        "startTime": 0,
                        "duration": 2.0,
                        "layer": 1,
                        "layerGroup": "video",
                        "effects": {
                            "transition": "Cross fade",
                            "transitionDuration": 0.5,
                            "transitionWith": "clip-b",
                        },
                    },
                    {
                        "id": "clip-b",
                        "type": "video",
                        "sourceId": "v2",
                        "startTime": 2.0 + one_frame,
                        "duration": 2.0,
                        "layer": 1,
                        "layerGroup": "video",
                    },
                ],
            }
        ]
    }
    video_map = {
        "v1": type("Video", (), {"storage_path": src1})(),
        "v2": type("Video", (), {"storage_path": src2})(),
    }
    output_path = str(tmp_path / "out_gap.mp4")

    renderer.render(
        state=state,
        video_map=video_map,
        asset_map={},
        output_path=output_path,
        output_settings={"width": 1920, "height": 1080, "fps": 30, "bitrate": "4M"},
    )

    trace_data = json.loads(Path(f"{output_path}.parity.trace.json").read_text(encoding="utf-8"))
    assert any(item.get("gap_frames") == 1 for item in trace_data["transition_decisions"])
    assert all(not item.get("accepted") for item in trace_data["transition_decisions"])
