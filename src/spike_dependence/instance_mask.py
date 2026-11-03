"""Turn a CARLA instance-segmentation frame into per-viewpoint ground truth.

Encoding verified empirically against CARLA 0.9.16 on 2026-11-03 (SD-013):
`carla.Image.raw_data` is BGRA; the red channel carries the semantic tag; the
actor id is `B * 256 + G`, with green as the low byte.

Ground truth is read from rendered pixels, not from projected 3D boxes. That
choice is what makes per-viewpoint visibility honest: an occluded object
occupies few or no pixels in that camera, so it never enters that agent's
visible set. Projecting 3D boxes could not tell occluded from visible and
would have quietly broken the shared-object rule in SD-008.

Simulator truth stops here. It labels detections and goes no further (AD-001).
"""

from __future__ import annotations

import numpy as np

from spike_dependence.scoring import BoundingBox, GroundTruthObject

CAR_TAG = 14
TRUCK_TAG = 15
BUS_TAG = 16
MOTORCYCLE_TAG = 18
BICYCLE_TAG = 19

# Labels are COCO class names so they compare directly with YOLO output.
VEHICLE_LABELS: dict[int, str] = {
    CAR_TAG: "car",
    TRUCK_TAG: "truck",
    BUS_TAG: "bus",
    MOTORCYCLE_TAG: "motorcycle",
    BICYCLE_TAG: "bicycle",
}

_BLUE, _GREEN, _RED = 0, 1, 2


def _require_bgra(frame: np.ndarray) -> None:
    """Raise unless the frame is a height x width x 4 BGRA array."""
    if frame.ndim != 3 or frame.shape[2] != 4:
        raise ValueError("instance frame must be a BGRA array of shape (h, w, 4)")


def decode_actor_ids(frame: np.ndarray) -> np.ndarray:
    """Return the per-pixel CARLA actor id decoded from blue and green."""
    _require_bgra(frame)
    blue = frame[:, :, _BLUE].astype(np.int32)
    green = frame[:, :, _GREEN].astype(np.int32)
    return blue * 256 + green


def ground_truth_from_instance_frame(
    frame: np.ndarray,
    *,
    min_pixels: int,
) -> list[GroundTruthObject]:
    """Return the vehicles this camera can actually see, with tight boxes.

    `min_pixels` is the visibility threshold. An actor rendered in fewer than
    that many pixels is treated as not visible from this viewpoint, which is
    how occlusion and extreme distance are handled.
    """
    _require_bgra(frame)
    if min_pixels < 1:
        raise ValueError("min_pixels must be at least 1")

    tags = frame[:, :, _RED].astype(np.int32)
    vehicle_mask = np.isin(tags, list(VEHICLE_LABELS))
    if not vehicle_mask.any():
        return []

    actor_ids = decode_actor_ids(frame)
    rows, cols = np.nonzero(vehicle_mask)
    visible_ids = actor_ids[rows, cols]

    objects: list[GroundTruthObject] = []
    for actor_id in np.unique(visible_ids):
        selected = visible_ids == actor_id
        if int(selected.sum()) < min_pixels:
            continue

        actor_rows, actor_cols = rows[selected], cols[selected]
        tag = int(tags[actor_rows[0], actor_cols[0]])
        objects.append(
            GroundTruthObject(
                object_id=f"actor-{int(actor_id)}",
                label=VEHICLE_LABELS[tag],
                # Max is exclusive so a single pixel still has unit area.
                box=BoundingBox(
                    x1=float(actor_cols.min()),
                    y1=float(actor_rows.min()),
                    x2=float(actor_cols.max() + 1),
                    y2=float(actor_rows.max() + 1),
                ),
            )
        )

    objects.sort(key=lambda obj: obj.object_id)
    return objects
