# Evidence boundary

## Claim under test

Two past passages across the witness labels `BODY → WORLD → BODY` change the
placement of relations inside the persistent group. After the temporary
`WORLD` records are removed, those placements survive a fresh-process restart
and common washout and remain distinguishable in the timing of closure after a
new injury.

This is a claim about Relational Distinguishability and history-dependent repair
in a prepared digital carrier. It is not a claim of biological regeneration or
basal cognition.

## Relational Distinguishability

> **No relation is physically meaningful unless its sides are distinguishable.**<br>
> **Отношение физически содержательно лишь постольку, поскольку его стороны различимы.**

The experiment operationalizes this postulate narrowly. A/B histories remain
distinguishable after world deletion, restart, common washout, and renewed
injury. Full node-address relabeling preserves that distinction; return-placement
shuffle removes it. This makes the distribution of the tested relation class
interventionally necessary for the observed A/B difference.

Any connection to relativity is proposed and programmatic, not derived. The
tested address-relabel invariance concerns graph storage labels and is not a
spacetime transformation.

## Carrier

- `BODY`: 1,024 records, 24 bytes each.
- One higher-order entry, one common relation, a 510-site action route, and two 256-site return routes.
- One immutable local collision kernel (`growth_carrier.py`).
- Explicit relation handles; storage address is not treated as geometry.
- A separately allocated temporary `WORLD` storage surface with independent
  state but the same record physics.

`BODY` and `WORLD` are harness labels for two mmap surfaces of the same record
physics. `MultiMmapArena` routes a handle to one file or the other; the frozen
local `collision` predicate does not inspect a BODY/WORLD type.

## Single-mmap flattening control

One prepared matched passage was executed twice:

1. in the normal 1,024-record BODY plus five-record WORLD arrangement;
2. in one direct 1,029-record `MmapBody` with no surface namespace in any
   non-sentinel handle.

The witness constructed a deterministic hostile fixed-point-free permutation of
all 1,029 nodes, mixing former BODY and WORLD records in one address field. The
receipt establishes:

- `2,058 / 2,058` collision events are isomorphic in full, including event kind,
  current place, met place, continuation, and changed-place tuple;
- `1,029 / 1,029` final `MaterialRecord` values are isomorphic;
- all flat non-sentinel handles are plain addresses `< 1,029` and carry no
  surface bits;
- the standard passage crosses BODY → WORLD and WORLD → BODY and earns its
  return before comparison.

This removes the two-file surface namespace as a necessary ingredient of that
one matched local trajectory. It does not remove the witness: the witness knows
the former surfaces and constructs the isomorphism.

## Serial assay

```text
G0 closure
→ one common cut (513 surviving material sites)
→ matched history A or B
→ delete WORLD
→ BODY-only fresh-process restart
→ identical common washout
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

| Intervention | Protocol dependency removed |
|---|---|
| `no_world` | no external world contact |
| `passive` | contact without action-dependent world transition |
| `disconnected` | world changes independently of body action |
| `mismatched` | world continuation has the wrong phase for the ongoing bodily passage |
| `delay` | return cannot complete under the matched finite collision budget |
| `permute` | return enters the other prepared route |
| `shuffle` | a pre-conducting phase-incompatible world route replaces action-dependent world formation |

Representation-class interventions:

- full node-address relabeling with relations preserved: body and future signature preserved;
- return-placement shuffle with material and other relations preserved: A/B future difference removed.

This identifies a relation class whose distribution is interventionally
necessary for the observed A/B distinction. It does not localize memory to a
small site.

Scale control:

- remove only the higher-order relation: large-scale passage disappears;
- preserve the lower route and traverse it again: the higher-order relation returns.

## Fresh verification

```text
pytest: 22 passed
ruff:   passed
```

Recorded source/evidence hashes:

```text
collision kernel SHA-256:
0d32047eecb391f572671a3404eb912fa3cc96ea3a39a44212328d5884d312f7

world-lineage source SHA-256:
d3ed7438372973ef17b61b01659569372bb8c9faf61c48b334ded6bedca962e8
```

The compact audits are in `results/`. Full receipts are regenerated locally because their ephemeral file paths are intentionally not published.

## Known limits

- prepared topology and two prepared return opportunities;
- experimenter-defined cut and readout;
- binary local gestures and deterministic transition rule;
- no metabolism, cells, ion channels, gap junctions, or endogenous bioelectric dynamics;
- no open-ended discovery of morphology or self-originated goal;
- address-relabel invariance is not a spacetime symmetry result;
- the single-mmap control covers one prepared matched passage, not world deletion,
  body-only restart, common washout, G2, or the paired control family;
- the flattening map is witness-constructed; a self-born BODY/WORLD boundary is
  not demonstrated;
- no independent replication.
