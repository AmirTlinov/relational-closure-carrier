# Evidence boundary

## Claim under test

A past `BODY → WORLD → BODY` contact changes the placement of relations inside `BODY`; after the original `WORLD` is deleted, this placement survives a fresh-process restart and common washout and causally changes the timing of closure after a new injury.

This is a claim about causal memory and history-dependent repair in a prepared digital carrier. It is not a claim of biological regeneration or basal cognition.

## Carrier

- `BODY`: 1,024 records, 24 bytes each.
- One higher-order entry, one common relation, a 510-site action route, and two 256-site return routes.
- One immutable local collision kernel (`growth_carrier.py`).
- Explicit relation handles; storage address is not treated as geometry.
- A separately created `WORLD` file with independent state.

## Serial assay

```text
G0 closure
→ one common cut (513 surviving material sites)
→ matched history A or B
→ delete WORLD
→ BODY-only fresh-process restart
→ identical causal common washout
→ cut the resulting current BODY
→ fresh A/B probes in both AB and BA order
```

The A/B worlds use equal resources and differ only in where an earned world return enters the body.

## Result

- Seeds: `17`, `23`, `41`, `59`.
- Full body after matched closure: `1,024` sites.
- Higher-order relation born at collision `772`.
- Maximum within-line signature distance: `0`.
- Minimum A/B signature distance: `2`.
- Paired control denominator: `4 seeds × 2 lines × 2 generations × 7 controls = 112`.
- Every control separated from matched both in resulting `BODY` bytes and in behavior after another common washout and injury.

## Controls

| Intervention | Broken causal link |
|---|---|
| `no_world` | no external world contact |
| `passive` | contact without action-dependent world transition |
| `disconnected` | world changes independently of body action |
| `mismatched` | world continuation has the wrong phase for the ongoing bodily passage |
| `delay` | return cannot complete under the matched finite collision budget |
| `permute` | return enters the other prepared route |
| `shuffle` | a pre-conducting phase-incompatible world route replaces action-dependent world formation |

Hostile localization:

- full node-address relabeling with relations preserved: body and future signature preserved;
- return-placement shuffle with material and other relations preserved: A/B future difference removed.

Scale control:

- remove only the higher-order relation: large-scale passage disappears;
- preserve the lower route and traverse it again: the higher-order relation returns.

## Fresh verification

```text
pytest: 21 passed
ruff:   passed
```

Recorded source/evidence hashes:

```text
collision kernel SHA-256:
0d32047eecb391f572671a3404eb912fa3cc96ea3a39a44212328d5884d312f7

world-lineage source SHA-256:
2ac3304f0a95d8a5e4533401f4727e1a0ee4e4c9e616da3321672866f590c1fd
```

The compact audits are in `results/`. Full receipts are regenerated locally because their ephemeral file paths are intentionally not published.

## Known limits

- prepared topology and two prepared return opportunities;
- experimenter-defined cut and readout;
- binary local gestures and deterministic transition rule;
- no metabolism, cells, ion channels, gap junctions, or endogenous bioelectric dynamics;
- no open-ended discovery of morphology or self-originated goal;
- no independent replication.
