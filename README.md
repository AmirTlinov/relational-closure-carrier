# Relational Closure Carrier

This repository is the first reproducible computational step in a broader
question: when does a difference exposed by contact become persistent memory in
the same non-neural substrate that later conducts repair? The public abstract
places this explicit-topology assay beside the later passage-based PC carrier
and the still-open physical carrier test. The code here remains deliberately
bounded: it tests whether retained relational placement can change later repair
without a complete-body target register, reward, or online external selection.

## Start here

- **[Public visual abstract](https://amirtlinov.github.io/relational-closure-carrier/)** — the two-page research argument from difference through contact, reentry, and repair.
- **[Русское зеркало](https://amirtlinov.github.io/relational-closure-carrier/ru/)** — тот же компактный абстракт, схема и отдельный двухстраничный PDF на русском.
- **[Two-page PDF](ABSTRACT.pdf)** / **[English text](ABSTRACT.md)** / **[Russian meaning mirror](ABSTRACT_RU.md)**.
- **[Technical extended abstract](TECHNICAL_ABSTRACT.md)** — the denser Relational Distinguishability account and full controls narrative.
- **[Evidence boundary](EVIDENCE.md)** — exact result, interventions, controls, and hashes.
- **[Reproduce](REPRODUCE.md)** — clean commands for tests and both experiments.

## Operational criterion and carrier hypothesis

An unexposed difference is not yet an experimentally established distinction.
Within a declared continuation domain, two retained histories count as
physically distinguishable only when substituting one for the other changes an
admissible later contact. The formal `D+` witness reads that consequence; it is
not a scheduler, memory selector, or routing law.

The carrier hypothesis is stricter:

> **A useful distinction becomes memory only when contact changes the same
> substrate that later conducts a changed continuation.**

In the broader hypothesis, a whole is a temporarily stable class of future
continuations, not an inventory of parts or a declared diagram. A new scale is
earned only when later contact encounters that closure as one whole. Injury
opens an unresolved continuation; repair may recover the previous class,
stabilize another, support new wholes, or fail into collapse.

## Reproducible claim of this repository

> In this prepared digital carrier, two histories of continuation through separately stored surrounding records are retained as different relational placements in the persistent group; they remain distinguishable in later repair after those temporary records are removed, the persistent snapshot alone is restarted, and an identical washout and injury are applied.

Here **relational distinguishability** has a narrow operational meaning: full
address relabeling preserves the A/B distinction, while shuffling the placement
of the candidate return-relation class erases it. The placement of that relation
class is therefore interventionally necessary for the observed A/B difference.

This is a bounded intervention result for history-dependent material memory in
an engineered arena. It is **not** presented as evidence of basal cognition, a
biological model, or a proof that morphogenesis lacks target states.

The open biological question is how to distinguish a distributed homeostatic
target from ordinary path-dependent hysteresis when present anatomy and
immediate behavior are matched but causal repair history differs.

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

## Snapshot

- body capacity: 1,024 relational sites;
- histories: A and B from one identical injured body;
- initializations: 17, 23, 41, 59 (prespecified deterministic seeds, not independent replicates);
- paired G1/G2 controls: 112;
- separate hostile memory interventions: 8 placement shuffles + 8 full relabels;
- single-mmap control: 1,029 records, 2,058 matched collision events, exact final-record isomorphism;
- current test suite: 22 passing tests;
- world-lineage executable source SHA-256: `d3ed7438372973ef17b61b01659569372bb8c9faf61c48b334ded6bedca962e8`.
