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
21 passed
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

The full receipt includes four seeds, A/B histories, two generations, and 112 paired controls. It is generated outside the repository because its internal paths are run-specific.

## What to inspect

- `passed` must be `true` in both receipts.
- `controls_total` and `actual_controls_total` must both equal `112` in the world-lineage receipt.
- `lineage_analysis.lineages_reproducible_and_separated` must be `true`.
- placement shuffle must remove the A/B future difference.
- full node relabeling must preserve body organization and future behavior.
