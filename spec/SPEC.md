# The Recognition Kernel: Specification

**Version 0.2.0.** Normative. Where this document and `data/kernel.json` disagree, the JSON governs; where the JSON and the OWL module disagree, that is a bug, and `rkernel validate` will report it.

This specification defines a domain-neutral kernel of contradiction primitives, a seven-link recognition chain, and a product construction over the two. Its purpose is to make one claim runnable: that a domain's contradiction typology is *derived* from its chain rather than compiled from observation, and that a system's failure profile is readable from its shape before its substantive rules are examined.

Source: Koepsell, D. R., *The Recognition Layer: A Generative Typology of Structural Contradiction for Recognition-Constituted Domains* (working draft), §§5–8.

The key words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are to be interpreted as in RFC 2119.

---

## 1. The recognition chain

A **recognition chain** is a sequence of seven links:

| Link | Identifier | What occupies it |
| --- | --- | --- |
| Source of authority | `authority` | the source entitled to fix the criteria |
| Criteria | `criteria` | the substantive standard |
| Assessor in role | `assessor` | the agent licensed by the authority to apply the criteria |
| Presenting facts | `facts` | the state of affairs to which the criteria are applied |
| Recognition act | `act` | the act in which criteria are applied to facts and a status is conferred |
| Effects | `effects` | what follows from the conferral |
| Remedy | `remedy` | the pathway, where one exists, by which a conferral is revisited |

The chain is not the contribution. It is recognisably the shape of a status function declaration, of Hohfeldian power and liability positions, of capacitative norms, and of institutionalised power. Its use here is as an **index set**: the positions over which a typology of structural failure is generated.

### 1.1 Link status

Each link carries exactly one **status**, and this is the only chain content the gating rule consumes.

| Status | Condition |
| --- | --- |
| `internal` | The system specifies the link **and** it is carried out under the system's own authority. |
| `external` | The link occurs but is neither specified nor governed by the system. |
| `absent` | The system has no such link at all. |

The conjunction in `internal` is load-bearing and is the commonest place an assignment goes wrong. A diagnostic manual specifies its criteria in full, yet those criteria are applied by clinicians it does not license. Its `criteria` link is therefore **external**, not internal: specification without performance under own authority does not satisfy the definition. Recording it as internal reports Stratum D as firing at that locus, which is the reading the gating rule exists to rule out.

Because specification-thickness is nonetheless a real and interesting property, a link MAY additionally carry a `specification` value drawn from the same three-valued set. It is documentation. **No rule in this specification consumes it.**

### 1.2 Chain thickness

Two derived properties, each read off a single link:

- **Act thickness** from `act`: `act-thick` (internal), `act-thin` (external), `act-empty` (absent).
- **Repair thickness** from `remedy`: `repair-internal`, `repair-external`, `repair-absent`.

The source text uses *repair-thick* for the legal case and *repair-internal* for the certification case. These name the same status; this specification uses `repair-internal` throughout.

Chain thickness is not a degree of formality. It is a structural fact about which links a system specifies and performs for itself, and it is readable from the system's own governing documents.

### 1.3 Computed system kind

A system's kind is computed from link statuses alone, consulting no substantive rule:

| Condition | Kind |
| --- | --- |
| no link present | `reference_ontology` |
| `act` internal and `remedy` internal | `legal_order` |
| `act` external and `remedy` internal | `certification_scheme` |
| `act` external and `remedy` external or absent | `classification` |
| `act` absent, some other link present | `reference_ontology` |
| otherwise | `other` |

A chain file MAY declare a kind. Where the declared and computed kinds disagree, an implementation MUST report the mismatch and MUST NOT silently reconcile it. Disagreement is a finding about the assignment, the corpus, or the classification scheme, and which of the three it is cannot be settled by the tool.

### 1.4 The artifact pseudo-locus

Implementations MUST provide an eighth locus, `artifact`, standing for the definitional and assertional content of the artifact considered apart from any chain link.

This is an addition to the source text, made for a reason the source text requires. A reference ontology performs no link, yet Strata A, B and C must still be able to fire in it — a gene ontology can be as inconsistent as a legal code. Without a locus present unconditionally, the ungated strata would have nothing to be indexed to in an act-empty system and the constancy of the A, B and C columns could not be exhibited.

