"""Independent mmap world and serial A/B lineage over the frozen collision law.

The module owns experiments, surfaces and witnesses.  ``growth_carrier.py`` is
source-hash frozen and imported without modification; one CPU continuation
crosses BODY and WORLD through explicit handles stored in their mmap records.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
import hashlib
import math
from pathlib import Path
import random
import shutil
from typing import Iterable, Sequence

import growth_carrier as core
from growth_carrier import (
    Collision,
    CollisionKind,
    FREE,
    GESTURE_0,
    GESTURE_1,
    MaterialRecord,
    MmapBody,
    NO_HANDLE,
    Place,
    collision,
    execute_lane,
)


ROOT = Path(__file__).resolve().parent
IMMUTABLE_KERNEL_SHA256 = "0d32047eecb391f572671a3404eb912fa3cc96ea3a39a44212328d5884d312f7"

BODY_SURFACE = 0
WORLD_SURFACE = 1
SURFACE_SHIFT = 24
LOCAL_MASK = (1 << SURFACE_SHIFT) - 1
BODY_CAPACITY = 1024
WORLD_SIZE = 5
PRELUDE_COUNT = 510
RETURN_ROUTE_COUNT = 256
# Every branch receives the same finite amount of actual CPU continuation.
# A larger world therefore creates a real delay instead of silently receiving
# more execution merely because it contains more mmap records.
COLLISION_BUDGET = 2 * (BODY_CAPACITY + WORLD_SIZE)
DELAY_WORLD_SIZE = COLLISION_BUDGET
CONDITIONS = (
    "matched",
    "no_world",
    "passive",
    "disconnected",
    "mismatched",
    "delay",
    "permute",
    "shuffle",
)


def kernel_sha256() -> str:
    return hashlib.sha256((ROOT / "growth_carrier.py").read_bytes()).hexdigest()


def assert_immutable_kernel() -> None:
    actual = kernel_sha256()
    if actual != IMMUTABLE_KERNEL_SHA256:
        raise RuntimeError(
            f"world-lineage requires frozen kernel {IMMUTABLE_KERNEL_SHA256}, got {actual}"
        )


def encode_handle(surface: int, local_address: int) -> int:
    if not 0 <= surface < 255:
        raise ValueError("surface does not fit an explicit handle")
    if not 0 <= local_address <= LOCAL_MASK:
        raise ValueError("local address does not fit an explicit handle")
    return (int(surface) << SURFACE_SHIFT) | int(local_address)


def decode_handle(handle: int) -> tuple[int, int]:
    if handle == NO_HANDLE:
        raise ValueError("NO_HANDLE has no material surface")
    return int(handle) >> SURFACE_SHIFT, int(handle) & LOCAL_MASK


def body_place(local_address: int) -> Place:
    return Place(encode_handle(BODY_SURFACE, local_address))


def world_place(local_address: int) -> Place:
    return Place(encode_handle(WORLD_SURFACE, local_address))


def surface_of(place: Place | None) -> int | None:
    return None if place is None else decode_handle(place.address)[0]


class MultiMmapArena:
    """Duck-typed material owner used by the unchanged collision function."""

    def __init__(self, body: MmapBody, world: MmapBody | None = None):
        self.body = body
        self.world = world

    def _surface(self, surface: int) -> MmapBody | None:
        if surface == BODY_SURFACE:
            return self.body
        if surface == WORLD_SURFACE:
            return self.world
        return None

    def read(self, place: Place) -> MaterialRecord:
        surface, local = decode_handle(place.address)
        mapped = self._surface(surface)
        if mapped is None:
            raise IndexError(place.address)
        return mapped.read(local)

    def resolve(self, handle: int) -> Place | None:
        if handle == NO_HANDLE:
            return None
        surface, local = decode_handle(handle)
        mapped = self._surface(surface)
        if mapped is None or not 0 <= local < mapped.capacity:
            return None
        return Place(handle)

    def contact(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.contact_handle)

    def port(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.port_handle)

    def back(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.birth_handle)

    def return_from(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.return_handle)

    def upper_slot(self, record: MaterialRecord) -> Place | None:
        return self.resolve(record.upper_handle)

    def _store(self, place: int | Place, record: MaterialRecord) -> None:
        material_place = place if isinstance(place, Place) else Place(int(place))
        surface, local = decode_handle(material_place.address)
        mapped = self._surface(surface)
        if mapped is None:
            raise IndexError(material_place.address)
        handles = (
            record.contact_handle,
            record.port_handle,
            record.birth_handle,
            record.return_handle,
            record.upper_handle,
        )
        for handle in handles:
            if handle != NO_HANDLE:
                linked_surface, linked_local = decode_handle(handle)
                linked = self._surface(linked_surface)
                if linked is not None and not 0 <= linked_local < linked.capacity:
                    raise IndexError(handle)
        core._RECORD.pack_into(
            mapped._mmap,
            mapped._offset(local),
            int(record.gesture),
            *map(int, handles),
        )


@dataclass(frozen=True)
class BodyLayout:
    origin: Place
    upper: Place
    prelude: tuple[Place, ...]
    route_a: tuple[Place, ...]
    route_b: tuple[Place, ...]

    def route(self, line: str) -> tuple[Place, ...]:
        if line == "A":
            return self.route_a
        if line == "B":
            return self.route_b
        raise ValueError(f"unknown lineage {line}")


def canonical_layout() -> BodyLayout:
    upper = body_place(0)
    origin = body_place(1)
    prelude = tuple(body_place(address) for address in range(2, 2 + PRELUDE_COUNT))
    route_a_start = 2 + PRELUDE_COUNT
    route_a = tuple(
        body_place(address)
        for address in range(route_a_start, route_a_start + RETURN_ROUTE_COUNT)
    )
    route_b = tuple(
        body_place(address)
        for address in range(route_a_start + RETURN_ROUTE_COUNT, BODY_CAPACITY)
    )
    if len(route_a) != RETURN_ROUTE_COUNT or len(route_b) != RETURN_ROUTE_COUNT:
        raise AssertionError("1024-body partition drifted")
    return BodyLayout(origin, upper, prelude, route_a, route_b)


def _store_existing_route(
    arena: MultiMmapArena,
    route: tuple[Place, ...],
    origin: Place,
) -> None:
    gesture = GESTURE_1
    for offset, place in enumerate(route):
        following = route[offset + 1] if offset + 1 < len(route) else origin
        arena._store(
            place,
            MaterialRecord(
                gesture=gesture,
                contact_handle=following.address,
                port_handle=following.address,
            ),
        )
        gesture = -gesture


def create_damaged_body(path: Path) -> tuple[MmapBody, BodyLayout]:
    """Create one 1024-place half-cut shared by every A/B history."""
    assert_immutable_kernel()
    layout = canonical_layout()
    body = MmapBody.create(path, BODY_CAPACITY)
    arena = MultiMmapArena(body)
    arena._store(
        layout.upper,
        MaterialRecord(
            gesture=FREE,
            contact_handle=layout.origin.address,
        ),
    )
    arena._store(
        layout.origin,
        MaterialRecord(
            gesture=GESTURE_1,
            contact_handle=layout.prelude[0].address,
            port_handle=layout.prelude[0].address,
            upper_handle=layout.upper.address,
        ),
    )
    for offset, place in enumerate(layout.prelude):
        following = (
            layout.prelude[offset + 1]
            if offset + 1 < len(layout.prelude)
            else world_place(0)
        )
        arena._store(
            place,
            MaterialRecord(
                gesture=FREE,
                contact_handle=following.address,
            ),
        )
    _store_existing_route(arena, layout.route_a, layout.origin)
    _store_existing_route(arena, layout.route_b, layout.origin)
    body.flush()
    return body, layout


def _world_order(size: int, seed: int) -> tuple[int, ...]:
    tail = list(range(1, size))
    random.Random(seed).shuffle(tail)
    return (0, *tail)


def _expected_world_gestures(size: int) -> tuple[int, ...]:
    gesture = GESTURE_0
    result = []
    for _ in range(size):
        result.append(gesture)
        gesture = -gesture
    return tuple(result)


def create_world(
    body: MmapBody,
    path: Path,
    layout: BodyLayout,
    *,
    line: str,
    seed: int,
    condition: str,
) -> tuple[MmapBody, MultiMmapArena, tuple[int, ...]]:
    if condition == "delay":
        size = DELAY_WORLD_SIZE
    elif condition == "mismatched":
        size = WORLD_SIZE + 1
    else:
        size = WORLD_SIZE
    world = MmapBody.create(path, size)
    arena = MultiMmapArena(body, world)
    order = _world_order(size, seed)
    return_line = ("B" if line == "A" else "A") if condition == "permute" else line
    target = layout.route(return_line)[0]
    gestures = _expected_world_gestures(size)

    for offset, local in enumerate(order):
        following = (
            world_place(order[offset + 1])
            if offset + 1 < len(order)
            else target
        )
        place = world_place(local)
        if condition == "passive" and offset == 0:
            arena._store(
                place,
                MaterialRecord(
                    # The world presents matter at the contact, but does not
                    # execute an action-dependent transition.  Matching the
                    # incoming body's gesture reflects the passage without a
                    # prewritten birth or return relation.
                    gesture=-gestures[offset],
                    contact_handle=following.address,
                ),
            )
        elif condition == "passive":
            arena._store(
                place,
                MaterialRecord(
                    gesture=FREE,
                    contact_handle=following.address,
                ),
            )
        elif condition == "shuffle":
            wrong = GESTURE_1 if offset == 0 else gestures[offset]
            arena._store(
                place,
                MaterialRecord(
                    gesture=wrong,
                    contact_handle=following.address,
                    port_handle=following.address,
                ),
            )
        else:
            arena._store(
                place,
                MaterialRecord(
                    gesture=FREE,
                    contact_handle=following.address,
                ),
            )
    world.flush()
    return world, arena, order


def create_disconnected_world(
    body: MmapBody,
    path: Path,
) -> tuple[MmapBody, MultiMmapArena]:
    world = MmapBody.create(path, WORLD_SIZE)
    arena = MultiMmapArena(body, world)
    arena._store(
        world_place(0),
        MaterialRecord(
            gesture=GESTURE_1,
            contact_handle=world_place(1).address,
            port_handle=world_place(1).address,
        ),
    )
    for local in range(1, WORLD_SIZE):
        following = world_place(local + 1) if local + 1 < WORLD_SIZE else None
        arena._store(
            world_place(local),
            MaterialRecord(
                gesture=FREE,
                contact_handle=(NO_HANDLE if following is None else following.address),
            ),
        )
    world.flush()
    return world, arena


def trace_summary(trace: tuple[Collision, ...]) -> dict:
    kinds = Counter(event.kind.value for event in trace)
    body_to_world = sum(
        surface_of(event.current) == BODY_SURFACE
        and surface_of(event.continuation) == WORLD_SURFACE
        for event in trace
    )
    world_to_body = sum(
        surface_of(event.current) == WORLD_SURFACE
        and surface_of(event.continuation) == BODY_SURFACE
        for event in trace
    )
    changed_body = {
        place.address
        for event in trace
        for place in event.changed
        if surface_of(place) == BODY_SURFACE
    }
    changed_world = {
        place.address
        for event in trace
        for place in event.changed
        if surface_of(place) == WORLD_SURFACE
    }
    return {
        "kind_counts": dict(sorted(kinds.items())),
        "body_to_world": body_to_world,
        "world_to_body": world_to_body,
        "changed_body_places": len(changed_body),
        "changed_world_places": len(changed_world),
        "visited_surfaces": sorted(
            {surface_of(event.current) for event in trace if event.current is not None}
        ),
    }


def world_return_was_earned(trace: tuple[Collision, ...]) -> bool:
    changed_world: set[Place] = set()
    for event in trace:
        if (
            surface_of(event.current) == WORLD_SURFACE
            and surface_of(event.continuation) == BODY_SURFACE
            and event.kind in (CollisionKind.PASS, CollisionKind.MATERIALIZE)
            and event.current in changed_world
        ):
            return True
        changed_world.update(
            place for place in event.changed if surface_of(place) == WORLD_SURFACE
        )
    return False


def _upper_place(arena: MultiMmapArena, layout: BodyLayout) -> Place:
    upper = arena.upper_slot(arena.read(layout.origin))
    if upper is None:
        raise RuntimeError("body lost its explicit upper slot")
    return upper


def _upper_birth(trace: tuple[Collision, ...], upper: Place) -> tuple[int, Collision] | None:
    for index, event in enumerate(trace, start=1):
        if upper in event.changed and event.kind is CollisionKind.MATERIALIZE:
            return index, event
    return None


def body_material_count(body: MmapBody) -> int:
    return sum(body.read(local).gesture != FREE for local in range(body.capacity))


def body_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_branch(
    source_body: Path,
    root: Path,
    layout: BodyLayout,
    *,
    line: str,
    seed: int,
    condition: str,
    start_at_upper: bool = False,
) -> dict:
    if condition not in CONDITIONS:
        raise ValueError(condition)
    root.mkdir(parents=True, exist_ok=True)
    body_path = root / "BODY.mmap"
    world_path = root / "WORLD.mmap"
    shutil.copyfile(source_body, body_path)
    body = MmapBody.open(body_path)
    world: MmapBody | None = None
    world_before: bytes | None = None
    independent_world_changed = False

    if condition == "no_world":
        arena = MultiMmapArena(body)
    elif condition == "disconnected":
        world, world_arena = create_disconnected_world(body, world_path)
        world_before = world.snapshot()
        execute_lane(world_arena, world_place(0), 2, capture_trace=False)
        independent_world_changed = world.snapshot() != world_before
        arena = MultiMmapArena(body)
    else:
        world, arena, _order = create_world(
            body,
            world_path,
            layout,
            line=line,
            seed=seed,
            condition=condition,
        )
        world_before = world.snapshot()

    body_before = body.snapshot()
    body_before_sha256 = hashlib.sha256(body_before).hexdigest()
    upper = _upper_place(arena, layout)
    start = upper if start_at_upper and not arena.read(upper).free else layout.origin
    run = execute_lane(arena, start, COLLISION_BUDGET, capture_trace=True)
    body_after = body.snapshot()
    world_after = None if world is None else world.snapshot()
    summary = trace_summary(run.trace)
    birth = _upper_birth(run.trace, upper)
    upper_born = not arena.read(upper).free
    coarse_event = collision(arena, upper) if upper_born else None
    origin_return = arena.return_from(arena.read(layout.origin))
    result = {
        "condition": condition,
        "line": line,
        "seed": seed,
        "body_path": str(body_path),
        "body_before_sha256": body_before_sha256,
        "body_sha256": hashlib.sha256(body_after).hexdigest(),
        "body_changed": body_after != body_before,
        "body_material_count": body_material_count(body),
        "upper_born": upper_born,
        "upper_birth_collision": None if birth is None else birth[0],
        "coarse_pass": coarse_event is not None
        and coarse_event.kind is CollisionKind.PASS
        and coarse_event.met == layout.origin,
        "origin_return_handle": (
            None if origin_return is None else origin_return.address
        ),
        "trace": summary,
        "world_return_earned_by_prior_world_change": world_return_was_earned(
            run.trace
        ),
        "world_changed": independent_world_changed
        or (
            world_before is not None
            and world_after is not None
            and world_before != world_after
        ),
        "world_sha256_before_washout": (
            None if world_after is None else hashlib.sha256(world_after).hexdigest()
        ),
    }
    body.flush()
    if world is not None:
        world.close()
        world_path.unlink()
    body.close()
    result["world_deleted"] = not world_path.exists()
    return result


def _flat_node_keys() -> tuple[tuple[int, int], ...]:
    return tuple(
        [(BODY_SURFACE, local) for local in range(BODY_CAPACITY)]
        + [(WORLD_SURFACE, local) for local in range(WORLD_SIZE)]
    )


def _hostile_flat_permutation(
    nodes: tuple[tuple[int, int], ...],
) -> dict[tuple[int, int], int]:
    """Mix both former surfaces into one deterministic, fixed-point-free field."""
    capacity = len(nodes)
    multiplier = 100
    offset = 1
    if math.gcd(multiplier, capacity) != 1:
        raise AssertionError("flat permutation multiplier must be invertible")
    permutation = {
        node: (multiplier * canonical + offset) % capacity
        for canonical, node in enumerate(nodes)
    }
    if sorted(permutation.values()) != list(range(capacity)):
        raise AssertionError("flat permutation must cover every address exactly once")
    if any(permutation[node] == canonical for canonical, node in enumerate(nodes)):
        raise AssertionError("flat permutation must move every material node")
    return permutation


def _remap_surface_handle(
    handle: int,
    permutation: dict[tuple[int, int], int],
) -> int:
    if handle == NO_HANDLE:
        return NO_HANDLE
    return permutation[decode_handle(handle)]


def _flatten_record(
    record: MaterialRecord,
    permutation: dict[tuple[int, int], int],
) -> MaterialRecord:
    return MaterialRecord(
        gesture=record.gesture,
        contact_handle=_remap_surface_handle(record.contact_handle, permutation),
        port_handle=_remap_surface_handle(record.port_handle, permutation),
        birth_handle=_remap_surface_handle(record.birth_handle, permutation),
        return_handle=_remap_surface_handle(record.return_handle, permutation),
        upper_handle=_remap_surface_handle(record.upper_handle, permutation),
    )


def _flatten_place(
    place: Place | None,
    permutation: dict[tuple[int, int], int],
) -> Place | None:
    if place is None:
        return None
    return Place(permutation[decode_handle(place.address)])


def _flatten_collision(
    event: Collision,
    permutation: dict[tuple[int, int], int],
) -> Collision:
    current = _flatten_place(event.current, permutation)
    if current is None:
        raise AssertionError("a collision must have a current place")
    return Collision(
        kind=event.kind,
        current=current,
        met=_flatten_place(event.met, permutation),
        continuation=_flatten_place(event.continuation, permutation),
        changed=tuple(
            mapped
            for place in event.changed
            if (mapped := _flatten_place(place, permutation)) is not None
        ),
    )


def _surface_record(
    body: MmapBody,
    world: MmapBody,
    node: tuple[int, int],
) -> MaterialRecord:
    surface, local = node
    if surface == BODY_SURFACE:
        return body.read(local)
    if surface == WORLD_SURFACE:
        return world.read(local)
    raise AssertionError(f"unknown material surface {surface}")


def _record_handles(record: MaterialRecord) -> tuple[int, ...]:
    return (
        record.contact_handle,
        record.port_handle,
        record.birth_handle,
        record.return_handle,
        record.upper_handle,
    )


def single_mmap_flattening_control(
    root: Path,
    *,
    line: str = "A",
    seed: int = 17,
) -> dict:
    """Replay one matched two-surface passage in one hostilely permuted mmap.

    The witness retains the former surface identity only to construct and audit
    the isomorphism.  The flat execution runs the frozen ``collision`` directly
    over one ``MmapBody`` whose handles are ordinary local addresses.
    """
    assert_immutable_kernel()
    root.mkdir(parents=True, exist_ok=True)
    body_path = root / "two_surface_BODY.mmap"
    world_path = root / "two_surface_WORLD.mmap"
    flat_path = root / "flat_single_MATERIAL.mmap"
    body, layout = create_damaged_body(body_path)
    world: MmapBody | None = None
    flat: MmapBody | None = None
    try:
        world, arena, _order = create_world(
            body,
            world_path,
            layout,
            line=line,
            seed=seed,
            condition="matched",
        )
        nodes = _flat_node_keys()
        flat_capacity = len(nodes)
        permutation = _hostile_flat_permutation(nodes)
        flat = MmapBody.create(flat_path, flat_capacity)

        for node in nodes:
            flat._store(
                permutation[node],
                _flatten_record(_surface_record(body, world, node), permutation),
            )
        flat.flush()

        initial_records_isomorphic = all(
            _flatten_record(_surface_record(body, world, node), permutation)
            == flat.read(permutation[node])
            for node in nodes
        )
        initial_flat_handles = tuple(
            handle
            for address in range(flat_capacity)
            for handle in _record_handles(flat.read(address))
            if handle != NO_HANDLE
        )
        standard = execute_lane(
            arena,
            layout.origin,
            COLLISION_BUDGET,
            capture_trace=True,
        )
        flat_origin = _flatten_place(layout.origin, permutation)
        if flat_origin is None:
            raise AssertionError("flat origin cannot be absent")
        flattened = execute_lane(
            flat,
            flat_origin,
            COLLISION_BUDGET,
            capture_trace=True,
        )

        mapped_standard_trace = tuple(
            _flatten_collision(event, permutation) for event in standard.trace
        )
        trace_isomorphic = mapped_standard_trace == flattened.trace
        stop_isomorphic = (
            _flatten_place(standard.stop.start, permutation) == flattened.stop.start
            and _flatten_place(standard.stop.final, permutation) == flattened.stop.final
            and standard.stop.collisions == flattened.stop.collisions
            and standard.stop.halted == flattened.stop.halted
        )
        final_records_isomorphic = all(
            _flatten_record(_surface_record(body, world, node), permutation)
            == flat.read(permutation[node])
            for node in nodes
        )

        flat_records = tuple(flat.read(address) for address in range(flat_capacity))
        flat_handles = tuple(
            handle
            for record in flat_records
            for handle in _record_handles(record)
            if handle != NO_HANDLE
        )
        every_flat_handle = initial_flat_handles + flat_handles
        standard_summary = trace_summary(standard.trace)
        world_flat_addresses = tuple(
            permutation[(WORLD_SURFACE, local)] for local in range(WORLD_SIZE)
        )
        body_flat_addresses = tuple(
            permutation[(BODY_SURFACE, local)] for local in range(BODY_CAPACITY)
        )
        checks = {
            "frozen_collision_kernel_exact": kernel_sha256()
            == IMMUTABLE_KERNEL_SHA256,
            "one_flat_MmapBody_used_directly": type(flat) is MmapBody,
            "all_1029_nodes_permuted_once": sorted(permutation.values())
            == list(range(flat_capacity)),
            "every_node_moved_from_canonical_address": all(
                permutation[node] != canonical
                for canonical, node in enumerate(nodes)
            ),
            "former_BODY_and_WORLD_nodes_mixed": any(
                address < BODY_CAPACITY for address in world_flat_addresses
            )
            and any(address >= BODY_CAPACITY for address in body_flat_addresses)
            and max(world_flat_addresses) - min(world_flat_addresses) > WORLD_SIZE,
            "initial_records_isomorphic": initial_records_isomorphic,
            "matched_crossed_BODY_to_WORLD": standard_summary["body_to_world"] > 0,
            "matched_returned_WORLD_to_BODY": standard_summary["world_to_body"] > 0,
            "matched_return_was_earned": world_return_was_earned(standard.trace),
            "entire_collision_trace_isomorphic": trace_isomorphic,
            "lane_stop_isomorphic": stop_isomorphic,
            "all_final_MaterialRecords_isomorphic": final_records_isomorphic,
            "all_flat_handles_within_capacity": all(
                0 <= handle < flat_capacity for handle in every_flat_handle
            ),
            "no_surface_namespace_in_flat_handles": all(
                handle >> SURFACE_SHIFT == 0 for handle in every_flat_handle
            ),
        }
        return {
            "artifact_kind": "single_mmap_surface_flattening_control",
            "claim": "matched_pass_isomorphic_without_surface_namespace",
            "line": line,
            "seed": seed,
            "kernel_sha256": kernel_sha256(),
            "flat_capacity": flat_capacity,
            "node_counts": {
                "former_BODY": BODY_CAPACITY,
                "former_WORLD": WORLD_SIZE,
            },
            "permutation": {
                "kind": "affine_fixed_point_free",
                "multiplier": 100,
                "offset": 1,
                "former_WORLD_flat_addresses": list(world_flat_addresses),
            },
            "collision_counts": {
                "two_surface": len(standard.trace),
                "flat_single_mmap": len(flattened.trace),
            },
            "two_surface_crossings": {
                "BODY_to_WORLD": standard_summary["body_to_world"],
                "WORLD_to_BODY": standard_summary["world_to_body"],
            },
            "final_record_count": flat_capacity,
            "checks": checks,
            "passed": all(checks.values()),
        }
    finally:
        if flat is not None:
            flat.close()
        if world is not None:
            world.close()
        body.close()


FUTURE_BEHAVIOR_FIELDS = (
    "washout_body_changed",
    "washout_upper_birth_collision",
    "washout_material_count",
    "washout_coarse_pass",
    "washout_changed_body_places",
    "recut_body_changed",
    "recut_upper_birth_collision",
    "recut_material_count",
    "recut_coarse_pass",
    "recut_changed_body_places",
)


def _collision_number(value: int | None) -> int:
    return -1 if value is None else int(value)


def future_behavior_probe(
    source_body: Path,
    root: Path,
    layout: BodyLayout,
    *,
    seed: int,
) -> dict:
    """Read a branch through the same later world and the same later cut.

    The signature contains only changes and timing in BODY.  World causality is
    checked as protocol integrity, but world hashes and world-change counts do
    not decide whether a control separated from matched.
    """
    source_sha256 = body_sha256(source_body)
    washout = run_branch(
        source_body,
        root / "common_washout",
        layout,
        line="A",
        seed=seed + 700_001,
        condition="matched",
        start_at_upper=True,
    )
    recut = recut_upper(
        Path(washout["body_path"]),
        root / "recut_BODY.mmap",
        layout,
    )
    after_recut = run_branch(
        Path(recut["body_path"]),
        root / "after_recut",
        layout,
        line="A",
        seed=seed + 1_700_003,
        condition="matched",
    )
    signature = {
        "washout_body_changed": int(washout["body_changed"]),
        "washout_upper_birth_collision": _collision_number(
            washout["upper_birth_collision"]
        ),
        "washout_material_count": washout["body_material_count"],
        "washout_coarse_pass": int(washout["coarse_pass"]),
        "washout_changed_body_places": washout["trace"][
            "changed_body_places"
        ],
        "recut_body_changed": int(after_recut["body_changed"]),
        "recut_upper_birth_collision": _collision_number(
            after_recut["upper_birth_collision"]
        ),
        "recut_material_count": after_recut["body_material_count"],
        "recut_coarse_pass": int(after_recut["coarse_pass"]),
        "recut_changed_body_places": after_recut["trace"][
            "changed_body_places"
        ],
    }
    checks = {
        "probe_started_from_resulting_BODY": washout["body_before_sha256"]
        == source_sha256,
        "washout_return_was_earned": washout[
            "world_return_earned_by_prior_world_change"
        ],
        "washout_world_deleted": washout["world_deleted"],
        "recut_used_exact_washout_BODY": recut["source_sha256"]
        == washout["body_sha256"],
        "same_external_recut_applied": recut["upper_cut"],
        "recut_return_was_earned": after_recut[
            "world_return_earned_by_prior_world_change"
        ],
        "recut_world_deleted": after_recut["world_deleted"],
    }
    return {
        "source_body_sha256": source_sha256,
        "washout": washout,
        "recut": recut,
        "after_recut": after_recut,
        "signature": signature,
        "checks": checks,
        "passed": all(checks.values()),
    }


def _future_signature_tuple(probe: dict) -> tuple[int, ...]:
    return tuple(int(probe["signature"][name]) for name in FUTURE_BEHAVIOR_FIELDS)


def run_paired_conditions(
    source_body: Path,
    root: Path,
    layout: BodyLayout,
    *,
    line: str,
    seed: int,
) -> dict:
    branches = {
        condition: run_branch(
            source_body,
            root / condition,
            layout,
            line=line,
            seed=seed,
            condition=condition,
        )
        for condition in CONDITIONS
    }
    matched = branches["matched"]
    input_hashes = {branch["body_before_sha256"] for branch in branches.values()}
    future_behavior = {
        condition: future_behavior_probe(
            Path(branch["body_path"]),
            root / "future_behavior" / condition,
            layout,
            seed=seed,
        )
        for condition, branch in branches.items()
    }
    matched_future = _future_signature_tuple(future_behavior["matched"])
    separations = {
        condition: {
            "BODY": branches[condition]["body_sha256"] != matched["body_sha256"],
            "future_behavior": _future_signature_tuple(future_behavior[condition])
            != matched_future,
        }
        for condition in CONDITIONS
        if condition != "matched"
    }
    for separation in separations.values():
        separation["passed"] = separation["BODY"] and separation["future_behavior"]
    checks = {
        "matched_crossed_into_independent_world": matched["trace"]["body_to_world"] > 0,
        "matched_returned_from_independent_world": matched["trace"]["world_to_body"] > 0,
        "matched_changed_world": matched["world_changed"],
        "matched_return_was_earned_by_world_change": matched[
            "world_return_earned_by_prior_world_change"
        ],
        "matched_closed_upper_relation": matched["upper_born"] and matched["coarse_pass"],
        "all_branches_started_from_same_body": len(input_hashes) == 1,
        "all_worlds_deleted": all(branch["world_deleted"] for branch in branches.values()),
        "all_future_probes_causal_and_deleted": all(
            probe["passed"] for probe in future_behavior.values()
        ),
        "every_control_changed_BODY_differently": all(
            separation["BODY"] for separation in separations.values()
        ),
        "every_control_changed_future_behavior_differently": all(
            separation["future_behavior"] for separation in separations.values()
        ),
        "all_paired_controls_separated": all(
            separation["passed"] for separation in separations.values()
        ),
        "passive_did_not_change_world_or_close": not branches["passive"][
            "world_changed"
        ]
        and branches["passive"]["trace"]["world_to_body"] == 0
        and not branches["passive"]["world_return_earned_by_prior_world_change"]
        and not branches["passive"]["upper_born"]
        and not branches["passive"]["coarse_pass"],
    }
    return {
        "line": line,
        "seed": seed,
        "matched_body": matched["body_path"],
        "branches": branches,
        "future_behavior": future_behavior,
        "separations": separations,
        "checks": checks,
        "passed": all(checks.values()),
    }


def cut_to_shared_damage(
    formed_body: Path,
    target: Path,
    expected_damaged: Path,
    layout: BodyLayout,
) -> dict:
    shutil.copyfile(formed_body, target)
    body = MmapBody.open(target)
    arena = MultiMmapArena(body)
    for local in range(body.capacity):
        place = body_place(local)
        record = arena.read(place)
        if place == layout.upper or record.born_here:
            arena._store(
                place,
                MaterialRecord(
                    gesture=FREE,
                    contact_handle=record.contact_handle,
                    upper_handle=record.upper_handle,
                ),
            )
        elif record.carries_return:
            arena._store(place, replace(record, return_handle=NO_HANDLE))
    body.flush()
    material_count = body_material_count(body)
    body.close()
    exact = target.read_bytes() == expected_damaged.read_bytes()
    return {
        "body_path": str(target),
        "exact_shared_snapshot": exact,
        "material_count": material_count,
        "sha256": body_sha256(target),
    }


def recut_upper(source: Path, target: Path, layout: BodyLayout) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    source_sha256 = body_sha256(source)
    shutil.copyfile(source, target)
    body = MmapBody.open(target)
    arena = MultiMmapArena(body)
    upper = _upper_place(arena, layout)
    before = arena.read(upper)
    arena._store(
        upper,
        MaterialRecord(
            gesture=FREE,
            contact_handle=before.contact_handle,
            upper_handle=before.upper_handle,
        ),
    )
    body.flush()
    cut = arena.read(upper).free
    body.close()
    return {
        "body_path": str(target),
        "source_body": str(source),
        "source_sha256": source_sha256,
        "upper_cut": cut,
        "upper_handle": upper.address,
        "sha256": body_sha256(target),
    }


def ordinary_life_baseline(
    body_path: Path,
    root: Path,
    layout: BodyLayout,
    *,
    line: str,
    seed: int,
    worlds: int = 3,
) -> dict:
    episodes = [
        run_branch(
            body_path,
            root / f"world_{episode}",
            layout,
            line=line,
            seed=seed + episode * 10_007,
            condition="matched",
            start_at_upper=True,
        )
        for episode in range(worlds)
    ]
    checks = {
        "all_fresh_worlds_deleted": all(item["world_deleted"] for item in episodes),
        "all_worlds_changed_by_action": all(item["world_changed"] for item in episodes),
        "all_world_returns_were_earned": all(
            item["world_return_earned_by_prior_world_change"] for item in episodes
        ),
        "all_top_entries_conducted": all(item["coarse_pass"] for item in episodes),
        "all_bodies_unchanged": all(not item["body_changed"] for item in episodes),
    }
    return {
        "episodes": episodes,
        "checks": checks,
        "passed": all(checks.values()),
    }


def common_world_washout(
    g1_body: Path,
    root: Path,
    layout: BodyLayout,
    *,
    seed: int,
) -> dict:
    """Pass BODY through one identical causal world, then keep BODY alone."""
    source_sha256 = body_sha256(g1_body)
    branch = run_branch(
        g1_body,
        root,
        layout,
        line="A",
        seed=seed + 700_001,
        condition="matched",
        start_at_upper=True,
    )
    checks = {
        "started_from_exact_input_BODY": branch["body_before_sha256"]
        == source_sha256,
        "body_actually_changed_independent_world": branch["world_changed"]
        and branch["trace"]["body_to_world"] > 0,
        "return_was_earned_by_world_change": branch[
            "world_return_earned_by_prior_world_change"
        ]
        and branch["trace"]["world_to_body"] > 0,
        "world_was_destroyed": branch["world_deleted"],
        "BODY_remained_live": branch["coarse_pass"],
    }
    return {
        "source_body": str(g1_body),
        "source_body_sha256": source_sha256,
        "body_path": branch["body_path"],
        "body_sha256": branch["body_sha256"],
        "branch": branch,
        "checks": checks,
        "passed": all(checks.values()),
    }


def common_recut_lineage(
    washed_body: Path,
    root: Path,
    layout: BodyLayout,
    *,
    seed: int,
    episode_order: tuple[str, str] = ("A", "B"),
) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    washed_sha256 = body_sha256(washed_body)
    recut = recut_upper(
        washed_body,
        root / "recut_BODY.mmap",
        layout,
    )
    current_body = Path(recut["body_path"])
    episodes = []
    first_birth_episode: int | None = None
    first_birth_collision: int | None = None
    for episode, line in enumerate(episode_order):
        branch = run_branch(
            current_body,
            root / f"common_{episode}_{line}",
            layout,
            line=line,
            seed=seed + episode * 1_000_003,
            condition="matched",
        )
        episodes.append(branch)
        current_body = Path(branch["body_path"])
        if first_birth_episode is None and branch["upper_birth_collision"] is not None:
            first_birth_episode = episode
            first_birth_collision = branch["upper_birth_collision"]

    final_body = root / "G2_BODY.mmap"
    shutil.copyfile(current_body, final_body)
    body = MmapBody.open(final_body)
    arena = MultiMmapArena(body)
    upper = _upper_place(arena, layout)
    top = collision(arena, upper) if not arena.read(upper).free else None
    return_count = sum(
        body.read(local).return_handle != NO_HANDLE for local in range(body.capacity)
    )
    body.close()
    signature = {
        "birth_episode": 2 if first_birth_episode is None else first_birth_episode,
        "birth_collision": 0 if first_birth_collision is None else first_birth_collision,
        "episode_0_birth": int(episodes[0]["upper_birth_collision"] is not None),
        "episode_1_birth": int(episodes[1]["upper_birth_collision"] is not None),
        "episode_0_world_return": episodes[0]["trace"]["world_to_body"],
        "episode_1_world_return": episodes[1]["trace"]["world_to_body"],
        "return_relation_count": return_count,
        "coarse_pass": int(top is not None and top.kind is CollisionKind.PASS),
    }
    checks = {
        "recut_started_from_exact_washed_BODY": recut["source_sha256"]
        == washed_sha256,
        "same_recut_applied": recut["upper_cut"],
        "both_common_worlds_deleted": all(item["world_deleted"] for item in episodes),
        "both_common_worlds_caused_returns": all(
            item["trace"]["body_to_world"] > 0
            and item["trace"]["world_to_body"] > 0
            and item["world_return_earned_by_prior_world_change"]
            for item in episodes
        ),
        "upper_eventually_restored": bool(signature["coarse_pass"]),
    }
    return {
        "episode_order": list(episode_order),
        "washed_source_body": str(washed_body),
        "washed_source_sha256": washed_sha256,
        "recut": recut,
        "episodes": episodes,
        "G2_body": str(final_body),
        "signature": signature,
        "checks": checks,
        "passed": all(checks.values()),
    }


def balanced_common_lineage(
    washed_body: Path,
    root: Path,
    layout: BodyLayout,
    *,
    seed: int,
) -> dict:
    ab = common_recut_lineage(
        washed_body,
        root / "order_AB",
        layout,
        seed=seed,
        episode_order=("A", "B"),
    )
    ba = common_recut_lineage(
        washed_body,
        root / "order_BA",
        layout,
        seed=seed,
        episode_order=("B", "A"),
    )
    signature = {
        "AB_birth_episode": ab["signature"]["birth_episode"],
        "BA_birth_episode": ba["signature"]["birth_episode"],
        "AB_birth_collision": ab["signature"]["birth_collision"],
        "BA_birth_collision": ba["signature"]["birth_collision"],
        "AB_episode_0_birth": ab["signature"]["episode_0_birth"],
        "BA_episode_0_birth": ba["signature"]["episode_0_birth"],
        "AB_return_relation_count": ab["signature"]["return_relation_count"],
        "BA_return_relation_count": ba["signature"]["return_relation_count"],
        "AB_coarse_pass": ab["signature"]["coarse_pass"],
        "BA_coarse_pass": ba["signature"]["coarse_pass"],
    }
    checks = {
        "both_common_orders_passed": ab["passed"] and ba["passed"],
        "both_orders_started_from_same_washed_BODY": ab[
            "washed_source_sha256"
        ]
        == ba["washed_source_sha256"]
        == body_sha256(washed_body),
        "both_orders_deleted_every_world": ab["checks"][
            "both_common_worlds_deleted"
        ]
        and ba["checks"]["both_common_worlds_deleted"],
    }
    return {
        "AB": ab,
        "BA": ba,
        "G2_body": ab["G2_body"],
        "signature": signature,
        "checks": checks,
        "passed": all(checks.values()),
    }


SIGNATURE_FEATURES = (
    "AB_birth_episode",
    "BA_birth_episode",
    "AB_birth_collision",
    "BA_birth_collision",
    "AB_episode_0_birth",
    "BA_episode_0_birth",
    "AB_return_relation_count",
    "BA_return_relation_count",
    "AB_coarse_pass",
    "BA_coarse_pass",
)


def signature_vector(signature: dict) -> tuple[float, ...]:
    return tuple(float(signature[name]) for name in SIGNATURE_FEATURES)


def vector_distance(left: Sequence[float], right: Sequence[float]) -> float:
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(left, right, strict=True)))


def analyze_lineages(records: Sequence[dict]) -> dict:
    vectors_a = [signature_vector(record["A"]["signature"]) for record in records]
    vectors_b = [signature_vector(record["B"]["signature"]) for record in records]
    within = [
        vector_distance(vectors[index], vectors[other])
        for vectors in (vectors_a, vectors_b)
        for index in range(len(vectors))
        for other in range(index + 1, len(vectors))
    ]
    between = [vector_distance(a, b) for a in vectors_a for b in vectors_b]
    max_within = max(within, default=0.0)
    min_between = min(between, default=0.0)
    return {
        "features": list(SIGNATURE_FEATURES),
        "max_within_distance": max_within,
        "min_between_distance": min_between,
        "lineages_reproducible_and_separated": min_between > max_within,
    }


def shuffle_return_placement(source: Path, target: Path, seed: int) -> dict:
    shutil.copyfile(source, target)
    body = MmapBody.open(target)
    arena = MultiMmapArena(body)
    carriers = [
        local
        for local in range(body.capacity)
        if body.read(local).return_handle != NO_HANDLE
    ]
    values = [body.read(local).return_handle for local in carriers]
    structural_before = [
        (
            body.read(local).gesture,
            body.read(local).contact_handle,
            body.read(local).port_handle,
            body.read(local).birth_handle,
            body.read(local).upper_handle,
        )
        for local in range(body.capacity)
    ]
    material_before = body_material_count(body)
    random.Random(seed).shuffle(values)
    if len(values) > 1:
        values = values[1:] + values[:1]
    before_multiset = sorted(record.return_handle for record in (body.read(a) for a in carriers))
    for local, value in zip(carriers, values, strict=True):
        place = body_place(local)
        arena._store(place, replace(arena.read(place), return_handle=value))
    after_multiset = sorted(record.return_handle for record in (body.read(a) for a in carriers))
    structural_after = [
        (
            body.read(local).gesture,
            body.read(local).contact_handle,
            body.read(local).port_handle,
            body.read(local).birth_handle,
            body.read(local).upper_handle,
        )
        for local in range(body.capacity)
    ]
    top = collision(arena, canonical_layout().upper)
    body.flush()
    material_after = body_material_count(body)
    body.close()
    return {
        "body_path": str(target),
        "return_count": len(carriers),
        "return_multiset_unchanged": before_multiset == after_multiset,
        "graph_and_material_unchanged": structural_before == structural_after
        and material_before == material_after,
        "ordinary_upper_pass_survived": top.kind is CollisionKind.PASS,
    }


def _remap_body_handle(handle: int, permutation: tuple[int, ...]) -> int:
    if handle == NO_HANDLE:
        return NO_HANDLE
    surface, local = decode_handle(handle)
    if surface == BODY_SURFACE:
        return encode_handle(BODY_SURFACE, permutation[local])
    return handle


def relabel_body(
    source: Path,
    target: Path,
    layout: BodyLayout,
    seed: int,
) -> tuple[BodyLayout, dict]:
    original = MmapBody.open(source)
    addresses = list(range(original.capacity))
    random.Random(seed).shuffle(addresses)
    permutation = tuple(addresses)
    relabeled = MmapBody.create(target, original.capacity)
    arena = MultiMmapArena(relabeled)
    for old_local in range(original.capacity):
        old = original.read(old_local)
        new = MaterialRecord(
            gesture=old.gesture,
            contact_handle=_remap_body_handle(old.contact_handle, permutation),
            port_handle=_remap_body_handle(old.port_handle, permutation),
            birth_handle=_remap_body_handle(old.birth_handle, permutation),
            return_handle=_remap_body_handle(old.return_handle, permutation),
            upper_handle=_remap_body_handle(old.upper_handle, permutation),
        )
        arena._store(body_place(permutation[old_local]), new)
    isomorphic = all(
        MaterialRecord(
            gesture=original.read(old_local).gesture,
            contact_handle=_remap_body_handle(
                original.read(old_local).contact_handle,
                permutation,
            ),
            port_handle=_remap_body_handle(
                original.read(old_local).port_handle,
                permutation,
            ),
            birth_handle=_remap_body_handle(
                original.read(old_local).birth_handle,
                permutation,
            ),
            return_handle=_remap_body_handle(
                original.read(old_local).return_handle,
                permutation,
            ),
            upper_handle=_remap_body_handle(
                original.read(old_local).upper_handle,
                permutation,
            ),
        )
        == relabeled.read(permutation[old_local])
        for old_local in range(original.capacity)
    )
    relabeled.flush()
    original.close()
    relabeled.close()

    def mapped(place: Place) -> Place:
        _surface, local = decode_handle(place.address)
        return body_place(permutation[local])

    mapped_layout = BodyLayout(
        origin=mapped(layout.origin),
        upper=mapped(layout.upper),
        prelude=tuple(mapped(place) for place in layout.prelude),
        route_a=tuple(mapped(place) for place in layout.route_a),
        route_b=tuple(mapped(place) for place in layout.route_b),
    )
    return mapped_layout, {
        "body_path": str(target),
        "permutation_is_hostile": any(
            old != new for old, new in enumerate(permutation)
        ),
        "body_isomorphic": isomorphic,
    }


def controls_receipt(conditions: Iterable[dict]) -> dict:
    records = list(conditions)
    return {
        "runs": len(records),
        "passed": all(record["passed"] for record in records),
        "all_matched_returns_earned_by_world_change": all(
            record["branches"]["matched"][
                "world_return_earned_by_prior_world_change"
            ]
            for record in records
        ),
        "no_passive_branch_closed_a_crack": all(
            not record["branches"]["passive"]["upper_born"]
            and not record["branches"]["passive"]["coarse_pass"]
            and not record["branches"]["passive"][
                "world_return_earned_by_prior_world_change"
            ]
            for record in records
        ),
        "all_resulting_BODIES_separated": all(
            separation["BODY"]
            for record in records
            for separation in record["separations"].values()
        ),
        "all_future_behaviors_separated": all(
            separation["future_behavior"]
            for record in records
            for separation in record["separations"].values()
        ),
        "all_worlds_deleted": all(
            branch["world_deleted"]
            for record in records
            for branch in record["branches"].values()
        )
        and all(
            probe["washout"]["world_deleted"]
            and probe["after_recut"]["world_deleted"]
            for record in records
            for probe in record["future_behavior"].values()
        ),
    }
