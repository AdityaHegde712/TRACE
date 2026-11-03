"""Phase 1: render the scene matrix from two viewpoints and write it to disk.

This is the only module that talks to CARLA. It computes nothing on its own:
the scene matrix and the camera geometry come from `scene_matrix`, and the
ground truth comes from `instance_mask`. Its job is to drive the simulator and
persist artifacts, then exit so Phase 2 has the GPU to itself (SD-003).

Run it detached; it logs one line per scene and flushes continuously.

    python -m spike_dependence.render_scenes --scenes 54 --out artifacts/spike/raw
"""

from __future__ import annotations

import argparse
import math
import queue
import random
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import numpy as np

from spike_dependence.artifacts_io import ground_truth_to_json, write_manifest
from spike_dependence.instance_mask import ground_truth_from_instance_frame
from spike_dependence.scene_matrix import (
    CameraPose,
    SceneSpec,
    build_scene_matrix,
    viewpoint_pair,
)

_SETTLE_TICKS = 12
_OCCLUDER_FRACTION = 0.40
_VIEWPOINT_ATTEMPTS = 12
_SKY_PROBE_M = 60.0


def _log(message: str) -> None:
    """Print one progress line and flush, so a tailed log stays current."""
    print(f"[{time.strftime('%H:%M:%S')}] {message}", flush=True)


def _latest(sensor_queue: queue.Queue) -> Any:
    """Return the most recent sensor image, discarding stale queued frames.

    `queue.get()` alone returns the OLDEST frame, which can predate the actors
    spawned for this scene. That failure is silent and yields wrong ground
    truth, so every sensor read goes through here (SD-014).
    """
    image = sensor_queue.get(timeout=30.0)
    while True:
        try:
            image = sensor_queue.get_nowait()
        except queue.Empty:
            return image


def _to_bgra(image: Any) -> np.ndarray:
    """Return a CARLA image as a height x width x 4 BGRA array."""
    return np.frombuffer(image.raw_data, dtype=np.uint8).reshape(
        image.height, image.width, 4
    )


@contextmanager
def _synchronous(world: Any, delta_seconds: float = 0.05) -> Iterator[None]:
    """Hold the world in synchronous mode, restoring the original settings."""
    original = world.get_settings()
    settings = world.get_settings()
    settings.synchronous_mode = True
    settings.fixed_delta_seconds = delta_seconds
    world.apply_settings(settings)
    try:
        yield
    finally:
        world.apply_settings(original)


def _carla_transform(carla: Any, pose: CameraPose) -> Any:
    """Convert one computed pose into a CARLA transform."""
    return carla.Transform(
        carla.Location(x=pose.x, y=pose.y, z=pose.z),
        carla.Rotation(pitch=pose.pitch, yaw=pose.yaw),
    )


def _has_clear_view(carla: Any, world: Any, pose: CameraPose) -> bool:
    """Return True when the camera is outdoors and can see the scene centre.

    Pure geometry has no idea where walls are, so an orbit point can land
    inside a building. Two ray casts catch that: one straight down from high
    above the camera, which hits a roof if the camera is indoors, and one from
    the camera to the centre, which hits anything standing between them.
    Both run BEFORE traffic is spawned, so only static geometry can block.
    """
    camera = carla.Location(x=pose.x, y=pose.y, z=pose.z)
    overhead = carla.Location(x=pose.x, y=pose.y, z=pose.z + _SKY_PROBE_M)
    if world.cast_ray(overhead, camera):
        return False

    target = carla.Location(
        x=pose.target[0], y=pose.target[1], z=pose.target[2] + 1.0
    )
    return not world.cast_ray(camera, target)


def _clear_viewpoint_pair(
    carla: Any,
    world: Any,
    scene: SceneSpec,
    centre: Any,
    *,
    radius_m: float,
    height_m: float,
) -> tuple[CameraPose, CameraPose] | None:
    """Rotate the camera pair until both cameras have an unobstructed view."""
    start = random.Random(scene.seed).uniform(0.0, 360.0)
    step = 360.0 / _VIEWPOINT_ATTEMPTS
    for attempt in range(_VIEWPOINT_ATTEMPTS):
        pose_a, pose_b = viewpoint_pair(
            scene,
            radius_m=radius_m,
            height_m=height_m,
            centre=(centre.x, centre.y, centre.z),
            base_angle_degrees=(start + attempt * step) % 360.0,
        )
        if _has_clear_view(carla, world, pose_a) and _has_clear_view(
            carla, world, pose_b
        ):
            return pose_a, pose_b
    return None


