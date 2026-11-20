"""Behavioral contract for the Track B corpus execution runner.

CARLA and ultralytics are optional extras, so these tests replace both with
small fakes. What is pinned: poses survive rendering, detection writes one
report per frame per detector, and the result loads through the Track C loader.
"""

from __future__ import annotations

import json
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from scenario_gen import render, runner
from scenario_gen.corpus import CorpusLayout, write_plan
from scenario_gen.planning import ScenarioGenerationConfig, ScenarioPlan
from scenario_gen.render import RenderSettings
from scenario_gen.reports import read_report
from scenario_gen.runner import detect_corpus, render_corpus
from scenario_gen.truth_export import write_truth
from spike_dependence.artifacts_io import camera_poses_to_json
from spike_dependence.scene_matrix import CameraPose as SpikePose
from spike_dependence.scoring import BoundingBox as SpikeBox
from spike_dependence.scoring import Detection as SpikeDetection
from sweep.corpus import load_tasks
from trace_contracts.observations import BoundingBox
from trace_contracts.scenario import (
    DetectorPairing,
    ScenarioManifestEntry,
    render_cells,
)
from trace_contracts.truth import TruthObject

BOX = BoundingBox(390, 300, 410, 400)
POSE_A = SpikePose(12.5, -3.0, 14.0, 180.0, -32.5, 0.0, (1.0, 2.0, 0.5))
POSE_B = SpikePose(-8.25, 7.5, 14.0, 45.0, -32.5, 60.0, (1.0, 2.0, 0.5))
WEIGHTS = {"yolo11m": "yolo11m.pt", "rtdetr-l": "rtdetr-l.pt"}


def plan_with_one_scene() -> ScenarioPlan:
    entry = ScenarioManifestEntry("scene-0000", render_cells()[0], "Town10HD", 42)
    return ScenarioPlan(ScenarioGenerationConfig(), (entry,))


def make_rendered_corpus(root: Path) -> CorpusLayout:
    """Lay out what Phase 1 leaves behind: plan, frames, poses and truth."""
    layout = CorpusLayout(root)
    write_plan(layout, plan_with_one_scene())
    camera_poses_to_json(
        {"a": POSE_A, "b": POSE_B}, layout.camera_pose_path("scene-0000", "frame-000")
    )
    for source in ("agent-a", "agent-b"):
        frame = layout.frame_path("scene-0000", "frame-000", source)
        frame.parent.mkdir(parents=True, exist_ok=True)
        frame.write_bytes(b"not a real png; the fake predictor never reads it")
        write_truth(
            layout,
            scene_id="scene-0000",
            frame_id="frame-000",
            source_id=source,
            objects=[TruthObject("real", "scene-0000", source, "car", BOX)],
        )
    return layout


class FakePredictorFactory:
    """Records load order and returns one fixed detection per frame."""

    def __init__(self) -> None:
        self.loads: list[tuple[str, str, str]] = []

    def __call__(self, detector: str, weights: str, device: str):
        self.loads.append((detector, weights, device))

        def predict(image_path: Path, min_confidence: float):
            assert min_confidence == 0.3
            return [SpikeDetection("car", 0.9, SpikeBox(390.0, 300.0, 410.0, 400.0))]

        return predict


def test_detect_corpus_writes_one_report_per_frame_per_detector(tmp_path) -> None:
    layout = make_rendered_corpus(tmp_path)
    factory = FakePredictorFactory()

    written = detect_corpus(layout, WEIGHTS, "cpu", 0.3, predictor_factory=factory)

    assert len(written) == 4
    for detector in WEIGHTS:
        for source in ("agent-a", "agent-b"):
            path = layout.reports_root / detector / f"scene-0000--frame-000--{source}.json"
            report = read_report(path)
            assert (report.detector, report.source_id) == (detector, source)
            assert report.report_id == f"scene-0000--frame-000--{source}"
            assert len(report.detections) == 1
            assert report.detections[0].label == "car"


