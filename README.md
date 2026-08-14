# The Recognition Kernel

**typology = kernel × chain**

A reference implementation of a domain-neutral kernel of twelve contradiction primitives in four strata, indexed over the seven links of a recognition chain. Give it a domain's chain and it returns the full typology, the gated profile, and the predicted failure modes — for domains nobody has examined as readily as for domains that have been studied for a century.

Implements Koepsell, D. R., *The Recognition Layer: A Generative Typology of Structural Contradiction for Recognition-Constituted Domains* (working draft), §§5–8.

```bash
pip install -e ".[dev]"
make            # build the OWL module, validate, test, regenerate out/
```

```bash
rkernel typology examples/frcp/frcp.chain.json
rkernel compare  examples/frcp/frcp.chain.json examples/cfr205/cfr205.chain.json \
                 examples/icd11/icd11.chain.json examples/go/go.chain.json
rkernel extract  examples/frcp/corpus/frcp_demo.json
rkernel detect   examples/frcp/corpus/frcp_demo.json
rkernel validate
```

---

## What it does

Give it seven link statuses. It computes the system's kind, its chain thickness, which of the 96 crossings are well-formed, which can fire and at what rate, and which have a detector in this release.

```
| System            | Computed kind        | Chain thickness           |  A  |  B  |  C  |      D      |
| ----------------- | -------------------- | ------------------------- | --- | --- | --- | ----------- |
| FRCP              | legal order          | act-thick, repair-internal |fires|fires|fires| fires       |
| 7 CFR 205         | certification scheme | act-thin, repair-internal  |fires|fires|fires| rare        |
| ICD-11            | classification       | act-thin, repair-external  |fires|fires|fires| rare        |
| Gene Ontology     | reference ontology   | act-empty, repair-absent   |fires|fires|fires| cannot fire |
```

Only the D column varies, and it varies with chain thickness alone. **No substantive rule of any of these systems is consulted.**

Two things follow that a list of known defects could not deliver. A system's failure profile is readable from its shape before its content is examined. And an empty pragmatic stratum is not a clean bill of health — it is a report about what kind of thing you are looking at.

---

## The three deliverables

### 1. The kernel as a formal specification — `spec/`

| | |
| --- | --- |
| [`SPEC.md`](spec/SPEC.md) | Normative prose specification, with conformance conditions |
| [`PRIMITIVES.md`](spec/PRIMITIVES.md) | Two worked examples and a near miss for each of the twelve primitives |
| [`schema/`](spec/schema/) | JSON Schema for the kernel, chains, generated typologies, and findings |
| [`owl/recognition-kernel.ttl`](spec/owl/) | OWL 2 DL module, BFO-aligned |
| [`data/kernel.json`](data/kernel.json) | The single source of truth |

The OWL module is **generated** from `kernel.json`, so the ontology and the generator cannot drift apart. It does more than supply vocabulary: **the gating rule is enforced as an unsatisfiability axiom.** Asserting a Stratum D crossing at a link the system does not have makes the ontology inconsistent, and `rkernel validate` verifies that under HermiT:

```
- reasoning: pass
    - example-abox: consistent
    - gating-violation: inconsistent
```

That check is the load-bearing one. It verifies that the rule is *enforced* rather than merely documented.

### 2. The chain extractor — `src/rkernel/extract/`

Rule-based, **no required dependencies**, optional spaCy path for bearer identification.

- `norms.py` — norm tuples: bearer, modality, action, conditions, deadline, counterparty. Modality in {duty, prohibition, permission, power}. Power tuples are the capacities the K-D3 detector consumes.
- `ontological.py` — the entity-relation extractor, kept as a **control** rather than for its yield.
- `chain_extract.py` — drafts a chain from cue density. A draft, never a committed chain.
- `kd3.py` — the K-D3 detector.
- `lexicon.py` — vocabularies, with disjointness asserted at import time.

### 3. The typology generator — `src/rkernel/typology.py`

The periodic-table generator. Takes a chain plus the kernel; returns the full typology, the gated profile, per-locus firing values, and ranked predicted failure modes with named types located where the coordinates match.

Given the ICD-11 chain it regenerates **CT-1 through CT-7** at their coordinates. Given the FRCP chain it regenerates the five located types of the Structural Ontology of Law. Neither list is looked up — the cells are derived and then named.

---

## Four worked examples

| Cell | Example | Chain | Predicted D |
| --- | --- | --- | --- |
| Reference ontology | [Gene Ontology](examples/go/NOTES.md) | act-empty | cannot fire |
| Classification | [ICD-11](examples/icd11/NOTES.md) | act-thin, repair-external | rare |
| Certification scheme | [7 CFR 205](examples/cfr205/NOTES.md) | act-thin, repair-internal | rare |
| Legal system | [FRCP](examples/frcp/NOTES.md) | act-thick, repair-internal | fires |