def _spawn_traffic(world: Any, centre: Any, vehicle_count: int, seed: int) -> list[Any]:
    """Spawn vehicles at the spawn points nearest the scene centre."""
    points = sorted(
        world.get_map().get_spawn_points(),
        key=lambda point: point.location.distance(centre),
    )
    blueprints = world.get_blueprint_library().filter("vehicle.*")
    rng = np.random.default_rng(seed)

    spawned: list[Any] = []
    for point in points[: vehicle_count * 3]:
        if len(spawned) >= vehicle_count:
            break
        blueprint = blueprints[int(rng.integers(len(blueprints)))]
        actor = world.try_spawn_actor(blueprint, point)
        if actor is not None:
            spawned.append(actor)
    return spawned


def _spawn_occluder(carla: Any, world: Any, centre: Any, pose: CameraPose) -> Any:
    """Place a large vehicle between one camera and the scene centre."""
    large = world.get_blueprint_library().filter("vehicle.carlamotors.*")
    if not large:
        large = world.get_blueprint_library().filter("vehicle.*")

    location = carla.Location(
        x=pose.x + (centre.x - pose.x) * _OCCLUDER_FRACTION,
        y=pose.y + (centre.y - pose.y) * _OCCLUDER_FRACTION,
        z=centre.z + 0.3,
    )
    yaw = math.degrees(math.atan2(centre.y - pose.y, centre.x - pose.x)) + 90.0
    return world.try_spawn_actor(large[0], carla.Transform(location, carla.Rotation(yaw=yaw)))


def _attach_cameras(
    carla: Any,
    world: Any,
    pose: CameraPose,
    *,
    width: int,
    height: int,
) -> tuple[list[Any], queue.Queue, queue.Queue]:
    """Attach an RGB and an instance-segmentation camera at one pose."""
    library = world.get_blueprint_library()
    transform = _carla_transform(carla, pose)

    sensors: list[Any] = []
    queues: list[queue.Queue] = []
    for sensor_name in ("rgb", "instance_segmentation"):
        blueprint = library.find(f"sensor.camera.{sensor_name}")
        blueprint.set_attribute("image_size_x", str(width))
        blueprint.set_attribute("image_size_y", str(height))
        camera = world.spawn_actor(blueprint, transform)
        sensor_queue: queue.Queue = queue.Queue()
        camera.listen(sensor_queue.put)
        sensors.append(camera)
        queues.append(sensor_queue)
    return sensors, queues[0], queues[1]


def render_scene(
    carla: Any,
    client: Any,
    scene: SceneSpec,
    out_dir: Path,
    *,
    width: int,
    height: int,
    radius_m: float,
    camera_height_m: float,
    vehicle_count: int,
    min_pixels: int,
) -> dict[str, int] | None:
    """Render one scene from both viewpoints and write its artifacts.

    Returns None when no unobstructed camera pair could be found, so the
    caller can record the scene as skipped rather than writing empty truth.
    """
    world = client.get_world()
    world.set_weather(getattr(carla.WeatherParameters, scene.weather.value))

    points = world.get_map().get_spawn_points()
    centre = points[scene.seed % len(points)].location

    # Line of sight is checked before any traffic exists, so only static
    # geometry can disqualify a viewpoint.
    poses = _clear_viewpoint_pair(
        carla, world, scene, centre,
        radius_m=radius_m, height_m=camera_height_m,
    )
    if poses is None:
        return None
    pose_a, pose_b = poses

    actors: list[Any] = []
    sensors: list[Any] = []
    try:
        actors.extend(_spawn_traffic(world, centre, vehicle_count, scene.seed))

        if scene.occluder:
            occluder = _spawn_occluder(carla, world, centre, pose_a)
            if occluder is not None:
                actors.append(occluder)

        captures: dict[str, tuple[queue.Queue, queue.Queue]] = {}
        for name, pose in (("a", pose_a), ("b", pose_b)):
            cameras, rgb_queue, seg_queue = _attach_cameras(
                carla,
                world,
                pose,
                width=width,
                height=height,
            )
            sensors.extend(cameras)
            captures[name] = (rgb_queue, seg_queue)

        for _ in range(_SETTLE_TICKS):
            world.tick()

        scene_dir = out_dir / scene.scene_id
        scene_dir.mkdir(parents=True, exist_ok=True)
        counts: dict[str, int] = {}
        for name, (rgb_queue, seg_queue) in captures.items():
            _latest(rgb_queue).save_to_disk(str(scene_dir / f"rgb_{name}.png"))
            objects = ground_truth_from_instance_frame(
                _to_bgra(_latest(seg_queue)), min_pixels=min_pixels
            )
            ground_truth_to_json(objects, scene_dir / f"gt_{name}.json")
            counts[name] = len(objects)
        return counts
    finally:
        for sensor in sensors:
            sensor.stop()
            sensor.destroy()
        for actor in actors:
            actor.destroy()