def test_detect_corpus_loads_detectors_sequentially_in_given_order(tmp_path) -> None:
    layout = make_rendered_corpus(tmp_path)
    factory = FakePredictorFactory()

    detect_corpus(layout, WEIGHTS, "cuda:0", 0.3, predictor_factory=factory)

    assert factory.loads == [
        ("yolo11m", "yolo11m.pt", "cuda:0"),
        ("rtdetr-l", "rtdetr-l.pt", "cuda:0"),
    ]


def test_report_pose_comes_from_the_recorded_camera_poses(tmp_path) -> None:
    layout = make_rendered_corpus(tmp_path)
    detect_corpus(layout, WEIGHTS, "cpu", 0.3, predictor_factory=FakePredictorFactory())

    report = read_report(
        layout.reports_root / "yolo11m" / "scene-0000--frame-000--agent-b.json"
    )

    pose = report.camera_pose
    assert (pose.x, pose.y, pose.z, pose.yaw, pose.pitch) == (-8.25, 7.5, 14.0, 45.0, -32.5)
    assert report.observed_at == report.arrived_at
    assert report.observed_at.tzinfo is not None


def test_generated_corpus_loads_through_the_sweep_loader(tmp_path) -> None:
    layout = make_rendered_corpus(tmp_path)
    detect_corpus(layout, WEIGHTS, "cpu", 0.3, predictor_factory=FakePredictorFactory())

    tasks = load_tasks(layout.root, tuple(DetectorPairing))

    assert len(tasks) == len(DetectorPairing)
    for task in tasks:
        assert len(task.reports) == 2
        assert {r.source_id for r in task.reports} == {"agent-a", "agent-b"}
        assert all(len(objects) == 1 for objects in task.truth.values())


def test_detect_corpus_is_byte_reproducible(tmp_path) -> None:
    first = make_rendered_corpus(tmp_path / "first")
    second = make_rendered_corpus(tmp_path / "second")
    for layout in (first, second):
        detect_corpus(layout, WEIGHTS, "cpu", 0.3, predictor_factory=FakePredictorFactory())

    name = Path("yolo11m") / "scene-0000--frame-000--agent-a.json"
    assert (first.reports_root / name).read_bytes() == (second.reports_root / name).read_bytes()


def test_detect_corpus_rejects_a_frame_without_recorded_poses(tmp_path) -> None:
    layout = make_rendered_corpus(tmp_path)
    layout.camera_pose_path("scene-0000", "frame-000").unlink()

    with pytest.raises(FileNotFoundError):
        detect_corpus(layout, WEIGHTS, "cpu", 0.3, predictor_factory=FakePredictorFactory())


def test_detect_corpus_rejects_a_frame_name_it_cannot_parse(tmp_path) -> None:
    layout = make_rendered_corpus(tmp_path)
    (layout.frames_root / "stray.png").write_bytes(b"x")

    with pytest.raises(ValueError, match="stray"):
        detect_corpus(layout, WEIGHTS, "cpu", 0.3, predictor_factory=FakePredictorFactory())


def test_detect_corpus_rejects_an_empty_frame_folder(tmp_path) -> None:
    layout = CorpusLayout(tmp_path)
    write_plan(layout, plan_with_one_scene())

    with pytest.raises(ValueError, match="no frames"):
        detect_corpus(layout, WEIGHTS, "cpu", 0.3, predictor_factory=FakePredictorFactory())


