# Relational Closure Carrier

A minimal computational experiment asking whether two histories of contact
across witness-labeled regions of one relational material, retained as changed
relational placement, remain distinguishable in later repair—without a
complete-body target register, reward, or online external selection inside the
modeled loop.

## Start here

- **[Public visual abstract](https://amirtlinov.github.io/relational-closure-carrier/)** — the primary two-page argument and biological question.
- **[Русское зеркало](https://amirtlinov.github.io/relational-closure-carrier/ru/)** — тот же компактный абстракт, схема и отдельный двухстраничный PDF на русском.
- **[Two-page PDF](ABSTRACT.pdf)** / **[English text](ABSTRACT.md)** / **[Russian meaning mirror](ABSTRACT_RU.md)**.
- **[Technical extended abstract](TECHNICAL_ABSTRACT.md)** — the denser Relational Distinguishability account and full controls narrative.
- **[Evidence boundary](EVIDENCE.md)** — exact result, interventions, controls, and hashes.
- **[Reproduce](REPRODUCE.md)** — clean commands for tests and both experiments.

## Current claim

> In this prepared digital carrier, two histories of continuation through separately stored surrounding records are retained as different relational placements in the persistent group; they remain distinguishable in later repair after those temporary records are removed, the persistent snapshot alone is restarted, and an identical washout and injury are applied.

The governing postulate is:

> **No relation is physically meaningful unless its sides are distinguishable.**<br>
> **Отношение физически содержательно лишь постольку, поскольку его стороны различимы.**

Here **Relational Distinguishability** has a narrow operational meaning: full
address relabeling preserves the A/B distinction, while shuffling the placement
of the candidate return-relation class erases it. The placement of that relation
class is therefore interventionally necessary for the observed A/B difference.

This is a bounded intervention result for history-dependent material memory in
an engineered arena. It is **not** presented as evidence of basal cognition, a
biological model, or a proof that morphogenesis lacks target states.

The open interpretation is whether the prepared closure affordance plus the
history-bearing relational state should count as a minimal distributed pattern
memory or homeostatic target, only as a path-dependent attractor, or as both at
different organizational levels.

The graph, an explicit empty upper slot, the A/B return routes, injury, and readout are engineered. The higher-order conducting relation itself is not pre-installed: it appears only after the lower route actually closes, disappears under targeted ablation, and is restored by a new traversal of surviving material. A/B identity is assigned by the harness through one of the prepared routes.

## Relational provenance chain

```text
ongoing continuation in the retained group
        ↓
actual change to an independently stored surrounding record
        ↓
earned return from that changed record into the retained group
        ↓
changed relational placement survives removal of the temporary records
        ↓
future injury produces history-dependent closure
```

The implementation uses one local collision kernel and explicit relation
handles. Address relabeling preserves the result; shuffling the placement of
the history-bearing relations erases the A/B future difference.

## Witness boundary and single-mmap control

`BODY` and `WORLD` are harness labels for two storage surfaces using the same
`MaterialRecord` format and the same local record physics. The surface router
uses those labels to choose an mmap file, but the frozen `collision` predicate
does not inspect a BODY/WORLD type.

For one prepared matched passage, the witness flattened all 1,024 former BODY
records and five former WORLD records into one direct `MmapBody`. A deterministic
hostile fixed-point-free permutation mixed all 1,029 nodes in one address field,
and every non-sentinel handle became a plain address below 1,029 with no surface
namespace. The two-surface and flat executions matched event-for-event across
all `2,058 / 2,058` collisions, and all `1,029 / 1,029` final `MaterialRecord`
values were isomorphic.

This proves that the two-surface namespace is dynamically unnecessary for that
one matched passage. It does **not** flatten world deletion, body-only restart,
common washout, G2, or the paired controls. The witness constructs the mapping;
the carrier has not been shown to originate its own BODY/WORLD boundary.

The connection to relativity is **proposed and programmatic**, not derived: both
directions emphasize description through relations rather than privileged
absolute labels. The tested address-relabel invariance is invariance to graph
storage labels; it is **not** a spacetime transformation, Lorentz invariance, or
general covariance.

## Snapshot

- body capacity: 1,024 relational sites;
- histories: A and B from one identical injured body;
- initializations: 17, 23, 41, 59 (prespecified deterministic seeds, not independent replicates);
- paired G1/G2 controls: 112;
- separate hostile memory interventions: 8 placement shuffles + 8 full relabels;
- single-mmap control: 1,029 records, 2,058 matched collision events, exact final-record isomorphism;
- current test suite: 22 passing tests;
- world-lineage executable source SHA-256: `d3ed7438372973ef17b61b01659569372bb8c9faf61c48b334ded6bedca962e8`.
