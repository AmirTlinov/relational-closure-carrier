# Can Repair Arise from Changed Relational Organization Rather Than an Explicit Stored Target?

## A minimal non-neural carrier experiment

**Amir Tlinov — Independent Researcher**  
**14 July 2026**  
**Materials:** [github.com/AmirTlinov/relational-closure-carrier](https://github.com/AmirTlinov/relational-closure-carrier)

### Biological boundary

Work on anatomical homeostasis and basal cognition treats morphogenesis as a form of collective problem-solving in morphospace: a body can reach or recover large-scale organization despite perturbation, while physiological networks retain information that is not reducible to current anatomy alone [1–4]. I am exploring a narrow mechanistic question inside that program:

> Can target-like repair arise from history retained in the relational organization of the same substrate that later conducts repair, without a separate complete-body target model, global controller, reward signal, or online external selection inside the modeled loop?

The motivating hypothesis is relational:

> **No relation is physically meaningful unless its sides are distinguishable.**<br>
> **Отношение физически содержательно лишь постольку, поскольку его стороны различимы.**

Motion or contact alone need not create an operative unit. When distinguishable states modify one another and remain coupled so that their relation changes later propagation, they form what I call a **held difference**: a group that can act as one operative relational unit without erasing its internal distinction. At the scale of a body, injury then changes not only a local site but the organization of the surviving whole. Repair need not reproduce the previous component exactly; it may restore a group-level capability by forming a different relation with the surviving material.

This is an experimental heuristic, not a demonstrated account of biological regeneration or a claim about fundamental physics. The computational experiment asks only whether one clean, interventionally testable fragment of this hypothesis can be realized.

The proposed connection to relativity is programmatic: physical description may
be grounded in relations between distinguishable sides rather than privileged
absolute labels. No result in relativity is derived here. In particular, the
tested invariance under hostile address relabeling is invariance to graph
storage labels, not a spacetime transformation, Lorentz invariance, or general
covariance.

### Minimal carrier

The carrier is a deterministic, non-neural computational dynamical system with explicit body–world coupling. Its body contains 1,024 writable relational sites in a memory-mapped file. Each site stores a small local state and explicit handles to available contacts and conducting relations. One finite local collision rule is used throughout. It has no global sweep, coordinate arithmetic, fitness function, symbolic planner, runtime comparison with a completed form, or channel carrying reward.

The same rule can:

1. conduct change through an existing relation;
2. occupy material available through the current relations;
3. retract a route that fails to close;
4. form a higher-order conducting relation only after a lower route physically returns to its origin.

The external harness prepares the arena and reads the result, but it does not select a relation during execution.

The body contacts a separately created `WORLD` substrate. The same collision rule operates across both files. A continuation from `WORLD` back into `BODY` counts as an earned return only if the ongoing bodily action first changed the particular world site from which that return later emerged:

```text
BODY action → changed WORLD site → return to BODY → closure
```

Passive contact, a disconnected world change, or a prewritten return state therefore cannot substitute for this body–world provenance sequence.

### History-dependent repair assay

Two lines, A and B, begin from the same injured 513-site body. Their worlds have equal resources and differ only in the physical placement of the earned return into one of two bodily routes. Both lines recover the full 1,024-site body and the same higher-order conducting capacity.

The original worlds are then deleted. Only each `BODY` file survives. Every body is reopened in a fresh process, exposed to the same common washout, and cut again at the same current relation. Future repair is probed in fresh A and B worlds in both orders (`AB` and `BA`).

The question is not whether a log can classify the histories. It is whether the surviving placement of relations inside the body is necessary for different future conduct.

### Result

Across seeds 17, 23, 41, and 59, histories A and B produced bodies with the same material extent and the same immediately available large-scale conductance, but with different placements of world-produced return relations. These differences survived deletion of the original world, body-only restart, common washout, and a second injury.

After that injury, line A restored the higher-order relation on the A opportunity and line B on the B opportunity. Reversing probe order changed the episode number but not the line-specific response. Within-line signatures were identical across seeds; A/B signatures remained separated.

The result was tested over two generations with seven paired controls per line and seed, for 112 comparisons. Controls removed the world, made contact passive, disconnected world change from bodily action, mismatched the continuation phase, delayed return under the same finite collision budget, redirected the return to the other prepared route, or replaced action-dependent world formation with a pre-conducting phase-incompatible route. All 112 controls separated from the matched condition both in the resulting `BODY` bytes and in behavior after a further common washout and injury.

Two hostile interventions localize the memory claim:

- a complete relabeling of storage addresses, while preserving relations, preserved both body organization and future behavior;
- shuffling only the placement of the history-bearing return relations erased the A/B future difference while preserving the amount of material and the rest of the relational structure.

Together these interventions define **Relational Distinguishability** in this
carrier: changing storage labels preserves the A/B distinction, while changing
the distribution of the candidate return-relation class removes it. That
distribution is interventionally necessary for the observed A/B difference;
the result does not localize memory to a small site.

A separate scale intervention removed only the higher-order conducting relation. The large-scale act disappeared while the lower route remained. A new pass through that surviving route restored the higher-order relation.

The bounded result is therefore:

> In this prepared carrier, two histories of world contact are retained as different relational placements in the body; they remain distinguishable in later repair after world deletion, restart, common washout, and renewed injury, and the distribution of the tested return-relation class is interventionally necessary for that distinction.

The current source passes 21 tests; the public evidence bundle records four seeds and 112 paired controls.

### Limits and the question I am asking

The topology is engineered. The experimenter specifies the available contacts, the higher-order closure affordance, the two return routes, the injury, and the readout. The carrier does not originate its own boundary, discover an open-ended morphology, maintain metabolism, or establish its own goals. It is digital, uses a small state vocabulary, and is not a model of ion channels, gap junctions, or biological tissue. It has not been independently replicated. I do **not** present it as evidence of basal cognition or as an explanation of morphogenesis.

Its intended value is narrower: it probes the boundary between **history-dependent self-organization** and **anatomical homeostasis**. The runtime contains no separate symbolic target register or model of a completed body. However, the history-bearing relational placement is readable through future repair and rewritable by intervention, while the prepared higher-order slot and return routes encode a closure affordance. Together, these may already constitute a rudimentary distributed pattern memory or homeostatic target rather than its absence.

My main question is:

> Would you regard the topology-encoded closure affordance and history-bearing relational state as a minimal distributed pattern memory or homeostatic target, or only as a path-dependent attractor? What single perturbation would best distinguish those interpretations?

### References

1. Levin M. [Technological Approach to Mind Everywhere: An Experimentally-Grounded Framework for Understanding Diverse Bodies and Minds](https://doi.org/10.3389/fnsys.2022.768201). *Frontiers in Systems Neuroscience*. 2022.
2. Durant F, Morokuma J, Fields C, Williams K, Adams DS, Levin M. [Long-Term, Stochastic Editing of Regenerative Anatomy via Targeting Endogenous Bioelectric Gradients](https://pubmed.ncbi.nlm.nih.gov/28538159/). *Biophysical Journal*. 2017.
3. Manicka S, Levin M. [Modeling somatic computation with non-neural bioelectric networks](https://doi.org/10.1038/s41598-019-54859-8). *Scientific Reports*. 2019.
4. Levin M. [Bioelectric networks: the cognitive glue enabling evolutionary scaling from physiology to mind](https://doi.org/10.1007/s10071-023-01780-3). *Animal Cognition*. 2023.