def run(args: argparse.Namespace) -> int:
    """Render every scene in the matrix, grouping by town to limit reloads."""
    import carla  # Imported here so this module stays importable without CARLA.

    out_dir = Path(args.out)
    scenes = build_scene_matrix(args.scenes, seed=args.seed)
    write_manifest(
        scenes,
        out_dir / "manifest.json",
        extra={
            "min_pixels": args.min_pixels,
            "width": args.width,
            "height": args.height,
            "radius_m": args.radius,
            "camera_height_m": args.camera_height,
            "vehicle_count": args.vehicles,
            "matrix_seed": args.seed,
        },
    )
    _log(f"manifest written; {len(scenes)} scenes planned -> {out_dir}")

    client = carla.Client(args.host, args.port)
    client.set_timeout(args.timeout)
    _log(f"connected; server {client.get_server_version()}")

    # client.load_world() crashes this server (SD-016), so the town is fixed by
    # how CarlaUE4.exe was launched and every scene runs against it.
    loaded_map = client.get_world().get_map().name
    _log(f"server map: {loaded_map}")

    rendered = 0
    skipped: list[str] = []
    started = time.time()

    for scene in scenes:
        with _synchronous(client.get_world()):
            counts = render_scene(
                carla,
                client,
                scene,
                out_dir,
                width=args.width,
                height=args.height,
                radius_m=args.radius,
                camera_height_m=args.camera_height,
                vehicle_count=args.vehicles,
                min_pixels=args.min_pixels,
            )
        rendered += 1
        if counts is None:
            skipped.append(scene.scene_id)
            _log(
                f"{scene.scene_id} [{rendered}/{len(scenes)}] SKIPPED: "
                f"no unobstructed camera pair at this centre"
            )
            continue
        _log(
            f"{scene.scene_id} [{rendered}/{len(scenes)}] "
            f"{scene.weather.value} overlap={scene.overlap.value} "
            f"occluder={scene.occluder} -> visible A={counts['a']} B={counts['b']}"
        )

    _log(
        f"DONE: {rendered - len(skipped)} rendered, {len(skipped)} skipped, "
        f"in {time.time() - started:.0f}s -> {out_dir}"
    )
    if skipped:
        _log(f"skipped scenes: {', '.join(skipped)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and render the matrix."""
    parser = argparse.ArgumentParser(description="Render the dependence spike scenes.")
    parser.add_argument("--scenes", type=int, default=54)
    parser.add_argument("--out", default="artifacts/spike/raw")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=2000)
    parser.add_argument("--timeout", type=float, default=120.0)
    parser.add_argument("--width", type=int, default=800)
    parser.add_argument("--height", type=int, default=600)
    parser.add_argument("--radius", type=float, default=22.0)
    parser.add_argument("--camera-height", type=float, default=14.0)
    parser.add_argument("--vehicles", type=int, default=12)
    parser.add_argument("--min-pixels", type=int, default=50)
    return run(parser.parse_args(argv))


if __name__ == "__main__":
    sys.exit(main())