The pseudo-locus MUST be treated as having status `absent` for gated strata and `internal` for ungated strata. No Stratum D primitive is well-formed there.

---

## 2. The kernel

Twelve primitives in four strata. The strata are indexed **by the kind of structure each failure presupposes in order to be possible at all** — not by aspect of quality, which is how the existing defect catalogues are organised. This index is what yields cumulativity, and cumulativity is what makes the gating rule available.

| Stratum | Precondition | Gated | Primitives |
| --- | --- | --- | --- |
| A — model-theoretic | a formal theory | no | K-A1 Inconsistency, K-A2 Term Incoherence, K-A3 Indeterminacy |
| B — definitional | a system of definitions | no | K-B1 Circularity, K-B2 Equivocation, K-B3 Residual Definition |
| C — meta-ontological | an upper ontology | no | K-C1 Category Violation, K-C2 Level Confusion, K-C3 Dependence Violation |
| D — pragmatic | acts | **yes** | K-D1 Falsification, K-D2 Performative Self-Defeat, K-D3 Modal Clash |

The strata are cumulative: whatever can suffer a Stratum D failure can also suffer A through C, and not the reverse.

Definitions, formal signatures, precedents, and detection instruments for each primitive are in `data/kernel.json` and are exhibited with worked examples in [`PRIMITIVES.md`](PRIMITIVES.md).

The kernel is **upper-ontology-neutral**. Only Stratum C requires an upper ontology, and it requires only that the upper ontology assert disjointness among top-level categories, which BFO, UFO and DOLCE all do. BFO appears in the OWL module because the reference corpora are biomedical and legal.

### 2.1 The detectability partition

| Instrument | Detects |
| --- | --- |
| Description-logic reasoner | K-A1, K-A2, K-C1 (given upper-level disjointness); K-B1 for cyclic subsumption only; K-C3 partially |
| Structural analysis of axioms | K-A3, K-B2, K-B3, K-C2; K-B1 for grounding cycles and temporal inversions |
| World-facing data | K-D1 |
| Process modelling or text-internal structural analysis | K-D2, K-D3 |

**A reasoner is necessary and never sufficient.** Half the kernel is invisible to description logic in principle. An implementation reporting only reasoner output has reported Stratum A plus part of C and silently scored the rest as zero. Implementations MUST therefore report stratum-resolved results and MUST NOT emit an aggregate score over the kernel.

### 2.2 Operationalisation status

Each primitive carries an `operationalized` flag. In version 0.2.0:

- **K-D3** — operationalised. See `rkernel.extract.kd3`.
- **K-D2** — partial. Text-internal case only; low recall by construction.
- **K-D1** — not operationalised, and will not be. Detection requires world-facing ground truth about whether asserted triggering conditions obtained.
- **All others** — not operationalised in this release. Stratum A and part of C are delegable to an existing reasoner; Strata B and C otherwise await structural detectors.

Absence of a flag from a primitive that is not operationalised MUST NOT be reported as absence of the failure. The distinction between *not detected* and *not implemented* MUST be carried through to every table.

---

## 3. Well-formedness: the locus mask

A crossing (primitive, locus) is **well-formed** when the locus supplies the structure the primitive presupposes. Each primitive carries a `well_formed_at` list and an `excluded_at` list, which MUST together partition the loci.

The governing principle, applied cell by cell: falsification needs something asserted about the world, so it is well-formed at presenting facts, at the act, at effects and at remedy, and nowhere else. Residual definition needs a term fixed by complement, so it is well-formed wherever a positive differentia is owed. Modal clash needs a capacity, so it is well-formed at every locus that confers or exercises one, and not at presenting facts, which confer nothing.

Over the seven chain loci this yields **70 of 84** crossings well-formed.

> **Discrepancy with the source text.** The paper's §7.2 states sixty-nine of eighty-four while its Table 7 marks seventy. This implementation follows the table and computes the total rather than storing it, so whichever way the discrepancy is resolved the artifacts follow. Per-primitive counts over the chain loci: A1 7, A2 6, A3 7, B1 6, B2 7, B3 4, C1 7, C2 7, C3 6, D1 4, D2 3, D3 6.

