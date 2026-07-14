import json
from pathlib import Path
import subprocess
import sys

from world_lineage import (
    BODY_CAPACITY,
    IMMUTABLE_KERNEL_SHA256,
    analyze_lineages,
    balanced_common_lineage,
    body_material_count,
    create_damaged_body,
    cut_to_shared_damage,
    kernel_sha256,
    relabel_body,
    run_branch,
    run_paired_conditions,
    shuffle_return_placement,
)


def test_world_lineage_uses_exact_frozen_collision_kernel():
    assert kernel_sha256() == IMMUTABLE_KERNEL_SHA256


def test_one_cpu_continuation_changes_independent_world_and_returns(tmp_path):
    body, layout = create_damaged_body(tmp_path / "damaged.mmap")
    assert body_material_count(body) == 513
    body.close()
    result = run_branch(
        tmp_path / "damaged.mmap",
        tmp_path / "matched",
        layout,
        line="A",
        seed=17,
        condition="matched",
    )
    assert result["trace"]["body_to_world"] > 0
    assert result["trace"]["world_to_body"] > 0
    assert result["world_changed"]
    assert result["world_return_earned_by_prior_world_change"]
    assert result["world_deleted"]
    assert result["upper_born"] and result["coarse_pass"]
    assert result["body_material_count"] == BODY_CAPACITY


def test_passive_world_contact_cannot_create_return_or_close_crack(tmp_path):
    body, layout = create_damaged_body(tmp_path / "damaged.mmap")
    body.close()
    result = run_branch(
        tmp_path / "damaged.mmap",
        tmp_path / "passive",
        layout,
        line="A",
        seed=17,
        condition="passive",
    )
    assert not result["world_changed"]
    assert not result["world_return_earned_by_prior_world_change"]
    assert result["trace"]["world_to_body"] == 0
    assert not result["upper_born"]
    assert not result["coarse_pass"]
    assert not result["body_changed"]


def test_controls_separate_by_resulting_BODY_and_later_behavior(tmp_path):
    body, layout = create_damaged_body(tmp_path / "damaged.mmap")
    body.close()
    result = run_paired_conditions(
        tmp_path / "damaged.mmap",
        tmp_path / "paired",
        layout,
        line="A",
        seed=23,
    )
    assert result["passed"]
    assert all(item["BODY"] for item in result["separations"].values())
    assert all(
        item["future_behavior"] for item in result["separations"].values()
    )
    assert all(item["passed"] for item in result["separations"].values())
    assert all(
        "world" not in field
        for probe in result["future_behavior"].values()
        for field in probe["signature"]
    )


def test_G0_cut_gives_one_exact_snapshot_for_honest_A_B_histories(tmp_path):
    damaged, layout = create_damaged_body(tmp_path / "template.mmap")
    damaged.close()
    g0 = run_branch(
        tmp_path / "template.mmap",
        tmp_path / "G0",
        layout,
        line="A",
        seed=17,
        condition="matched",
    )
    cut = cut_to_shared_damage(
        Path(g0["body_path"]),
        tmp_path / "shared_cut.mmap",
        tmp_path / "template.mmap",
        layout,
    )
    assert cut["exact_shared_snapshot"]
    a = run_paired_conditions(
        Path(cut["body_path"]),
        tmp_path / "A",
        layout,
        line="A",
        seed=17,
    )
    b = run_paired_conditions(
        Path(cut["body_path"]),
        tmp_path / "B",
        layout,
        line="B",
        seed=17,
    )
    assert a["passed"] and b["passed"]
    assert a["branches"]["matched"]["body_before_sha256"] == b["branches"]["matched"]["body_before_sha256"]
    assert a["branches"]["matched"]["body_sha256"] != b["branches"]["matched"]["body_sha256"]


