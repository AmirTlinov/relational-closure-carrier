#!/usr/bin/env python3
"""Witness explicit-handle growth, hostile relabeling and scale passage."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys
import time

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
    RECORD_BYTES,
    collision,
    execute_lane,
)


ROOT = Path(__file__).resolve().parent


@dataclass(frozen=True)
class PreparedBody:
    origin: Place
    initial_nonfree: tuple[Place, ...]


def source_hash() -> str:
    digest = hashlib.sha256()
    for path in (ROOT / "growth_carrier.py", ROOT / "run_growth.py"):
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def prepare_crack(
    path: Path,
    gap: int,
    *,
    compatible_side: bool = True,
    extra_free: int = 0,
) -> tuple[MmapBody, PreparedBody]:
    """Prepare old body plus passive free contacts; no contact conducts yet."""
    if gap < 1 or gap % 2 == 0:
        raise ValueError("this fixture needs a positive odd physical gap")
    lower_depth = 3
    upper = 0
    origin = 1
    free_chain = tuple(range(2, gap + 2))
    side = gap + 2
    tail = tuple(range(side + 1, side + 1 + lower_depth))
    capacity = gap + lower_depth + 3 + int(extra_free)
    body = MmapBody.create(path, capacity)

    body.place_free_contact(upper, origin)
    body.place_relation(
        origin,
        GESTURE_1,
        free_chain[0],
        upper_slot=upper,
    )
    for offset, address in enumerate(free_chain):
        target = free_chain[offset + 1] if offset + 1 < len(free_chain) else side
        body.place_free_contact(address, target)

    side_gesture = GESTURE_1 if compatible_side else GESTURE_0
    body.place_relation(side, side_gesture, tail[0])
    gesture = -side_gesture
    for offset, address in enumerate(tail):
        target = tail[offset + 1] if offset + 1 < len(tail) else origin
        body.place_relation(address, gesture, target)
        gesture = -gesture
    body.flush()
    return body, PreparedBody(
        origin=Place(origin),
        initial_nonfree=(Place(origin), Place(side), *(Place(a) for a in tail)),
    )


def prepare_unclosed(path: Path, capacity: int) -> tuple[MmapBody, Place]:
    if capacity < 4:
        raise ValueError("unclosed fixture needs room to expand")
    body = MmapBody.create(path, capacity)
    upper = 0
    origin = 1
    body.place_free_contact(upper, origin)
    body.place_relation(origin, GESTURE_1, 2, upper_slot=upper)
    for address in range(2, capacity):
        target = address + 1 if address + 1 < capacity else NO_HANDLE
        body.place_free_contact(address, target)
    body.flush()
    return body, Place(origin)


def relation_snapshot(body: MmapBody, places: tuple[Place, ...]) -> dict[int, bytes]:
    return {
        place.address: body.record_bytes(place.address)
        for place in places
    }


def structural_snapshot(
    body: MmapBody,
    places: tuple[Place, ...],
) -> dict[int, tuple[int, int, int, int]]:
    return {
        place.address: (
            body.read(place).gesture,
            body.read(place).contact_handle,
            body.read(place).port_handle,
            body.read(place).upper_handle,
        )
        for place in places
    }


def find_upper_birth(trace: tuple[Collision, ...]) -> tuple[Collision, Place] | None:
    for event in trace:
        if event.kind is CollisionKind.MATERIALIZE:
            created = tuple(place for place in event.changed if place != event.met)
            if len(created) == 1:
                return event, created[0]
    return None


def follow_cycle(body: MmapBody, start: Place) -> tuple[Place, ...] | None:
    """Read-only route-down witness; it never chooses a physical continuation."""
    route: list[Place] = [start]
    current = start
    for _ in range(body.capacity + 1):
        target = body.port(body.read(current))
        if target is None or body.read(target).free:
            return None
        if target == start:
            return tuple(route)
        if target in route:
            return None
        route.append(target)
        current = target
    return None


def reachable_cycle(
    body: MmapBody,
    start: Place,
) -> tuple[tuple[Place, ...], tuple[Place, ...]] | None:
    route: list[Place] = []
    first_seen: dict[Place, int] = {}
    current = start
    for _ in range(body.capacity + 1):
        if current in first_seen:
            split = first_seen[current]
            return tuple(route[:split]), tuple(route[split:])
        first_seen[current] = len(route)
        route.append(current)
        target = body.port(body.read(current))
        if target is None or body.read(target).free:
            return None
        current = target
    return None


def relational_octave(body: MmapBody, route: tuple[Place, ...]) -> bool:
    if not route:
        return False
    for offset, current in enumerate(route):
        target = route[(offset + 1) % len(route)]
        current_record = body.read(current)
        if body.port(current_record) != target:
            return False
        if body.read(target).gesture != -current_record.gesture:
            return False
    return True


def fresh_process_probe(path: Path, start: Place) -> dict:
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--probe-body",
            str(path),
            "--probe-start",
            str(start.address),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def event_receipt(event: Collision, step: int) -> dict:
    return {
        "step": step,
        "kind": event.kind.value,
        "current": event.current.address,
        "met": None if event.met is None else event.met.address,
        "continuation": (
            None if event.continuation is None else event.continuation.address
        ),
        "changed": [place.address for place in event.changed],
    }


def one_closed(root: Path, gap: int, *, include_trace: bool = False) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    body_path = root / "body.mmap"
    body, prepared = prepare_crack(body_path, gap, extra_free=5)
    with body:
        initial = body.snapshot()
        no_execution_no_change = body.snapshot() == initial
        initial_records = {
            address: body.read(address) for address in range(body.capacity)
        }
        passive_free_contacts = all(
            record.port_handle == NO_HANDLE
            and record.birth_handle == NO_HANDLE
            and record.return_handle == NO_HANDLE
            for record in initial_records.values()
            if record.free
        )
        records_before = {
            address: body.record_bytes(address) for address in range(body.capacity)
        }
        lower_before = structural_snapshot(body, prepared.initial_nonfree)
        started = time.thread_time_ns()
        run = execute_lane(
            body,
            prepared.origin,
            body.capacity * 3,
            capture_trace=True,
        )
        cpu_time_ns = time.thread_time_ns() - started
        birth = find_upper_birth(run.trace)
        if birth is None:
            raise RuntimeError("the local run did not materialize an upper entry")
        birth_event, upper = birth
        lower_after = structural_snapshot(body, prepared.initial_nonfree)
        cycle = follow_cycle(body, prepared.origin)
        upper_record = body.read(upper)
        origin_record = body.read(prepared.origin)
        first = body.port(origin_record)
        first_record = body.read(first) if first is not None else MaterialRecord(FREE)
        growth_events = tuple(
            event
            for event in run.trace[: run.trace.index(birth_event)]
            if event.kind is CollisionKind.MATERIALIZE and event.changed == (event.met,)
        )
        growth_chain = bool(growth_events) and growth_events[0].current == prepared.origin
        for previous, event in zip(growth_events, growth_events[1:]):
            growth_chain = growth_chain and event.current == previous.met
        for event in growth_events:
            if event.met is None:
                growth_chain = False
                continue
            before = initial_records[event.met.address]
            record = body.read(event.met)
            growth_chain = (
                growth_chain
                and before.free
                and before.port_handle == NO_HANDLE
                and record.contact_handle == before.contact_handle
                and record.port_handle == before.contact_handle
                and record.born_here
                and body.back(record) == event.current
            )
        changed_places = {
            place.address for event in run.trace for place in event.changed
        }
        untouched_places_unchanged = all(
            body.record_bytes(address) == before
            for address, before in records_before.items()
            if address not in changed_places
        )
        body.flush()
        sealed = body.snapshot()
        sealed_sha = sha256_bytes(sealed)
        checks = {
            "no_execution_no_change": no_execution_no_change,
            "free_contacts_started_passive": passive_free_contacts,
            "growth_followed_explicit_contacts": growth_chain,
            "upper_absent_until_body_return": all(
                upper not in event.changed
                for event in run.trace[: run.trace.index(birth_event)]
            )
            and birth_event.met == prepared.origin
            and birth_event.current not in {event.met for event in growth_events},
            "upper_is_explicit_ordinary_relation": upper_record.birth_handle
            == NO_HANDLE
            and upper_record.return_handle == NO_HANDLE
            and body.port(upper_record) == prepared.origin
            and body.contact(upper_record) == prepared.origin
            and body.upper_slot(origin_record) == upper
            and upper_record.gesture == -origin_record.gesture,
            "closed_route_survived": cycle is not None,
            "route_is_relational_octave": cycle is not None
            and relational_octave(body, cycle),
            "grown_lower_route_remains_physical": first is not None
            and first_record.born_here,
            "old_lower_route_forward_relations_preserved": lower_before == lower_after,
            "actual_return_became_material": all(
                body.read(place).carries_return
                for place in prepared.initial_nonfree
            ),
            "only_causally_touched_places_changed": untouched_places_unchanged,
            "real_cpu_execution_witnessed": cpu_time_ns > 0,
        }

    restarted_path = root / "restarted.mmap"
    shutil.copyfile(body_path, restarted_path)
    restarted_exact = restarted_path.read_bytes() == sealed
    restart = fresh_process_probe(restarted_path, upper)
    checks["body_only_restart_exact"] = restarted_exact
    checks["fresh_process_conducts_same_cycle"] = restart["closed_cycle"]
    checks["restart_does_not_rewrite_body"] = restart["body_unchanged"]

    result = {
        "fixture_gap": gap,
        "passed": all(checks.values()),
        "checks": checks,
        "observed": {
            "capacity": len(sealed[16:]) // RECORD_BYTES,
            "cpu_collisions": run.stop.collisions,
            "cpu_time_ns": cpu_time_ns,
            "materializations_before_upper": len(growth_events),
            "closed_cycle_places": 0 if cycle is None else len(cycle),
            "upper_address": upper.address,
            "origin_address": prepared.origin.address,
            "upper_birth_after_collision": run.trace.index(birth_event) + 1,
        },
        "sealed_body_sha256": sealed_sha,
        "restart": restart,
    }
    if include_trace:
        result["trace_to_upper"] = [
            event_receipt(event, step)
            for step, event in enumerate(
                run.trace[: run.trace.index(birth_event) + 1],
                start=1,
            )
        ]
    return result


def unclosed_growth(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    body, origin = prepare_unclosed(root / "unclosed.mmap", 17)
    with body:
        before = body.snapshot()
        run = execute_lane(body, origin, body.capacity * 3, capture_trace=True)
        after = body.snapshot()
    kinds = tuple(event.kind for event in run.trace)
    return {
        "passed": before == after
        and CollisionKind.MATERIALIZE in kinds
        and CollisionKind.RETRACT in kinds
        and find_upper_birth(run.trace) is None,
        "body_returned_exactly": before == after,
        "materializations": sum(kind is CollisionKind.MATERIALIZE for kind in kinds),
        "retractions": sum(kind is CollisionKind.RETRACT for kind in kinds),
        "upper_births": 0 if find_upper_birth(run.trace) is None else 1,
    }


def incompatible_contact(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    body, prepared = prepare_crack(
        root / "incompatible.mmap",
        7,
        compatible_side=False,
    )
    with body:
        before = body.snapshot()
        old_before = relation_snapshot(body, prepared.initial_nonfree)
        run = execute_lane(body, prepared.origin, body.capacity * 3, capture_trace=True)
        old_after = relation_snapshot(body, prepared.initial_nonfree)
        after = body.snapshot()
    return {
        "passed": old_before == old_after
        and before == after
        and find_upper_birth(run.trace) is None,
        "old_body_unchanged": old_before == old_after,
        "whole_body_restored": before == after,
        "upper_births": 0 if find_upper_birth(run.trace) is None else 1,
    }


def ready_matter(root: Path, gesture: int) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    name = "inverse" if gesture == GESTURE_0 else "duplicate"
    body, prepared = prepare_crack(root / f"ready_{name}.mmap", 1)
    with body:
        first = body.port(body.read(prepared.origin))
        if first is None:
            raise RuntimeError("fixture origin has no contact")
        target = body.contact(body.read(first))
        if target is None:
            raise RuntimeError("fixture free place has no next contact")
        body.place_relation(first.address, gesture, target.address)
        before = body.snapshot()
        run = execute_lane(body, prepared.origin, body.capacity * 2, capture_trace=True)
        after = body.snapshot()
    return {
        "passed": before == after and find_upper_birth(run.trace) is None,
        "body_unchanged": before == after,
        "upper_births": 0 if find_upper_birth(run.trace) is None else 1,
    }


def partial_growth_cannot_fake_return(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    body, prepared = prepare_crack(root / "partial.mmap", 7)
    with body:
        first = collision(body, prepared.origin)
        old_side = prepared.initial_nonfree[1]
        run = execute_lane(body, old_side, body.capacity, capture_trace=True)
        origin_record = body.read(prepared.origin)
        upper = body.upper_slot(origin_record)
        no_upper = (
            find_upper_birth(run.trace) is None
            and upper is not None
            and body.read(upper).free
        )
        origin_has_no_return = not origin_record.carries_return
    return {
        "passed": first.kind is CollisionKind.MATERIALIZE
        and no_upper
        and origin_has_no_return,
        "one_local_growth_place_existed": first.kind is CollisionKind.MATERIALIZE,
        "old_body_execution_created_no_upper": no_upper,
        "origin_received_no_false_return": origin_has_no_return,
    }


def remap_handle(handle: int, permutation: tuple[int, ...]) -> int:
    return NO_HANDLE if handle == NO_HANDLE else permutation[handle]


def remap_record(
    record: MaterialRecord,
    permutation: tuple[int, ...],
) -> MaterialRecord:
    return MaterialRecord(
        gesture=record.gesture,
        contact_handle=remap_handle(record.contact_handle, permutation),
        port_handle=remap_handle(record.port_handle, permutation),
        birth_handle=remap_handle(record.birth_handle, permutation),
        return_handle=remap_handle(record.return_handle, permutation),
        upper_handle=remap_handle(record.upper_handle, permutation),
    )


def permuted_copy(
    source: MmapBody,
    path: Path,
    permutation: tuple[int, ...],
) -> MmapBody:
    if sorted(permutation) != list(range(source.capacity)):
        raise ValueError("address permutation must be a bijection")
    target = MmapBody.create(path, source.capacity)
    for old_address in range(source.capacity):
        target._store(
            permutation[old_address],
            remap_record(source.read(old_address), permutation),
        )
    target.flush()
    return target


def bodies_are_isomorphic(
    left: MmapBody,
    right: MmapBody,
    permutation: tuple[int, ...],
) -> bool:
    return all(
        remap_record(left.read(old_address), permutation)
        == right.read(permutation[old_address])
        for old_address in range(left.capacity)
    )


def map_place(place: Place | None, permutation: tuple[int, ...]) -> Place | None:
    return None if place is None else Place(permutation[place.address])


def traces_are_isomorphic(
    left: tuple[Collision, ...],
    right: tuple[Collision, ...],
    permutation: tuple[int, ...],
) -> bool:
    if len(left) != len(right):
        return False
    for original, relabeled in zip(left, right):
        if original.kind is not relabeled.kind:
            return False
        if map_place(original.current, permutation) != relabeled.current:
            return False
        if map_place(original.met, permutation) != relabeled.met:
            return False
        if map_place(original.continuation, permutation) != relabeled.continuation:
            return False
        if tuple(map_place(place, permutation) for place in original.changed) != relabeled.changed:
            return False
    return True


def address_permutation_control(root: Path) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    original, prepared = prepare_crack(root / "original.mmap", 7, extra_free=5)
    addresses = list(range(original.capacity))
    random.Random(0x12_1024).shuffle(addresses)
    permutation = tuple(addresses)
    permuted = permuted_copy(original, root / "permuted.mmap", permutation)
    with original, permuted:
        original_run = execute_lane(
            original,
            prepared.origin,
            original.capacity * 3,
            capture_trace=True,
        )
        permuted_origin = Place(permutation[prepared.origin.address])
        permuted_run = execute_lane(
            permuted,
            permuted_origin,
            permuted.capacity * 3,
            capture_trace=True,
        )
        original_birth = find_upper_birth(original_run.trace)
        permuted_birth = find_upper_birth(permuted_run.trace)
        original_cycle = follow_cycle(original, prepared.origin)
        permuted_cycle = follow_cycle(permuted, permuted_origin)
        upper_mapped = (
            original_birth is not None
            and permuted_birth is not None
            and map_place(original_birth[1], permutation) == permuted_birth[1]
        )
        route_mapped = (
            original_cycle is not None
            and permuted_cycle is not None
            and tuple(map_place(place, permutation) for place in original_cycle)
            == permuted_cycle
        )
        trace_mapped = traces_are_isomorphic(
            original_run.trace,
            permuted_run.trace,
            permutation,
        )
        body_mapped = bodies_are_isomorphic(original, permuted, permutation)
        top_event_mapped = False
        if original_birth is not None and permuted_birth is not None:
            original_top = collision(original, original_birth[1])
            permuted_top = collision(permuted, permuted_birth[1])
            top_event_mapped = traces_are_isomorphic(
                (original_top,),
                (permuted_top,),
                permutation,
            )

    hostile = any(
        permutation[address] != address
        for address in range(len(permutation))
    ) and any(
        permutation[address + 1] != permutation[address] + 1
        for address in range(len(permutation) - 1)
    )
    checks = {
        "addresses_were_hostilely_permuted": hostile,
        "collision_trace_isomorphic": trace_mapped,
        "final_body_isomorphic": body_mapped,
        "closed_route_isomorphic": route_mapped,
        "same_upper_relation_isomorphic": upper_mapped,
        "one_top_contact_isomorphic": top_event_mapped,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "capacity": len(permutation),
        "permutation": list(permutation),
    }


def scale_form_proof(root: Path) -> dict:
    """Prove one upper contact and independently reveal its preserved route."""
    root.mkdir(parents=True, exist_ok=True)
    body, prepared = prepare_crack(root / "scale.mmap", 7, extra_free=3)
    with body:
        closure = execute_lane(
            body,
            prepared.origin,
            body.capacity * 3,
            capture_trace=True,
        )
        birth = find_upper_birth(closure.trace)
        if birth is None:
            raise RuntimeError("scale proof needs a born upper relation")
        upper = birth[1]
        before_top = body.snapshot()
        top_event = collision(body, upper)
        top_no_rewrite = body.snapshot() == before_top
        route_down = follow_cycle(body, prepared.origin)
        route_down_valid = route_down is not None and relational_octave(body, route_down)

        body.clear_place(upper.address)
        removed_event = collision(body, upper)
        route_after_removal = follow_cycle(body, prepared.origin)
        lower_survived = (
            route_down is not None
            and route_after_removal == route_down
            and relational_octave(body, route_after_removal)
        )

        regrowth = execute_lane(
            body,
            prepared.origin,
            body.capacity * 2,
            capture_trace=True,
        )
        rebirth = find_upper_birth(regrowth.trace)
        restored_event = collision(body, upper)
        route_after_restore = follow_cycle(body, prepared.origin)
        route_still_revealable = route_after_restore == route_down

    checks = {
        "upper_conducts_in_one_collision": top_event.kind is CollisionKind.PASS
        and top_event.met == prepared.origin
        and top_event.continuation == prepared.origin
        and not top_event.changed,
        "one_collision_did_not_hide_rewrite": top_no_rewrite,
        "route_down_reveals_closed_form": route_down_valid,
        "upper_ablation_removes_large_act": removed_event.kind is CollisionKind.HALT,
        "upper_ablation_preserves_route_down": lower_survived,
        "full_lower_pass_restores_upper": rebirth is not None and rebirth[1] == upper,
        "restored_upper_conducts_again": restored_event.kind is CollisionKind.PASS
        and restored_event.met == prepared.origin,
        "route_down_remains_revealable": route_still_revealable,
    }
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "top_event": event_receipt(top_event, 1),
        "route_down": [] if route_down is None else [p.address for p in route_down],
        "route_down_places": 0 if route_down is None else len(route_down),
        "regrowth_collisions_until_upper": (
            None
            if rebirth is None
            else regrowth.trace.index(rebirth[0]) + 1
        ),
    }


def relational_octave_from_file(path: Path, route: tuple[Place, ...]) -> bool:
    with MmapBody.open(path) as body:
        return relational_octave(body, route)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gaps", type=int, nargs="+", default=(1, 7, 127, 1023))
    parser.add_argument("--workdir", type=Path, default=ROOT / "results" / "bodies")
    parser.add_argument("--out", type=Path, default=ROOT / "results" / "growth_receipt.json")
    parser.add_argument("--probe-body", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--probe-start", type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.probe_body is not None:
        if args.probe_start is None:
            raise SystemExit("--probe-start is required")
        with MmapBody.open(args.probe_body) as body:
            before = body.snapshot()
            start = Place(args.probe_start)
            run = execute_lane(body, start, body.capacity * 2, capture_trace=True)
            reached = reachable_cycle(body, start)
            after = body.snapshot()
            route = None if reached is None else reached[1]
        print(
            json.dumps(
                {
                    "closed_cycle": route is not None
                    and relational_octave_from_file(args.probe_body, route),
                    "cycle_places": 0 if route is None else len(route),
                    "collisions": run.stop.collisions,
                    "body_unchanged": before == after,
                }
            )
        )
        return 0

    started_utc = datetime.now(timezone.utc).isoformat()
    initial_source = source_hash()
    if args.workdir.exists():
        shutil.rmtree(args.workdir)
    args.workdir.mkdir(parents=True)

    trace_gap = min(args.gaps)
    closed = [
        one_closed(
            args.workdir / f"gap_{gap}",
            gap,
            include_trace=gap == trace_gap,
        )
        for gap in args.gaps
    ]
    unclosed = unclosed_growth(args.workdir / "unclosed")
    incompatible = incompatible_contact(args.workdir / "incompatible")
    inverse = ready_matter(args.workdir / "counterfeit", GESTURE_0)
    duplicate = ready_matter(args.workdir / "counterfeit", GESTURE_1)
    partial = partial_growth_cannot_fake_return(args.workdir / "counterfeit")
    permutation = address_permutation_control(args.workdir / "address_permutation")
    scale = scale_form_proof(args.workdir / "scale_form")
    final_source = source_hash()
    checks = {
        "all_local_closures_passed": all(item["passed"] for item in closed),
        "unclosed_growth_dispersed": unclosed["passed"],
        "incompatible_contact_preserved_old_body": incompatible["passed"],
        "ready_inverse_did_not_close": inverse["passed"],
        "duplicate_did_not_close": duplicate["passed"],
        "partial_growth_could_not_fake_full_return": partial["passed"],
        "address_permutation_preserved_physics": permutation["passed"],
        "upper_relation_earned_scale_form": scale["passed"],
        "source_unchanged": initial_source == final_source,
    }
    passed = all(checks.values())
    report = {
        "artifact_kind": "explicit_relation_local_growth_receipt",
        "claim": "completed_scale_fold" if scale["passed"] else "local_growth_and_upper_entry",
        "started_utc": started_utc,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "source_hash": initial_source,
        "final_source_hash": final_source,
        "closed": closed,
        "minimal_experience": next(
            item for item in closed if "trace_to_upper" in item
        ),
        "unclosed": unclosed,
        "incompatible": incompatible,
        "counterfeits": {"ready_inverse": inverse, "duplicate": duplicate},
        "partial_growth_control": partial,
        "address_permutation_control": permutation,
        "scale_form_proof": scale,
        "checks": checks,
        "passed": passed,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "passed": passed,
                "claim": report["claim"],
                "source_hash": initial_source,
                "checks": checks,
                "closed": {
                    item["fixture_gap"]: item["observed"] for item in closed
                },
                "address_permutation": permutation["checks"],
                "scale_form": scale["checks"],
            },
            ensure_ascii=False,
        )
    )
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
