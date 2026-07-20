# Can Repair Arise from Changed Relational Organization Rather Than an Explicit Stored Target?

## A minimal non-neural carrier experiment

**Amir Tlinov — Independent Researcher**<br>
**20 July 2026**<br>
**Materials:** [github.com/AmirTlinov/relational-closure-carrier](https://github.com/AmirTlinov/relational-closure-carrier)

### Claim and biological question

The starting physical claim is that differences precede distinguishability:
differences exist before a contact in which they can become distinguishable.
Absence of distinguishability in that contact is therefore not absence of
differences. Operationally, retained histories A and B become physically
distinguishable when substituting one for the other changes an admissible later
contact. `D+` measures the strongest such future difference over the declared
continuation domain.

The material claim is:

> **Distinguishability becomes memory when contact changes the same substrate
> that later conducts a changed continuation.**

A whole is then a temporarily stable balance of mutually sustaining
differences. When later contact meets that closure as one operative unit, it is
distinguishable as one whole at its scale and a new difference at the next.
Injury opens a deficit in the balance; reclosure can restore the prior form, stabilize
another, divide into new wholes, or collapse.

Work on anatomical homeostasis and basal cognition makes this a direct
biological question [1–4]:

> Can target-like repair arise from history retained in the same substrate
> that later conducts repair, without a separate complete-body target model,
> global controller, reward signal, or online external selection?

### Exact small case: bubble sort

Zhang, Goldstein, and Levin use distributed sorting algorithms as minimal
models of morphogenesis [5]. Bubble sort isolates the scale transition. If

\[
I(a)=\#\{(i,j):i<j,\ a_i>a_j\}
\]

is the inversion count, every swap of an adjacent inverted pair lowers \(I\) by
exactly one; \(I=0\) is the sorted fixed condition. No element stores the final
permutation, yet local completion produces global order. The cell-view variants
add damage tolerance and unexpected algotype clustering. The carrier experiment
continues from the exact assumption sorting leaves outside itself: can retained
substrate history change a later contact? Carrier-owned formation of the
contacts themselves is the next material test.

### Minimal carrier

The prepared arena is a deterministic, non-neural computational dynamical system over explicit relations. The harness-designated persistent surface contains 1,024 writable relational sites and is called `BODY` for protocol provenance. Each site stores a small local state and explicit handles to available contacts and conducting relations. One finite local collision rule is used throughout. It has no global sweep, coordinate arithmetic, fitness function, symbolic planner, runtime comparison with a completed form, or channel carrying reward.

The same rule can:

1. conduct change through an existing relation;
2. occupy material available through the current relations;
3. retract a route that fails to close;
4. form a higher-order conducting relation only after a lower route physically returns to its origin.

The external harness prepares the arena, partitions storage, and reads the result, but it does not select a relation during execution. The local law has no predicate for that witness partition.

The temporary five-record surface labeled `WORLD` is another file-backed region of the same `MaterialRecord` physics. One ongoing continuation follows explicit handles across both witness partitions. A return is counted as earned only if that continuation first changes the particular surrounding record from which the return later emerges:

```text
ongoing continuation → changed surrounding record → earned return → closure
```

Passive contact, a disconnected surrounding change, or a prewritten return state therefore cannot substitute for this material provenance sequence.

### Witness boundary and surface flattening

`BODY` and `WORLD` are harness/witness labels for two mmap storage surfaces
governed by the same `MaterialRecord` format and local collision physics. This
partition belongs to the experimental architecture: the surface router uses its
namespace to choose a file, while the frozen `collision` law contains no
BODY/WORLD predicate and follows only explicit handles.

A dedicated control asked whether that routing namespace is required for the
local dynamics of one prepared matched passage. The witness copied all 1,024
former BODY records and five former WORLD records into one direct 1,029-record
`MmapBody`, removed the surface namespace from every non-sentinel handle, and
applied a deterministic hostile fixed-point-free permutation to all nodes. The
ordinary two-surface run and the flat run were then compared through the same
frozen collision kernel.

All `2,058 / 2,058` collision events were isomorphic in full—kind, current
place, met place, continuation, and changed-place tuple—and all `1,029 / 1,029`
final `MaterialRecord` values were isomorphic. Thus the BODY/WORLD namespace is
not dynamically necessary for this matched trajectory. The witness still
constructs the mapping and remembers the former labels.

### History-dependent repair assay

Two lines, A and B, begin from the same injured 513-site `BODY`-labeled snapshot. Their `WORLD` fixtures have equal resources and differ only in the physical placement of the earned return into one of two prepared routes in that persistent group. Both lines recover the full 1,024-site group and the same higher-order conducting capacity.

The harness then deletes the temporary `WORLD` files. Only each persistent `BODY`-labeled snapshot survives. Every snapshot is reopened in a fresh process, exposed to the same common washout, and cut again at the same current relation. Future repair is probed with fresh A and B fixtures in both orders (`AB` and `BA`).

The question is not whether a log can classify the histories. It is whether the surviving placement of relations within the persistent group is necessary for different future conduct.

### Result

Across seeds 17, 23, 41, and 59, histories A and B produced persistent groups with the same material extent and the same immediately available large-scale conductance, but with different placements of return relations earned during passage through records labeled `WORLD`. These differences survived deletion of the original temporary file, restart of the persistent snapshot, common washout, and a second injury.

After that injury, line A restored the higher-order relation on the A opportunity and line B on the B opportunity. Reversing probe order changed the episode number but not the line-specific response. Within-line signatures were identical across seeds; A/B signatures remained separated.

The result was tested over two generations with seven paired controls per line and seed, for 112 comparisons. Controls removed the `WORLD` fixture, made contact passive, disconnected change of the surrounding record from the ongoing continuation, mismatched the continuation phase, delayed return under the same finite collision budget, redirected the return to the other prepared route, or replaced continuation-dependent formation in `WORLD`-labeled records with a pre-conducting phase-incompatible route. All 112 controls separated from the matched condition both in the resulting `BODY` bytes and in behavior after a further common washout and injury.

Two hostile interventions localize the memory claim:

- a complete relabeling of storage addresses, while preserving relations, preserved both `BODY`-labeled relational organization and future behavior;
- shuffling only the placement of the history-bearing return relations erased the A/B future difference while preserving the amount of material and the rest of the relational structure.

Together these interventions define **Relational Distinguishability** in this
carrier: changing storage labels preserves the A/B distinction, while changing
the distribution of the candidate return-relation class removes it. That
distribution is interventionally necessary for the observed A/B difference;
the result does not localize memory to a small site.

A separate scale intervention removed only the higher-order conducting relation. The large-scale act disappeared while the lower route remained. A new pass through that surviving route restored the higher-order relation.

The bounded result is therefore:

> In this prepared carrier, two histories of contact across witness-labeled partitions are retained as different relational placements within the persistent group; they remain distinguishable in later repair after temporary-file deletion, restart, common washout, and renewed injury, and the distribution of the tested return-relation class is interventionally necessary for that distinction.

The current source passes 22 tests; the public evidence bundle records four seeds, 112 paired controls, and the single-mmap isomorphism receipt. World-lineage executable source SHA-256: `d3ed7438372973ef17b61b01659569372bb8c9faf61c48b334ded6bedca962e8`.

### Limits and the question I am asking

The topology and witness partition are engineered. The experimenter specifies the available contacts, the higher-order closure affordance, the two return routes, the injury, and the readout. No organism/environment or BODY/WORLD predicate is available to the local law. Calling the held `BODY`-labeled relational group an organism is a proposed interpretation: in this assay it remains a witness-selected group among other records of the same physics, not a demonstrated self-born boundary. The carrier does not discover an open-ended morphology, maintain metabolism, or establish its own goals. It is digital, uses a small state vocabulary, and is not a model of ion channels, gap junctions, or biological tissue. It has not been independently replicated. I do **not** present it as evidence of basal cognition or as an explanation of morphogenesis.

The flattening result is deliberately narrower than the serial assay. It covers
one prepared matched passage only; deletion of the temporary `WORLD` file,
restart of the persistent `BODY`-labeled snapshot, common washout, G2, and the
paired control family have not been reproduced in the flat field. It therefore
does not show a self-born boundary or establish that every use of the
BODY/WORLD witness partition can be eliminated from the full protocol.

Its intended value is narrower: it probes the boundary between **history-dependent self-organization** and **anatomical homeostasis**. The runtime contains no separate symbolic target register or model of a completed body. However, the history-bearing relational placement is readable through future repair and rewritable by intervention, while the prepared higher-order slot and return routes encode a closure affordance. Together, these may already constitute a rudimentary distributed pattern memory or homeostatic target rather than its absence.

My main question is:

> Given two tissues matched in present anatomy and immediate behavior but
> differing only in causal repair history, what perturbation would best
> distinguish a distributed homeostatic target from ordinary path-dependent
> hysteresis—without supplying the desired anatomy from outside?

### References

1. Levin M. [Technological Approach to Mind Everywhere: An Experimentally-Grounded Framework for Understanding Diverse Bodies and Minds](https://doi.org/10.3389/fnsys.2022.768201). *Frontiers in Systems Neuroscience*. 2022.
2. Durant F, Morokuma J, Fields C, Williams K, Adams DS, Levin M. [Long-Term, Stochastic Editing of Regenerative Anatomy via Targeting Endogenous Bioelectric Gradients](https://pubmed.ncbi.nlm.nih.gov/28538159/). *Biophysical Journal*. 2017.
3. Manicka S, Levin M. [Modeling somatic computation with non-neural bioelectric networks](https://doi.org/10.1038/s41598-019-54859-8). *Scientific Reports*. 2019.
4. Levin M. [Bioelectric networks: the cognitive glue enabling evolutionary scaling from physiology to mind](https://doi.org/10.1007/s10071-023-01780-3). *Animal Cognition*. 2023.
5. Zhang T, Goldstein A, Levin M. [Classical sorting algorithms as a model of morphogenesis: Self-sorting arrays reveal unexpected competencies in a minimal model of basal intelligence](https://doi.org/10.1177/10597123241269740). *Adaptive Behavior*. 2025;33(1):25–54.