Implementations MUST make the locus mask machine-checkable. The OWL module does this by asserting that a contradiction of a given class, part of a specification of a given kind, is unsatisfiable.

---

## 4. The product construction

> **typology = kernel × chain**

The typology of a domain is the kernel instantiated over the loci of that domain's chain. Domain typologies are therefore **theorems of this product rather than lists compiled from observation**, and the typology of a domain nobody has examined follows mechanically.

Given a chain, an implementation MUST produce, for every (primitive, locus) pair: whether the crossing is well-formed, the status of the link, the firing value, and whether a detector exists for it in the release.

### 4.1 Admission of named types

A candidate contradiction type is admitted to a domain typology only if it is:

1. **locus-indexed** — stated at a determinate (primitive, locus) coordinate;
2. **distinguishable** — model-theoretically distinguishable from every existing type in both directions;
3. **non-derivable** — not derivable from existing types, except where a compound carries emergent diagnostic value;
4. **attested** — attested in corpus data.

Derivability without attestation licenses failures nobody commits. Attestation without derivability yields a list that cannot be closed or principledly extended. Both conditions are required.

`data/kernel.json` registers the five located types of the Structural Ontology of Law, the seven classificatory types, and Fuller's eight desiderata at their coordinates. The generator uses the first two to *name* cells it derives; the third is a fixture, and the test suite checks that every Fuller coordinate lands on a well-formed crossing of the legal grid. That is a check on the kernel, using an independent eight-item list arrived at by a theorist with no knowledge of this construction.

---

## 5. The gating rule

**Strata A, B and C are ungated.** Their preconditions are rules, definitions and top-level kinds, all of which live inside the artifact. The chain does not gate them.

**Stratum D is gated three ways**, per link:

| Link status | Stratum D at that locus |
| --- | --- |
| `internal` — the system performs the link itself | **fires** |
| `external` — the link happens outside the system | **fires only rarely** |
| `absent` — the system has no such link | **cannot fire** |

That is the whole rule.

### 5.1 Firing values

| Value | Meaning |
| --- | --- |
| `fires` | The failure can occur at this coordinate. |
| `rare` | The failure can occur but at a low rate. Reserved for gated primitives at external links. |
| `cannot_fire` | The failure is impossible at this coordinate given the chain. |
| `no_locus` | The crossing is well-formed, but this system has no link at that locus. |
| `not_applicable` | The crossing is not well-formed; there is no such coordinate. |

`cannot_fire`, `no_locus` and `not_applicable` MUST be distinguished. They are three different reasons a cell does not fire, and they sit at three different levels.

`not_applicable` is a **kernel-level** fact. The crossing fails the locus mask, so the coordinate does not exist in any system whatsoever. Stratum D at the artifact body is `not_applicable` for every chain ever analysed, because no D primitive is well-formed there.

`no_locus` is a **system-level** fact. The coordinate exists and the primitive could sit at it, but this particular system has no such link. An ontology with no source of authority yields `no_locus` for K-A1 at `authority`: inconsistency is perfectly capable of sitting at an authority link, and this system has no authority link for it to sit at.

`cannot_fire` says the link exists and the primitive is barred at it.

Collapsing `no_locus` into `not_applicable` is the error this distinction exists to prevent. A reader scanning a stratum-A-by-locus table in which every chain locus reads `not_applicable` will conclude that the kernel says nothing about that system at those loci. The actual content is that the system has no chain. The failure has not been ruled out; it has **relocated to the artifact body**, where it reads `fires`.

`no_locus` is reserved for ungated strata. Gated strata retain `cannot_fire` at absent links, and the asymmetry is not a fudge: it tracks a difference in consequence. For A, B and C an absent link relocates the failure to the artifact pseudo-locus, which is present in every system. For D there is nowhere for it to relocate to, since no D primitive is well-formed at the artifact body. The failure is genuinely barred rather than displaced.

A firing value is a claim about **possibility, not incidence**. A cell marked `fires` asserts that the failure can occur, not that it has.

### 5.2 Why the middle value is not a hedge

A binary rule would say: internal acts admit pragmatic failure, everything else does not. That is cleaner and false. A system whose act is external does not perform the act, but it specifies what the act is for, and can therefore specify a capacity whose exercise the surrounding institution cannot deliver — a modal clash whose *de jure* half is inside the document and whose *de facto* half is outside it.

