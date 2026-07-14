# History-Dependent Repair in a Minimal Non-Neural Carrier

## A causal test of distributed pattern memory versus path-dependent attractor dynamics

**Amir Tlinov — Independent Researcher**<br>
**14 July 2026**<br>
**Materials:** [github.com/AmirTlinov/relational-closure-carrier](https://github.com/AmirTlinov/relational-closure-carrier)

### Biological question

Work on anatomical homeostasis and basal cognition treats morphogenesis as
collective problem-solving in morphospace: tissues can recover large-scale
organization after perturbation, while physiological networks retain history
not reducible to current anatomy alone [1–4]. I ask a narrower mechanistic
question:

> Can later repair depend on history retained in the causal organization of the
> same substrate that conducts repair—without a separate complete-body target
> model, global controller, reward signal, or online external selection inside
> the modeled loop?

The contribution is a joint intervention assay. One local-rule carrier must
earn closure through body–world contact, retain the resulting relational history
after the world is deleted, express that history during a later matched injury,
and lose the A/B difference when the candidate representation is disrupted.
This is a computational existence test, not a theory of biological regeneration
or fundamental physics.

### Carrier and causal provenance

The deterministic carrier contains 1,024 writable relational records. Each
stores a small local state and explicit handles to available contacts and
conducting relations. One immutable collision rule updates one linked encounter
at a time. It has no global sweep, coordinate arithmetic, fitness function,
symbolic planner, runtime target register, or reward channel.

The external harness prepares the topology, declared injury, worlds, and
readout. It fixes whether the earned return opportunity is A or B before a run;
it does not select a relation online during execution. The prepared upper slot
and two return routes are explicit limitations.

The body acts through a separately created five-record `WORLD` using the same
record format and collision rule as `BODY`. A return counts as earned only if
the ongoing bodily passage first changes the particular world record from which
the continuation later returns:

```text
BODY action → changed WORLD site → return to BODY → closure
```

Passive contact, a disconnected world change, a phase mismatch, or a prewritten
conducting route cannot substitute for that sequence.

### History-dependent repair assay

Lines A and B begin from the same injured body containing 513 occupied records.
Their worlds have equal resources and differ only in the physical placement of
the earned final return into one of two prepared bodily routes. Both lines
recover the full 1,024-record body and the same immediately available
higher-order conductance.

The original worlds are then deleted. Only each `BODY` file survives. Every body
is reopened by a fresh process, exposed to the same causal common washout, and
cut again at the same current relation. Repair is probed in fresh A and B worlds
in both orders (`AB` and `BA`). The assay asks not whether a log can classify
history, but whether surviving relational placement is necessary for different
future conduct.

### Result and interventions

Line A restored the upper entry in episode 1 of `AB` and episode 2 of `BA`;
line B gave the mirror result—episode 2 of `AB` and episode 1 of `BA`. The exact
pattern repeated in four prespecified deterministic initializations (`17`,
`23`, `41`, `59`); these are not independent experimental replicates.

Across G1 and G2, 112 paired controls varied world absence, passivity,
connectivity, continuation phase, delay under the same finite collision budget,
choice of the other prepared return route, or replacement of action-dependent
world formation by a pre-conducting phase-incompatible route. Every control
separated from matched both in resulting `BODY` bytes and in behavior after a
further common washout and injury.

Two separate representation-class interventions tested what carries the A/B
difference:

- complete relabeling of storage addresses while preserving relations preserved
  body organization and future behavior;
- shuffling the placement of all 257 candidate return relations erased the A/B
  future difference while preserving their multiset, material extent, current
  higher-order conductance, and the other relation classes.

Thus the distribution of this relation class is causally necessary in the
prepared carrier. The intervention does not localize memory to a small site.

A separate closure intervention used one 12-place lower cycle. After that cycle
had earned an upper relation by closing, removing only that relation changed a
one-collision `PASS` to `HALT` while the lower cycle remained traversable. One
new pass through the surviving cycle rematerialized the upper relation at
collision 12 and restored `PASS`.

The bounded result is:

> Past world contact is retained as changed relational placement in this body,
> and that placement causally changes later repair after world deletion,
> fresh-process restart, common washout, and renewed injury.

The frozen public source passes 21 tests. The evidence bundle records four
prespecified deterministic initializations, 112 paired world-continuity
controls, eight placement shuffles, and eight full node relabelings. Collision
kernel SHA-256: `0d32047eecb3…`; world-lineage executable source SHA-256:
`2ac3304f0a95…`.

### Limits and requested interpretation

The topology, closure affordance, two return routes, injury, and readout are
engineered. `WORLD` is a second instance of the same digital physics, not a
distinct material class, and the harness chooses A/B return placement before
execution. The carrier does not originate its boundary, discover a morphology,
maintain metabolism, or form its own goals. It is not a model of cells, ion
channels, gap junctions, or endogenous bioelectric dynamics; it has not been
independently replicated. I do not present it as evidence of basal cognition or
as evidence that morphogenesis lacks target states.

The ambiguity is the point: the runtime has no separate symbolic model of a
completed body, yet the prepared topology encodes a closure affordance and the
history-bearing relational state changes future repair. These may constitute a
minimal distributed pattern memory or homeostatic target, path-dependent
attractor dynamics, or both descriptions at different causal levels.

> Would you regard the topology-encoded closure affordance and history-bearing
> relational state as a minimal distributed pattern memory or homeostatic
> target, only as a path-dependent attractor, or as both? What single
> perturbation would best distinguish their causal roles?

### References

1. Levin M. [Technological Approach to Mind Everywhere](https://doi.org/10.3389/fnsys.2022.768201). *Frontiers in Systems Neuroscience*. 2022.
2. Durant F, et al. [Long-Term, Stochastic Editing of Regenerative Anatomy via Targeting Endogenous Bioelectric Gradients](https://pubmed.ncbi.nlm.nih.gov/28538159/). *Biophysical Journal*. 2017.
3. Manicka S, Levin M. [Modeling somatic computation with non-neural bioelectric networks](https://doi.org/10.1038/s41598-019-54859-8). *Scientific Reports*. 2019.
4. Levin M. [Bioelectric networks: the cognitive glue enabling evolutionary scaling from physiology to mind](https://doi.org/10.1007/s10071-023-01780-3). *Animal Cognition*. 2023.
