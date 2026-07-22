# Repository memory

## Responsibility

This repository owns the first public, reproducible **explicit-topology**
carrier assay. It tests whether different histories retained as relational
placement can survive restart and renewed injury and change later repair.

It also owns the public axiomatic companion `theory/source-brief.md`, its
editable visual owner `theory/atlas.html`, and the released `THEORY.pdf`.
The companion states the Theory of Useful Differences and keeps its formal
consequences separate from derivations that remain open.

The atlas uses author-derived raster scenes under `theory/illustrations/`.
Generated images own spatial explanation only; `source-brief.md` and HTML text
remain the sources of exact claims, formulas, captions, and evidence boundaries.
Imagegen may restyle author-supplied topology but must not invent it. Where no
author diagram exists, `atlas.html` uses an exact typographic mechanism instead.

It does not own the later private `one to two` carrier, a physical memristive
experiment, or a biological model. The executable assay does not prove the
companion's physical claims about charge, interference, or gravity.

## Causal contract

```text
contact -> retained local change -> world return -> reentry
        -> changed later contact
```

- `D+` is an external operational witness over admitted future continuations;
  it is not a routing law, scheduler, memory store, or carrier mechanism.
- A distinguishability counts as carrier memory when contact changes the
  same substrate that later conducts a changed continuation.
- The executable assay still has prepared topology, return opportunities,
  injury, and readout. Address relabeling is storage-label invariance, not a
  spacetime result.
- Public claims must distinguish the reproducible assay here from locally
  verified but not yet publicly bundled `one to two` evidence.

## Public narrative

`index.html` and `ru/index.html` are the editable visual-abstract sources.
They state the positive thesis before its evidence boundary. The canonical
claim is: **differences exist before a contact in which they can become
distinguishable**. Contact does not create differences; it lets already-existing
differences enter a shared physical consequence. Memory is changed future
conduct retained by the changed carrier; a stable closure is distinguishability
at one scale and a new difference at the next. A distinguishable body is a
temporarily stable balance of mutually sustaining differences, not an inventory
or drawn network. Injury opens a deficit whose reclosure can restore, transform,
divide, or collapse form. Regeneration does not replay a finished target: each
retained compatible completion narrows the continuations that can still close
the body, and a local closure becomes a difference at the next scale. Planarian
regeneration and measurement are developed from this thesis. The scientific
boundary appears once, at the end: the public assay proves one causal
computational slice, while carrier-owned physical contact remains the decisive
falsifiable test.

## Sorting analogy boundary

Zhang, Goldstein, and Levin's *Classical sorting algorithms as a model of
morphogenesis* (Adaptive Behavior 33(1), DOI
`10.1177/10597123241269740`) is the exact prior-art bridge. For ordinary bubble
sort, the inversion count
`I(a) = #{(i,j): i<j and a_i>a_j}` falls by exactly one whenever an adjacent
inverted pair is swapped, and `I=0` is the sorted condition. This is the exact
small case `local difference -> contact -> completion -> stable whole-scale
order`; no element stores the final permutation. The paper's cell-view variants
add damage tolerance, temporary regress under their sortedness measure, and
algotype clustering. Adjacency, comparison, update law, and goal interpretation
remain programmer-supplied, so the carrier program begins at the next ownership
boundary: whether substrate history can form and alter later contacts.

## Verification

```bash
./scripts/build_public_abstract.sh
npm ci --prefix theory
./scripts/build_public_theory.sh
uv run pytest -q
uv run ruff check .
./scripts/refresh_public_audit.py
```

Run the audit refresh last because it hashes the final publication bundle.