Such cases should be rare, because the artifact is describing a promise made elsewhere rather than making it. But rare is not never, and the difference between rare and never is **empirical rather than definitional**. Nothing in the definition of Stratum D fixes that rate. It could be zero, collapsing the rule to two values; it could be indistinguishable from the internal-act rate, in which case the gate does no work. Both outcomes are possible and are to be reported if found.

### 5.3 Profile summarisation

Per-locus values are primary. A stratum summary is a convenience and MUST be computed as follows:

- **Ungated strata**: the strongest firing value over the stratum's well-formed loci.
- **Gated strata**: the value **at the recognition act locus**.

Summarising Stratum D by a maximum instead would report `fires` for any system with one internal link anywhere, collapsing precisely the distinction the rule is about. Keying it to the act is what reproduces the four profiles of the source text.

The summary nonetheless discards information that matters. A classification and a certification scheme share a D summary of `rare`, because both are act-thin. They differ at `criteria`, `assessor` and `remedy`. Implementations MUST emit a per-locus profile alongside the summary, and any comparison of two systems SHOULD be made on the per-locus profile.

### 5.4 The four profiles

| System kind | Chain thickness | A | B | C | D |
| --- | --- | --- | --- | --- | --- |
| Reference ontology | no chain | fires | fires | fires | cannot fire |
| Classification | act-thin, repair-external | fires | fires | fires | rare |
| Certification scheme | act-thin, repair-internal | fires | fires | fires | rare |
| Legal order | act-thick, repair-internal | fires | fires | fires | fires |

The A, B and C columns are constant. This is not a weakness but a direct consequence of the rule: those strata are ungated, so every artifact can suffer them. What differs between kinds is not whether they can fail definitionally but whether they can fail pragmatically.

### 5.5 Two consequences

**Profiles are readable from shape.** To know which failures a system can suffer, one needs to know only which links it performs for itself — answerable from a redacted skeleton in which the domain and the substantive rules have been stripped out. `Chain.redacted_skeleton()` produces such a skeleton for the blind-prediction study.

**Emptiness is informative.** An empty pragmatic stratum is not a report that a system is well built. It is a report about what kind of thing it is: something that describes or classifies but does not decide. Reading an empty stratum as a clean audit is the natural error and the wrong one.

---

## 6. Findings and reporting discipline

A **finding** is a candidate contradiction returned by a detector. The following are normative.

1. **Status.** Every finding carries `candidate`, `confirmed`, `withdrawn` or `external`. A detector MUST emit `candidate` or `external` and MUST NOT emit `confirmed`.

2. **Provenance.** Every finding carries `undetermined`, `source` or `translation`, defaulting to `undetermined`. A detector MUST NOT emit `source`. The largest single source of artifactual incoherence in extraction pipelines has been a category misuse of the BFO `bearer-of` relation, in which a class correctly grounded as a disposition also acquires a *has disposition some …* restriction and is forced under two disjoint BFO categories. That is a defect of translation that presents exactly like a defect of source. **The tooling does not enforce this distinction; the analyst must.**

3. **External set-aside.** A capacity whose pathway lies in an instrument outside the corpus MUST be recorded as `external` and reported separately. A rate that collapses when external references are excluded is not a finding, and both rates MUST be reported side by side.

4. **Fan-out.** Any detector that matches one item against many MUST report the distribution of matches per item, unconditionally. A rate produced by a matcher whose fan-out is unreported cannot be interpreted.

5. **Not detected is not zero.** Where a primitive was not operationalised, its cells MUST be marked as such and MUST NOT be reported as zero.

---

## 7. Detector requirements: K-D3

The K-D3 detector targets a capacity conferred in the text with no procedural pathway specified for invoking it. Stage one extracts capacity-conferring provisions; stage two searches for an invocation pathway.

Stage two MUST satisfy **two independent conditions over disjoint vocabularies**. A provision counts as a pathway only if it is:

1. **about the same capacity** — established by explicit cross-reference, by position in the same rule, or by substantive content-word overlap; **and**
2. **supplying a procedural marker** — a filing or motion requirement, a named recipient, a deadline, a form specification, a hearing.

