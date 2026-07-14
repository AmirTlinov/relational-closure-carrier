#!/usr/bin/env python3
"""Source-hashed 1024 BODY -> WORLD -> A/B serial lineage receipt."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

from world_lineage import (
    BODY_CAPACITY,
    CONDITIONS,
    IMMUTABLE_KERNEL_SHA256,
    SIGNATURE_FEATURES,
    analyze_lineages,
    assert_immutable_kernel,
    balanced_common_lineage,
    body_material_count,
    body_sha256,
    canonical_layout,
    common_world_washout,
    controls_receipt,
    create_damaged_body,
    cut_to_shared_damage,
    kernel_sha256,
    ordinary_life_baseline,
    recut_upper,
    relabel_body,
    run_branch,
    run_paired_conditions,
    shuffle_return_placement,
)


ROOT = Path(__file__).resolve().parent
DEFAULT_SEEDS = (17, 23, 41, 59)


def source_hash() -> str:
    digest = hashlib.sha256()
    for path in (
        ROOT / "growth_carrier.py",
        ROOT / "world_lineage.py",
        ROOT / "run_world_lineage.py",
    ):
        digest.update(path.name.encode())
        digest.update(b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def fresh_process_restart(
    body_path: Path,
    root: Path,
    *,
    line: str,
    seed: int,
) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    restarted = root / "BODY_ONLY.mmap"
    shutil.copyfile(body_path, restarted)
    exact = restarted.read_bytes() == body_path.read_bytes()
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--probe-body",
            str(restarted),
            "--probe-line",
            line,
            "--probe-seed",
            str(seed),
            "--probe-root",
            str(root / "fresh_process"),
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    probe = json.loads(completed.stdout)
    return {
        "body_path": str(restarted),
        "exact_body_only_copy": exact,
        "fresh_process": probe,
        "passed": exact and probe["passed"],
    }


def one_seed(
    damaged_body: Path,
    root: Path,
    *,
    seed: int,
) -> tuple[dict, tuple[dict, dict], tuple[dict, dict]]:
    root.mkdir(parents=True, exist_ok=True)
    layout = canonical_layout()
    g1_controls = {}
    g2_controls = {}
    baselines = {}
    restarts = {}
    common_washouts = {}
    common = {}
    g2_recuts = {}
    matched_hashes = {}
    damaged_sha = body_sha256(damaged_body)

    for line in ("A", "B"):
        g1 = run_paired_conditions(
            damaged_body,
            root / "G1" / line,
            layout,
            line=line,
            seed=seed,
        )
        g1_controls[line] = g1
        g1_body = Path(g1["matched_body"])
        matched_hashes[line] = body_sha256(g1_body)
        restarts[line] = fresh_process_restart(
            g1_body,
            root / "restart" / line,
            line=line,
            seed=seed,
        )
        restarted_body = Path(restarts[line]["body_path"])
        baselines[line] = ordinary_life_baseline(
            restarted_body,
            root / "baseline_G1" / line,
            layout,
            line=line,
            seed=seed,
            worlds=3,
        )
        common_washouts[line] = common_world_washout(
            restarted_body,
            root / "G1_common_washout" / line,
            layout,
            seed=seed + 3_000_007,
        )
        washed_body = Path(common_washouts[line]["body_path"])
        common[line] = balanced_common_lineage(
            washed_body,
            root / "common_lineage" / line,
            layout,
            seed=seed,
        )

        recut = recut_upper(
            washed_body,
            root / "G2" / line / "recut_BODY.mmap",
            layout,
        )
        g2_recuts[line] = recut
        g2_controls[line] = run_paired_conditions(
            Path(recut["body_path"]),
            root / "G2" / line / "branches",
            layout,
            line=line,
            seed=seed + 2_000_003,
        )

    same_material_count = all(
        g1_controls[line]["branches"]["matched"]["body_material_count"]
        == BODY_CAPACITY
        for line in ("A", "B")
    )
    checks = {
        "same_damaged_snapshot_for_A_B": all(
            g1_controls[line]["branches"][condition]["body_before_sha256"]
            == damaged_sha
            for line in ("A", "B")
            for condition in CONDITIONS
        ),
        "both_G1_histories_causally_closed": all(
            g1_controls[line]["passed"] for line in ("A", "B")
        ),
        "G1_A_B_bodies_differ": matched_hashes["A"] != matched_hashes["B"],
        "G1_A_B_both_use_1024_material_places": same_material_count,
        "ordinary_G1_baselines_pass": all(
            baselines[line]["passed"] for line in ("A", "B")
        ),
        "body_only_fresh_process_restarts_pass": all(
            restarts[line]["passed"] for line in ("A", "B")
        ),
        "both_G1_bodies_passed_identical_common_washout": all(
            common_washouts[line]["passed"] for line in ("A", "B")
        ),
        "common_washout_started_from_restarted_BODY": all(
            common_washouts[line]["source_body_sha256"]
            == body_sha256(Path(restarts[line]["body_path"]))
            == common_washouts[line]["branch"]["body_before_sha256"]
            for line in ("A", "B")
        ),
        "A_B_memory_survived_restart_and_common_washout": common_washouts[
            "A"
        ]["body_sha256"]
        != common_washouts["B"]["body_sha256"],
        "same_common_recut_eventually_restores_both": all(
            common[line]["passed"] for line in ("A", "B")
        ),
        "A_B_future_responses_differ": (
            common["A"]["signature"] != common["B"]["signature"]
        ),
        "both_G2_generations_pass_controls": all(
            g2_controls[line]["passed"] for line in ("A", "B")
        ),
        "G2_recut_used_exact_restarted_common_washout_BODY": all(
            g2_recuts[line]["source_sha256"]
            == common_washouts[line]["body_sha256"]
            and all(
                branch["body_before_sha256"] == g2_recuts[line]["sha256"]
                for branch in g2_controls[line]["branches"].values()
            )
            for line in ("A", "B")
        ),
    }
    record = {
        "seed": seed,
        "G1": g1_controls,
        "G1_baseline": baselines,
        "restart": restarts,
        "G1_common_washout": common_washouts,
        "common_recut": common,
        "G2_recut": g2_recuts,
        "G2": g2_controls,
        "A": common["A"],
        "B": common["B"],
        "checks": checks,
        "passed": all(checks.values()),
    }
    return record, (g1_controls["A"], g1_controls["B"]), (
        g2_controls["A"],
        g2_controls["B"],
    )


def hostile_memory_controls(
    records: list[dict],
    root: Path,
) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    layout = canonical_layout()
    shuffled_records = []
    relabeled_records = []
    shuffle_audits = []
    relabel_audits = []
    hostile_washouts = []

    for record in records:
        seed = record["seed"]
        shuffled_pair = {}
        relabeled_pair = {}
        for line in ("A", "B"):
            g1_body = Path(record["G1"][line]["matched_body"])
            shuffle_path = root / f"seed_{seed}" / line / "shuffled_BODY.mmap"
            shuffle_path.parent.mkdir(parents=True, exist_ok=True)
            shuffle_audit = shuffle_return_placement(
                g1_body,
                shuffle_path,
                seed + (101 if line == "A" else 211),
            )
            shuffle_audits.append(shuffle_audit)
            shuffled_washout = common_world_washout(
                shuffle_path,
                root / f"seed_{seed}" / line / "shuffled_washout",
                layout,
                seed=seed + 3_000_007,
            )
            hostile_washouts.append(shuffled_washout)
            shuffled_pair[line] = balanced_common_lineage(
                Path(shuffled_washout["body_path"]),
                root / f"seed_{seed}" / line / "shuffled_common",
                layout,
                seed=seed,
            )

            relabel_path = root / f"seed_{seed}" / line / "relabeled_BODY.mmap"
            relabeled_layout, relabel_audit = relabel_body(
                g1_body,
                relabel_path,
                layout,
                seed + (307 if line == "A" else 401),
            )
            relabel_audits.append(relabel_audit)
            relabeled_washout = common_world_washout(
                relabel_path,
                root / f"seed_{seed}" / line / "relabeled_washout",
                relabeled_layout,
                seed=seed + 3_000_007,
            )
            hostile_washouts.append(relabeled_washout)
            relabeled_pair[line] = balanced_common_lineage(
                Path(relabeled_washout["body_path"]),
                root / f"seed_{seed}" / line / "relabeled_common",
                relabeled_layout,
                seed=seed,
            )

        shuffled_records.append(
            {"seed": seed, "A": shuffled_pair["A"], "B": shuffled_pair["B"]}
        )
        relabeled_records.append(
            {"seed": seed, "A": relabeled_pair["A"], "B": relabeled_pair["B"]}
        )

    shuffled_analysis = analyze_lineages(shuffled_records)
    relabel_exact = all(
        relabeled["A"]["signature"] == original["A"]["signature"]
        and relabeled["B"]["signature"] == original["B"]["signature"]
        for original, relabeled in zip(records, relabeled_records, strict=True)
    )
    checks = {
        "shuffle_preserved_return_multisets": all(
            audit["return_multiset_unchanged"] for audit in shuffle_audits
        ),
        "shuffle_preserved_graph_and_current_life": all(
            audit["graph_and_material_unchanged"]
            and audit["ordinary_upper_pass_survived"]
            for audit in shuffle_audits
        ),
        "shuffle_destroyed_A_B_future_separation": not shuffled_analysis[
            "lineages_reproducible_and_separated"
        ],
        "hostile_bodies_passed_same_common_washout": all(
            washout["passed"] for washout in hostile_washouts
        ),
        "node_relabel_was_hostile": all(
            audit["permutation_is_hostile"] for audit in relabel_audits
        ),
        "node_relabel_preserved_physical_body": all(
            audit["body_isomorphic"] for audit in relabel_audits
        ),
        "node_relabel_preserved_future_signatures": relabel_exact,
    }
    return {
        "shuffle_audits": shuffle_audits,
        "shuffled_analysis": shuffled_analysis,
        "relabel_audits": relabel_audits,
        "common_washouts": hostile_washouts,
        "checks": checks,
        "passed": all(checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workdir",
        type=Path,
        default=ROOT / "results" / "world_lineage_1024",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "results" / "world_lineage_1024.json",
    )
    parser.add_argument("--seeds", type=int, nargs="+", default=DEFAULT_SEEDS)
    parser.add_argument("--probe-body", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--probe-line", choices=("A", "B"), help=argparse.SUPPRESS)
    parser.add_argument("--probe-seed", type=int, default=17, help=argparse.SUPPRESS)
    parser.add_argument("--probe-root", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()

    assert_immutable_kernel()
    if args.probe_body is not None:
        if args.probe_line is None or args.probe_root is None:
            raise ValueError("fresh-process probe needs line and root")
        before = args.probe_body.read_bytes()
        baseline = ordinary_life_baseline(
            args.probe_body,
            args.probe_root,
            canonical_layout(),
            line=args.probe_line,
            seed=args.probe_seed,
            worlds=1,
        )
        print(
            json.dumps(
                {
                    "kernel_sha256": kernel_sha256(),
                    "body_source_unchanged": before == args.probe_body.read_bytes(),
                    "baseline": baseline,
                    "passed": baseline["passed"]
                    and before == args.probe_body.read_bytes(),
                }
            )
        )
        return 0

    started_utc = datetime.now(timezone.utc).isoformat()
    initial_source = source_hash()
    initial_kernel = kernel_sha256()
    if args.workdir.exists():
        shutil.rmtree(args.workdir)
    args.workdir.mkdir(parents=True)

    damaged_template = args.workdir / "damaged_template_1024.mmap"
    damaged, layout = create_damaged_body(damaged_template)
    damaged_material = body_material_count(damaged)
    damaged.close()

    g0 = run_branch(
        damaged_template,
        args.workdir / "G0_formation",
        layout,
        line="A",
        seed=args.seeds[0],
        condition="matched",
    )
    shared_cut = cut_to_shared_damage(
        Path(g0["body_path"]),
        args.workdir / "shared_cut_1024.mmap",
        damaged_template,
        layout,
    )
    shared_damaged = Path(shared_cut["body_path"])

    records = []
    g1_control_records = []
    g2_control_records = []
    for seed in args.seeds:
        record, g1_pair, g2_pair = one_seed(
            shared_damaged,
            args.workdir / f"seed_{seed}",
            seed=seed,
        )
        records.append(record)
        g1_control_records.extend(g1_pair)
        g2_control_records.extend(g2_pair)

    lineage = analyze_lineages(records)
    hostile = hostile_memory_controls(records, args.workdir / "hostile_memory")
    g1_controls = controls_receipt(g1_control_records)
    g2_controls = controls_receipt(g2_control_records)
    controls_total = len(args.seeds) * 2 * 2 * (len(CONDITIONS) - 1)
    actual_controls_total = sum(
        len(record["branches"]) - 1
        for record in (*g1_control_records, *g2_control_records)
    )
    final_source = source_hash()
    final_kernel = kernel_sha256()
    checks = {
        "immutable_collision_kernel_exact": initial_kernel
        == IMMUTABLE_KERNEL_SHA256
        == final_kernel,
        "G0_formed_1024_through_independent_world": g0["upper_born"]
        and g0["body_material_count"] == BODY_CAPACITY
        and g0["world_deleted"],
        "external_cut_produced_shared_A_B_snapshot": shared_cut[
            "exact_shared_snapshot"
        ]
        and shared_cut["material_count"] == damaged_material,
        "all_seed_lineage_records_passed": all(record["passed"] for record in records),
        "G1_all_controls_passed": g1_controls["passed"],
        "G2_all_controls_passed": g2_controls["passed"],
        "all_matched_returns_were_earned_by_world_change": g1_controls[
            "all_matched_returns_earned_by_world_change"
        ]
        and g2_controls["all_matched_returns_earned_by_world_change"],
        "passive_never_closed_a_crack": g1_controls[
            "no_passive_branch_closed_a_crack"
        ]
        and g2_controls["no_passive_branch_closed_a_crack"],
        "controls_separated_in_BODY_and_future_behavior": g1_controls[
            "all_resulting_BODIES_separated"
        ]
        and g1_controls["all_future_behaviors_separated"]
        and g2_controls["all_resulting_BODIES_separated"]
        and g2_controls["all_future_behaviors_separated"],
        "every_G2_descended_from_restarted_common_washout_BODY": all(
            record["checks"][
                "G2_recut_used_exact_restarted_common_washout_BODY"
            ]
            and record["checks"]["common_washout_started_from_restarted_BODY"]
            for record in records
        ),
        "full_112_control_denominator_present": controls_total
        == actual_controls_total
        == 112,
        "A_B_lineages_reproducible_and_separated": lineage[
            "lineages_reproducible_and_separated"
        ],
        "memory_owner_and_node_relabel_controls_passed": hostile["passed"],
        "all_world_mmaps_removed": g1_controls["all_worlds_deleted"]
        and g2_controls["all_worlds_deleted"]
        and not any(args.workdir.rglob("WORLD.mmap")),
        "source_unchanged": initial_source == final_source,
    }
    report = {
        "artifact_kind": "frozen_kernel_independent_world_serial_AB_lineage_receipt",
        "claim": "serial_world_lineage_carrier",
        "started_utc": started_utc,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "source_hash": initial_source,
        "final_source_hash": final_source,
        "kernel_sha256": initial_kernel,
        "required_kernel_sha256": IMMUTABLE_KERNEL_SHA256,
        "body_capacity": BODY_CAPACITY,
        "seeds": list(args.seeds),
        "signature_features": list(SIGNATURE_FEATURES),
        "G0_audit": g0,
        "shared_cut": shared_cut,
        "records": records,
        "lineage_analysis": lineage,
        "hostile_memory": hostile,
        "G1_controls": g1_controls,
        "G2_controls": g2_controls,
        "controls_total": controls_total,
        "actual_controls_total": actual_controls_total,
        "checks": checks,
        "passed": all(checks.values()),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(
        json.dumps(
            {
                "passed": report["passed"],
                "claim": report["claim"],
                "source_hash": initial_source,
                "kernel_sha256": initial_kernel,
                "checks": checks,
                "lineage_analysis": lineage,
                "hostile_memory_checks": hostile["checks"],
                "controls_total": controls_total,
            },
            ensure_ascii=False,
        )
    )
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