`out/` holds a generated report for each. `make demo` regenerates them.

The first three answer the brief: act-thick, act-thin, act-empty, and the contrast between them. **The fourth is where the framework is exposed.** It is the only cell whose result could distinguish the three-valued gate from a two-valued one, and it has not been run.

The instrument does contribute something to that measurement. Classification and certification share a Stratum D summary of `rare`, exactly as the published profile table has them — but they differ at three loci, most sharply at remedy, where one fires and the other is rare. Comparing at the summary level asks whether two rates differ. Comparing per locus asks *where*, which needs far fewer corpora to answer.

---

## What this release does not establish

Stated here rather than in a footnote, because an instrument that oversells itself is worse than no instrument.

- **One primitive in twelve has a working detector.** K-D3. K-D2 is partial and low-recall by construction. K-D1 is not operationalised and will not be: detection needs world-facing ground truth about whether asserted conditions obtained. The other nine await structural detectors or delegation to a reasoner. Every output marks which cells are detectable, and **nothing here emits an aggregate score over the kernel.**
- **No Stratum D rate exists.** The demo corpora are fixtures sized to exercise the instrument. A rate from twenty-eight abridged provisions is a number about the fixture.
- **A prior null is withdrawn**, not quietly omitted. An earlier empty Stratum D over ICD-11 came from a layer that operationalised four primitives, none of them D. An empty D is what one observes if the gating rule holds *and* what one observes if the tooling does not exist; that run does not distinguish them.
- **Chain extraction has no established reliability.** Two annotators, independent extraction, per-link agreement reported, is a precondition for the empirical design and has not been run. Every chain here is a single unreviewed assignment. Expect disagreement to concentrate at assessor-in-role and remedy.
- **The corrected matcher is expected to *increase* the candidate count**, since it withdraws pathways awarded on vocabulary alone. Recorded in advance so it cannot be adjusted afterwards.

---

## Two discrepancies found while encoding

Encoding the locus mask cell by cell surfaced two internal tensions in the source. Both are recorded in `data/kernel.json` and pinned by tests rather than silently resolved.

**The grid total.** The mask yields **70 of 84** well-formed crossings over the seven chain loci, following Table 7 cell by cell; the prose at §7.2 says sixty-nine. Per-primitive: A1 7, A2 6, A3 7, B1 6, B2 7, B3 4, C1 7, C2 7, C3 6, D1 4, D2 3, D3 6. The generator computes the total rather than storing it.

**Table 7 against Table 9.** Table 9 places Fuller's possibility-of-compliance at K-D2 with an arrow to Effects, while Table 7 marks K-D2 as not well-formed at Effects. This implementation reads the arrow as a *manifestation pointer* — where the failure shows up, not a second crossing — on which reading the tables agree. The alternative is to make K-D2 well-formed at Effects, which would take the grid to 71. An open question for the author.

---

## Reporting discipline, enforced in the tooling

The specification makes these normative and the code holds to them.

1. **Provenance defaults to `undetermined`.** No detector emits `source`. The largest single source of artifactual incoherence in extraction pipelines has been a category misuse of BFO `bearer-of`, which presents exactly like a defect of source. The tooling cannot enforce that distinction; the analyst must.
2. **Fan-out is reported unconditionally.** A rate produced by a matcher whose fan-out is unreported cannot be interpreted, and the report carries an interpretation string that refuses a rate when the distribution says so.
3. **Two conditions over disjoint vocabularies.** `lexicon.assert_disjoint()` raises at import time. Where one similarity test does both jobs, every procedural provision resembles every capacity and the detector measures the density of procedural language rather than the presence of pathways.
4. **External capacities are set aside**, and both rates are reported side by side.
5. **Not detected is not zero.** Cells for unoperationalised primitives are flagged, never zeroed.

---

## Layout

```
spec/          specification, schemas, OWL module
data/          kernel.json — the single source of truth
src/rkernel/   kernel, chain, typology, render, validate, cli, extract/
examples/      four cells, each with a chain, notes, and where licensing permits a corpus
tools/         build_owl.py (regenerates the OWL), fetch_frcp.py (builds a real corpus)
tests/         61 tests; the interesting ones check the construction against material it did not generate
out/           generated reports
```

## Licence

Code Apache-2.0; specification and documentation CC BY 4.0. Third-party material in `examples/` is itemised in [`LICENSE`](LICENSE). **No ICD-11 text is reproduced anywhere in this repository.**