def test_render_corpus_renders_every_manifest_entry_in_order(tmp_path, monkeypatch) -> None:
    layout = CorpusLayout(tmp_path)
    plan = ScenarioPlan(
        ScenarioGenerationConfig(),
        tuple(
            ScenarioManifestEntry(f"scene-{i:04d}", render_cells()[i], "Town10HD", i)
            for i in range(3)
        ),
    )
    seen: list[str] = []

    def fake_render_entry(client, entry, lay, settings):
        seen.append(entry.scene_id)
        pose_path = lay.camera_pose_path(entry.scene_id, "frame-000")
        return render.RenderedScene(entry.scene_id, "frame-000", (), (), pose_path)

    monkeypatch.setattr(runner, "render_entry", fake_render_entry)

    scenes = render_corpus(MagicMock(), plan, layout, RenderSettings())

    assert seen == ["scene-0000", "scene-0001", "scene-0002"]
    assert [s.scene_id for s in scenes] == seen


def test_render_entry_retains_the_camera_poses_beside_the_frames(tmp_path, monkeypatch) -> None:
    monkeypatch.setitem(sys.modules, "carla", types.ModuleType("carla"))

    def fake_render_scene(carla, client, spec, staging_root, **kwargs):
        scene_dir = staging_root / spec.scene_id
        scene_dir.mkdir(parents=True)
        for view in ("a", "b"):
            (scene_dir / f"rgb_{view}.png").write_bytes(b"png")
            (scene_dir / f"gt_{view}.json").write_text(
                json.dumps({"schema": "spike.ground_truth.v1", "objects": []}),
                encoding="utf-8",
            )
        camera_poses_to_json({"a": POSE_A, "b": POSE_B}, scene_dir / "camera_poses.json")
        return {"a": 0, "b": 0}

    monkeypatch.setattr(render, "render_scene", fake_render_scene)
    client = MagicMock()
    client.get_world().get_map().name = "/Game/Carla/Maps/Town10HD"
    layout = CorpusLayout(tmp_path)

    rendered = render.render_entry(client, plan_with_one_scene().entries[0], layout)

    assert rendered.camera_pose_path == layout.camera_pose_path("scene-0000", "frame-000")
    payload = json.loads(rendered.camera_pose_path.read_text(encoding="utf-8"))
    assert payload["schema"] == "spike.camera_poses.v1"
    assert set(payload["poses"]) == {"a", "b"}


def test_cli_passes_its_options_to_both_phases(tmp_path, monkeypatch) -> None:
    layout = make_rendered_corpus(tmp_path)
    calls: dict[str, tuple] = {}

    class FakeCarla(types.ModuleType):
        class Client:
            def __init__(self, host, port):
                calls["client"] = (host, port)

            def set_timeout(self, seconds):
                pass

    monkeypatch.setitem(sys.modules, "carla", FakeCarla("carla"))
    def fake_render_corpus(client, plan, lay, settings):
        calls["render"] = (lay.root,)
        return []

    def fake_detect_corpus(lay, weights, device, min_confidence):
        calls["detect"] = (device, min_confidence, dict(weights))
        return []

    monkeypatch.setattr(runner, "render_corpus", fake_render_corpus)
    monkeypatch.setattr(runner, "detect_corpus", fake_detect_corpus)

    code = runner.main(
        [
            "--corpus", str(layout.root),
            "--carla-host", "10.0.0.5",
            "--carla-port", "2100",
            "--device", "cpu",
            "--min-confidence", "0.4",
        ]
    )

    assert code == 0
    assert calls["client"] == ("10.0.0.5", 2100)
    assert calls["render"] == (layout.root,)
    assert calls["detect"][:2] == ("cpu", 0.4)
    assert set(calls["detect"][2]) == {"yolo11m", "rtdetr-l"}


def test_cli_skip_flags_run_neither_phase(tmp_path, monkeypatch) -> None:
    layout = make_rendered_corpus(tmp_path)
    monkeypatch.setattr(runner, "render_corpus", lambda *a, **k: pytest.fail("rendered"))
    monkeypatch.setattr(runner, "detect_corpus", lambda *a, **k: pytest.fail("detected"))

    assert runner.main(["--corpus", str(layout.root), "--skip-render", "--skip-detect"]) == 0