**The vocabulary establishing condition 2 MUST be excluded from condition 1.** Where a single similarity test does both jobs, every procedural provision resembles every capacity, and the detector measures the density of procedural language rather than the presence of pathways. The reference implementation enforces this at import time in `lexicon.assert_disjoint()`, which raises rather than warns.

This requirement was learned from a failure. A run over the Federal Rules with one test doing both jobs returned a median fan-out of twelve, a mean of twenty-one, a maximum of two hundred and nineteen, and one provision returned as the pathway for sixty-seven unrelated capacities. That inverts the interpretation of the zero-match cases: if a pathway is awarded on generic vocabulary, the absence of one is a lexical accident rather than a structural fact.

Correcting the matcher is expected to **increase** the candidate count, since the correction withdraws pathways that were awarded on vocabulary alone. That expectation is recorded here so it cannot be adjusted afterwards.

Implementations MUST also collapse byte-identical quotes across adjacent chunks. One norm counted twice under a mis-assigned locator is an extraction artifact, not two findings.

---

## 8. Conformance

An implementation conforms to this specification if:

1. It loads `data/kernel.json` and validates it against `spec/schema/kernel.schema.json`.
2. Its locus mask agrees with the kernel file, primitive for primitive.
3. Its firing values agree with §5 for all three link statuses and both gating classes.
4. Its stratum summaries follow §5.3, and it emits a per-locus profile.
5. It reports the counts and constraints of §6 in every output.
6. Any K-D3 detector it ships satisfies §7, including the disjointness requirement and unconditional fan-out reporting.

`rkernel validate` checks 1–6 for the reference implementation, and additionally verifies against a reasoner that a pragmatic contradiction in an act-empty artifact is *inconsistent*, that a contradiction at a locus the mask excludes is *inconsistent*, and that named types are *inferred* rather than looked up. The two negative checks are the load-bearing ones: they verify that the gating rule and the locus mask are enforced rather than merely documented, and they fail separately.

---

## 9. BFO conformance

The ontology is BFO 2020 conformant. Four decisions were required, and each is recorded in `data/kernel.json` under `bfo.decisions` with its rationale, because each could reasonably have gone another way and a later reader is owed the argument rather than the result.

**Universals are classes.** The twelve primitives are classes; their instances are particular contradictions in particular artifacts. Each carries an Aristotelian definition and a definition source.

**A contradiction is an information content entity**, a continuant part of the artifact bearing it. Not a quality, because two printings of one code carry the same contradiction, so the entity is generically dependent rather than inhering in a material bearer.

**Locus is mereological.** A contradiction at the criteria locus is one that is part of a criteria specification. Implementations MUST NOT introduce a locus-indexing relation or mint crossing individuals; `BFO_0000050` does the work.

**Absence is absence of a part.** An artifact either has a specification part of a given kind or it does not. Implementations MUST NOT represent an absent link by an individual carrying a status of `absent`, which posits an entity in order to deny that it exists.

**Conferred status is two-part**: a role inhering in the bearer, and a declaration about it. The single-part alternatives are each expressively inadequate. A role alone asserts that something inheres in the bearer; a generically dependent continuant alone gives no bearer for the assertion to be made or withheld about. Only the two-part model can represent a system that records and mandates a status while declining to assert that anything inheres in anyone, and that configuration is WHO's stated position on ICD-11 Chapter 26.

**Firing values are annotations, not axioms.** A rate is not something the world contains, and the middle value of the gate is an empirical claim that could turn out false without anything in the ontology being wrong.

### 9.1 Verifying the alignment

Conformance MUST be checked as a separate act from consistency. A mistyped OBO identifier parses, serialises and reasons perfectly well; OWL treats it as a fresh class nobody has said anything about, so an ontology can claim an alignment to terms BFO does not contain while every reasoner reports success.

An implementation MUST therefore verify that each external IRI is declared upstream as a class or property, and that its label upstream matches the label recorded locally. A label mismatch is as serious as a missing term: referring to the right IRI under the wrong description is how a module ends up wired backwards while passing every structural check.

Where the imports cannot be resolved, an implementation MAY fall back to bare declarations of the external terms in order to keep its own axioms checkable, and MUST report that it has done so. A consistency verdict reached without BFO's axioms present is a weaker claim than it appears, and reporting it as a pass on conformance would be false.
