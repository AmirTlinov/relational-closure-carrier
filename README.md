# Relational Closure Carrier

This repository implements the first reproducible computational step of a
broader claim: differences become distinguishability through contact, and
memory begins when contact changes the same carrier that later conducts a
different future. The experiment asks whether survived contact can change
renewed repair without a complete-body target register, reward, or online
external selection.

## Start here

- **[Public visual abstract](https://amirtlinov.github.io/relational-closure-carrier/)** — the two-page research argument from difference through contact, reentry, and repair.
- **[A Theory of Useful Differences](THEORY.pdf)** — the separate eight-page axiomatic companion: closure, injury, useful difference, charge, measurement, and the open derivations.
- **[Theory source](theory/source-brief.md)** / **[editable visual document](theory/atlas.html)** — the claim hierarchy and its print owner.
- **[Русское зеркало](https://amirtlinov.github.io/relational-closure-carrier/ru/)** — тот же компактный абстракт, схема и отдельный двухстраничный PDF на русском.
- **[Two-page PDF](ABSTRACT.pdf)** / **[English text](ABSTRACT.md)** / **[Russian meaning mirror](ABSTRACT_RU.md)**.
- **[Technical extended abstract](TECHNICAL_ABSTRACT.md)** — the denser Relational Distinguishability account and full controls narrative.
- **[Evidence boundary](EVIDENCE.md)** — exact result, interventions, controls, and hashes.
- **[Reproduce](REPRODUCE.md)** — clean commands for tests and both experiments.

## Differences, distinguishability, and memory

Differences exist before a contact in which they can become distinguishable.
Within a declared continuation domain, two retained histories are physically
distinguishable when substituting one for the other changes an admissible later
contact. The formal `D+` witness measures that future difference.

The carrier claim is material:

> **A distinguishability becomes memory when contact changes the same
> substrate that later conducts a changed continuation.**

In the broader hypothesis, a whole is a temporarily stable balance of mutually
sustaining differences. When later contact encounters that closure as one
operative unit, it becomes distinguishable as one whole at its scale and a new
difference at the next. Injury opens a deficit in that balance; reclosure may restore the
previous form, stabilize another, support new wholes, or end in collapse.

Zhang, Goldstein, and Levin's [minimal morphogenesis
model](https://doi.org/10.1177/10597123241269740) makes the transition visible
in bubble sort. An adjacent compare–swap resolves one inversion, so repeated
local completion drives the global inversion count to zero without any element
storing the final permutation. This repository takes the next step: whether the
same conducting substrate can retain contact history and thereby change a later
closure, rather than receiving every useful contact from the programmer.

## Reproducible claim of this repository

> In this prepared digital carrier, two histories of continuation through separately stored surrounding records are retained as different relational placements in the persistent group; they remain distinguishable in later repair after those temporary records are removed, the persistent snapshot alone is restarted, and an identical washout and injury are applied.

Here **relational distinguishability** has a narrow operational meaning: full
address relabeling preserves the A/B distinction, while shuffling the placement
of the candidate return-relation class erases it. The placement of that relation
class is therefore interventionally necessary for the observed A/B difference.

This establishes one causal slice of history-dependent material memory in an
engineered arena. The biological and basal-cognition claim belongs to the next
comparison: whether matched present tissues with different repair histories
close differently under a perturbation that does not supply the target form.

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

## Build the public documents

```bash
./scripts/build_public_abstract.sh
npm ci --prefix theory
./scripts/build_public_theory.sh
```

The abstract and theory have independent print contracts: the former remains a
two-page outreach artifact; the latter is an eight-page axiomatic companion.
`THEORY.pdf` states the author's physical theory and marks unfinished physical
derivations explicitly. The executable carrier assay does not by itself prove
those physical consequences.
