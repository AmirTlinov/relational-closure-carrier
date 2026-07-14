import ast
import inspect
from pathlib import Path
import shutil

from growth_carrier import (
    CollisionKind,
    FREE,
    GESTURE_0,
    GESTURE_1,
    MmapBody,
    NO_HANDLE,
    RECORD_BYTES,
    collision,
    execute_lane,
)
from run_growth import (
    address_permutation_control,
    find_upper_birth,
    follow_cycle,
    partial_growth_cannot_fake_return,
    prepare_crack,
    prepare_unclosed,
    reachable_cycle,
    relational_octave,
    scale_form_proof,
    structural_snapshot,
)


def test_growth_uses_explicit_passive_contact_instead_of_numeric_motion(tmp_path):
    body, prepared = prepare_crack(tmp_path / "body", 7)
    with body:
        origin_record = body.read(prepared.origin)
        first = body.port(origin_record)
        assert first is not None
        free_before = body.read(first)
        assert free_before.gesture == FREE
        assert free_before.contact_handle != NO_HANDLE
        assert free_before.port_handle == NO_HANDLE
        assert free_before.birth_handle == NO_HANDLE

        event = collision(body, prepared.origin)
        assert event.kind is CollisionKind.MATERIALIZE
        assert event.met == first
        created = body.read(first)
        assert created.gesture == -origin_record.gesture
        assert created.contact_handle == free_before.contact_handle
        assert created.port_handle == free_before.contact_handle
        assert body.back(created) == prepared.origin


def test_upper_slot_is_explicit_and_born_only_after_actual_return(tmp_path):
    body, prepared = prepare_crack(tmp_path / "body", 7)
    with body:
        before = structural_snapshot(body, prepared.initial_nonfree)
        origin_before = body.read(prepared.origin)
        explicit_upper = body.upper_slot(origin_before)
        assert explicit_upper is not None
        assert body.read(explicit_upper).free
        assert body.contact(body.read(explicit_upper)) == prepared.origin

        run = execute_lane(body, prepared.origin, body.capacity * 3, capture_trace=True)
        birth = find_upper_birth(run.trace)
        assert birth is not None
        event, upper = birth
        assert upper == explicit_upper
        assert all(upper not in item.changed for item in run.trace[: run.trace.index(event)])
        assert event.met == prepared.origin
        assert structural_snapshot(body, prepared.initial_nonfree) == before

        upper_record = body.read(upper)
        assert upper_record.birth_handle == NO_HANDLE
        assert upper_record.return_handle == NO_HANDLE
        assert body.port(upper_record) == prepared.origin
        cycle = follow_cycle(body, prepared.origin)
        assert cycle is not None
        assert relational_octave(body, cycle)


def test_closed_route_keeps_every_growth_born_place(tmp_path):
    body, prepared = prepare_crack(tmp_path / "body", 9)
    with body:
        execute_lane(body, prepared.origin, body.capacity * 3)
        current = body.port(body.read(prepared.origin))
        assert current is not None
        route = []
        while body.read(current).born_here:
            route.append(current)
            current = body.port(body.read(current))
        assert route
        assert all(body.read(place).gesture != FREE for place in route)
        assert all(body.read(place).birth_handle != NO_HANDLE for place in route)


def test_upper_contact_is_one_large_act_and_route_down_stays_revealable(tmp_path):
    proof = scale_form_proof(tmp_path / "scale")
    assert proof["passed"]
    assert proof["top_event"]["kind"] == CollisionKind.PASS.value
    assert proof["top_event"]["changed"] == []
    assert proof["route_down_places"] > 1
    assert proof["checks"]["upper_ablation_removes_large_act"]
    assert proof["checks"]["upper_ablation_preserves_route_down"]
    assert proof["checks"]["full_lower_pass_restores_upper"]


def test_unclosed_growth_retracts_to_same_explicit_free_contacts(tmp_path):
    body, origin = prepare_unclosed(tmp_path / "body", 17)
    with body:
        before = body.snapshot()
        run = execute_lane(body, origin, body.capacity * 3, capture_trace=True)
        assert any(event.kind is CollisionKind.MATERIALIZE for event in run.trace)
        assert any(event.kind is CollisionKind.RETRACT for event in run.trace)
        assert find_upper_birth(run.trace) is None
        assert body.snapshot() == before


