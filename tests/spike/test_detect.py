"""Spec for converting detector output into scored-ready detections.

The detector is a real one (project rule: synthetic claims with a chosen
correlation parameter would assume the conclusion). This module only converts
and filters its output; it never invents or adjusts a detection.
"""

from __future__ import annotations

import pytest

from spike_dependence.detect import detections_from_prediction
from spike_dependence.instance_mask import VEHICLE_LABELS


class TestDetectionsFromPrediction:
    def test_converts_one_box(self) -> None:
        detections = detections_from_prediction(
            boxes=[(10.0, 20.0, 50.0, 60.0)],
            labels=["car"],
            confidences=[0.9],
            min_confidence=0.25,
        )

        (detection,) = detections
        assert detection.label == "car"
        assert detection.confidence == pytest.approx(0.9)
        assert (detection.box.x1, detection.box.y1) == (10.0, 20.0)
        assert (detection.box.x2, detection.box.y2) == (50.0, 60.0)

    def test_drops_labels_that_are_not_vehicles(self) -> None:
        detections = detections_from_prediction(
            boxes=[(10.0, 20.0, 50.0, 60.0), (0.0, 0.0, 5.0, 5.0)],
            labels=["car", "person"],
            confidences=[0.9, 0.95],
            min_confidence=0.25,
        )

        assert [d.label for d in detections] == ["car"]

    def test_keeps_every_vehicle_class_the_truth_can_contain(self) -> None:
        labels = sorted(set(VEHICLE_LABELS.values()))
        detections = detections_from_prediction(
            boxes=[(float(i), 0.0, float(i) + 5.0, 5.0) for i in range(len(labels))],
            labels=labels,
            confidences=[0.9] * len(labels),
            min_confidence=0.25,
        )

        assert sorted(d.label for d in detections) == labels

    def test_drops_detections_below_the_confidence_floor(self) -> None:
        detections = detections_from_prediction(
            boxes=[(10.0, 20.0, 50.0, 60.0), (0.0, 0.0, 5.0, 5.0)],
            labels=["car", "car"],
            confidences=[0.9, 0.10],
            min_confidence=0.25,
        )

        assert len(detections) == 1

    def test_drops_degenerate_boxes_instead_of_raising(self) -> None:
        # A zero-area box would raise inside BoundingBox; it must be skipped.
        detections = detections_from_prediction(
            boxes=[(10.0, 20.0, 10.0, 60.0), (0.0, 0.0, 5.0, 5.0)],
            labels=["car", "car"],
            confidences=[0.9, 0.9],
            min_confidence=0.25,
        )

        assert len(detections) == 1

    def test_empty_prediction_yields_nothing(self) -> None:
        assert detections_from_prediction(
            boxes=[], labels=[], confidences=[], min_confidence=0.25
        ) == []

    def test_rejects_ragged_input(self) -> None:
        with pytest.raises(ValueError, match="same length"):
            detections_from_prediction(
                boxes=[(0.0, 0.0, 5.0, 5.0)],
                labels=["car", "car"],
                confidences=[0.9],
                min_confidence=0.25,
            )