def test_balanced_common_world_orders_read_different_future_lineages(tmp_path):
    body, layout = create_damaged_body(tmp_path / "damaged.mmap")
    body.close()
    a = run_branch(
        tmp_path / "damaged.mmap",
        tmp_path / "form_A",
        layout,
        line="A",
        seed=23,
        condition="matched",
    )
    b = run_branch(
        tmp_path / "damaged.mmap",
        tmp_path / "form_B",
        layout,
        line="B",
        seed=23,
        condition="matched",
    )
    future_a = balanced_common_lineage(
        Path(a["body_path"]),
        tmp_path / "future_A",
        layout,
        seed=23,
    )
    future_b = balanced_common_lineage(
        Path(b["body_path"]),
        tmp_path / "future_B",
        layout,
        seed=23,
    )
    analysis = analyze_lineages([{"A": future_a, "B": future_b}])
    assert future_a["passed"] and future_b["passed"]
    assert future_a["signature"] != future_b["signature"]
    assert analysis["lineages_reproducible_and_separated"]


def test_return_placement_owns_memory_but_node_addresses_do_not(tmp_path):
    body, layout = create_damaged_body(tmp_path / "damaged.mmap")
    body.close()
    formed = {}
    for line in ("A", "B"):
        formed[line] = run_branch(
            tmp_path / "damaged.mmap",
            tmp_path / f"form_{line}",
            layout,
            line=line,
            seed=41,
            condition="matched",
        )

    shuffled = {}
    relabeled = {}
    for line in ("A", "B"):
        source = Path(formed[line]["body_path"])
        shuffle_path = tmp_path / f"shuffle_{line}.mmap"
        audit = shuffle_return_placement(source, shuffle_path, 41)
        assert audit["return_multiset_unchanged"]
        assert audit["graph_and_material_unchanged"]
        assert audit["ordinary_upper_pass_survived"]
        shuffled[line] = balanced_common_lineage(
            shuffle_path,
            tmp_path / f"shuffle_future_{line}",
            layout,
            seed=41,
        )

        relabel_path = tmp_path / f"relabel_{line}.mmap"
        mapped_layout, relabel_audit = relabel_body(
            source,
            relabel_path,
            layout,
            41,
        )
        assert relabel_audit["body_isomorphic"]
        relabeled[line] = balanced_common_lineage(
            relabel_path,
            tmp_path / f"relabel_future_{line}",
            mapped_layout,
            seed=41,
        )

    assert shuffled["A"]["signature"] == shuffled["B"]["signature"]
    for line in ("A", "B"):
        original = balanced_common_lineage(
            Path(formed[line]["body_path"]),
            tmp_path / f"original_future_{line}",
            layout,
            seed=41,
        )
        assert relabeled[line]["signature"] == original["signature"]


def test_full_1024_serial_lineage_cli_has_all_112_controls(tmp_path):
    root = Path(__file__).parents[1]
    receipt = tmp_path / "receipt.json"
    completed = subprocess.run(
        [
            sys.executable,
            str(root / "run_world_lineage.py"),
            "--workdir",
            str(tmp_path / "run"),
            "--out",
            str(receipt),
        ],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    result = json.loads(receipt.read_text())
    assert completed.returncode == 0
    assert result["passed"]
    assert result["body_capacity"] == 1024
    assert result["controls_total"] == result["actual_controls_total"] == 112
    assert result["lineage_analysis"]["lineages_reproducible_and_separated"]
    assert result["hostile_memory"]["passed"]
    assert result["kernel_sha256"] == IMMUTABLE_KERNEL_SHA256
    for record in result["records"]:
        for line in ("A", "B"):
            washout = record["G1_common_washout"][line]
            recut = record["G2_recut"][line]
            assert washout["passed"]
            assert washout["source_body_sha256"] == washout["branch"][
                "body_before_sha256"
            ]
            assert recut["source_sha256"] == washout["body_sha256"]
            assert record["common_recut"][line]["AB"][
                "washed_source_sha256"
            ] == washout["body_sha256"]
            assert all(
                branch["body_before_sha256"] == recut["sha256"]
                for branch in record["G2"][line]["branches"].values()
            )