def test_incompatible_contact_preserves_old_body_and_contacts(tmp_path):
    body, prepared = prepare_crack(
        tmp_path / "body",
        7,
        compatible_side=False,
    )
    with body:
        before = body.snapshot()
        old_before = {
            place: body.record_bytes(place.address)
            for place in prepared.initial_nonfree
        }
        run = execute_lane(body, prepared.origin, body.capacity * 3, capture_trace=True)
        assert find_upper_birth(run.trace) is None
        assert {
            place: body.record_bytes(place.address)
            for place in prepared.initial_nonfree
        } == old_before
        assert body.snapshot() == before


def test_ready_inverse_and_duplicate_are_not_growth_history(tmp_path):
    for name, gesture in (("inverse", GESTURE_0), ("duplicate", GESTURE_1)):
        body, prepared = prepare_crack(tmp_path / name, 1)
        with body:
            first = body.port(body.read(prepared.origin))
            target = body.contact(body.read(first))
            body.place_relation(first.address, gesture, target.address)
            before = body.snapshot()
            run = execute_lane(body, prepared.origin, body.capacity * 2, capture_trace=True)
            assert find_upper_birth(run.trace) is None
            assert body.snapshot() == before


def test_partial_growth_cannot_fake_full_return(tmp_path):
    result = partial_growth_cannot_fake_return(tmp_path / "partial")
    assert result["passed"]


def test_hostile_address_permutation_preserves_trace_route_and_upper(tmp_path):
    result = address_permutation_control(tmp_path / "permutation")
    assert result["passed"]
    assert all(result["checks"].values())


def test_body_only_restart_keeps_topology_without_runtime_state(tmp_path):
    body_path = tmp_path / "body"
    restarted_path = tmp_path / "restarted"
    body, prepared = prepare_crack(body_path, 7)
    with body:
        run = execute_lane(body, prepared.origin, body.capacity * 3, capture_trace=True)
        upper = find_upper_birth(run.trace)[1]
        expected = body.snapshot()
    shutil.copyfile(body_path, restarted_path)
    with MmapBody.open(restarted_path) as restarted:
        assert restarted.snapshot() == expected
        reached = reachable_cycle(restarted, upper)
        assert reached is not None
        prefix, cycle = reached
        assert prefix == (upper,)
        assert relational_octave(restarted, cycle)
        before = restarted.snapshot()
        execute_lane(restarted, upper, restarted.capacity * 2)
        assert restarted.snapshot() == before


def test_trace_is_only_witness_and_cannot_change_material_trajectory(tmp_path):
    first, first_prepared = prepare_crack(tmp_path / "first", 7)
    second, second_prepared = prepare_crack(tmp_path / "second", 7)
    with first, second:
        execute_lane(first, first_prepared.origin, first.capacity * 3, capture_trace=True)
        execute_lane(second, second_prepared.origin, second.capacity * 3, capture_trace=False)
        assert first.snapshot() == second.snapshot()


def test_same_handle_kernel_scales_without_size_or_gesture_gate(tmp_path):
    for gap in (1, 7, 127, 1023):
        body, prepared = prepare_crack(tmp_path / str(gap), gap, extra_free=3)
        with body:
            run = execute_lane(body, prepared.origin, body.capacity * 3, capture_trace=True)
            assert find_upper_birth(run.trace) is not None
            cycle = follow_cycle(body, prepared.origin)
            assert cycle is not None
            assert relational_octave(body, cycle)


def test_collision_owner_has_no_address_geometry_or_global_sweep():
    assert RECORD_BYTES == 24
    path = Path(inspect.getsourcefile(collision))
    module = path.read_text().lower()
    for forbidden in (
        "fold",
        "port_delta",
        "birth_delta",
        "return_delta",
        "motion",
        "score",
        "weight",
        "experience",
        "conductance",
        "energy_packet",
        "scheduler",
        "allocator",
        "priority",
        "expose_path",
    ):
        assert forbidden not in module

    tree = ast.parse(path.read_text())
    owners = {"collision", "_retract_one", "_materialize_upper_entry"}
    functions = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in owners
    ]
    assert functions
    assert not any(
        isinstance(node, (ast.For, ast.While, ast.AsyncFor))
        for function in functions
        for node in ast.walk(function)
    )
    assert not any(
        isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub))
        for function in functions
        for node in ast.walk(function)
    )
    source = inspect.getsource(collision)
    assert ".snapshot(" not in source
    assert ".capacity" not in source
