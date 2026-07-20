# Reproduce

## Requirements

- Python 3.12 or later
- [`uv`](https://docs.astral.sh/uv/)

## Install and verify

```bash
git clone https://github.com/AmirTlinov/relational-closure-carrier.git
cd relational-closure-carrier
uv sync --extra test

uv run --extra test pytest -q -p no:cacheprovider -o addopts=''
uv run --extra test ruff check \
  growth_carrier.py run_growth.py \
  world_lineage.py run_world_lineage.py tests
```

Expected test result:

```text
22 passed
```

## Rebuild the public abstract

The English and Russian pages are the editable publication sources. Rebuild
their two-page A4 PDFs and first-page previews with:

```bash
./scripts/build_public_abstract.sh
```

After the publication files and all checks are final, refresh the compact
publication hashes:

```bash
./scripts/refresh_public_audit.py
```

Run the audit refresh last: it records the exact bytes of the public bundle.

To run only the single-mmap flattening control test:

```bash
uv run --extra test pytest -q -p no:cacheprovider -o addopts='' \
  tests/test_world_lineage.py::test_matched_pass_isomorphic_in_one_hostilely_permuted_mmap
```

## Local growth and scale intervention

```bash
rm -rf /tmp/relational-closure-growth
uv run python run_growth.py \
  --workdir /tmp/relational-closure-growth/bodies \
  --out /tmp/relational-closure-growth/receipt.json
```

The receipt covers closed routes of several depths, unclosed retraction, incompatible contact, address relabeling, higher-order ablation, and restoration through the surviving lower route.

## Serial world-lineage assay

```bash
rm -rf /tmp/relational-closure-lineage
uv run python run_world_lineage.py \
  --workdir /tmp/relational-closure-lineage/bodies \
  --out /tmp/relational-closure-lineage/receipt.json
```

The full receipt includes four seeds, A/B histories, two generations, 112
paired controls, and `single_mmap_flattening` for one prepared matched passage.
That control compares the ordinary two-surface run with one direct 1,029-record
`MmapBody` after a deterministic hostile fixed-point-free permutation. It is
generated outside the repository because its internal paths are run-specific.

## What to inspect

- `passed` must be `true` in both receipts.
- `controls_total` and `actual_controls_total` must both equal `112` in the world-lineage receipt.
- `lineage_analysis.lineages_reproducible_and_separated` must be `true`.
- `single_mmap_flattening.passed` must be `true`.
- both values in `single_mmap_flattening.collision_counts` must equal `2058`.
- `single_mmap_flattening.final_record_count` must equal `1029`.
- `single_mmap_flattening.checks.entire_collision_trace_isomorphic`,
  `all_final_MaterialRecords_isomorphic`,
  `all_flat_handles_within_capacity`, and
  `no_surface_namespace_in_flat_handles` must all be `true`.
- placement shuffle must remove the A/B future difference.
- full node relabeling must preserve body organization and future behavior.

The flat control is a witness-constructed isomorphism for one matched passage.
It does not flatten world deletion, body-only restart, common washout, G2, or
the paired controls, and it does not demonstrate a self-born BODY/WORLD boundary.

The executable source identity for this result is:

```text
d3ed7438372973ef17b61b01659569372bb8c9faf61c48b334ded6bedca962e8
```
