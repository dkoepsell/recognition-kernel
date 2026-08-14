# The Twelve Primitives, With Examples

Companion to [`SPEC.md`](SPEC.md). Each primitive gets a definition, a formal signature, **two worked examples** — one from a reference ontology or a body of definitions, one from an institution — a **near miss** that shows what the primitive is not, the instrument that detects it, and its status in this release.

Two cautions before the list.

**The primitives are not new, and no claim is made that they are.** Aristotle for non-contradiction and equivocation, Ryle for the category mistake, Waismann and Hart for open texture, Schlobach and Cornet for the inconsistency/incoherence distinction, Guarino and Welty for the metaproperty constraints, Husserl for foundation, Hintikka, Apel and Habermas for performative contradiction, Pound for law in books against law in action, Fuller for an anticipation of a whole chain profile. The contribution is compositional. The novelty of a periodic table is not the discovery of its elements.

**Every example below is illustrative.** Some are constructed, some are drawn from published cases, and none is a finding about a named artifact. Where an example refers to a real system it describes a pattern that system's own documentation acknowledges, not a defect detected by this tooling.

---

## Stratum A — model-theoretic

*Precondition: a formal theory. Ungated.*

### K-A1 Inconsistency

The theory admits no model; locally, a sentence and its negation are both derivable. Variants: assertional, deontic, analytic.

**Signature.** `O ⊨ ⊥` globally; locally, jointly unsatisfiable assertions over one locus.

**Definitional example.** An ontology asserts that every `Enzyme` is a `Protein`, that `Ribozyme ⊑ Enzyme`, and that `Ribozyme ⊑ ¬Protein`. The theory has no model in which any ribozyme exists, and if any is asserted, no model at all.

**Institutional example.** Two provisions of the same code, each valid, each in force, requiring incompatible dispositions of the same matter: one directs that a filing be accepted, another that it be refused, on identical triggering conditions. The deontic variant. Where the incompatibility is between what two authorities may each validly decide about the same case, the located type is **Jurisdictional Contradiction** (K-A1 at `effects`).

**Near miss.** Two provisions that *conflict in application* but are ordered by a priority rule — *lex specialis*, a savings clause, an explicit override — are not inconsistent. The theory has a model; the priority rule picks it out. Inconsistency requires that no ordering is supplied.

**Instrument.** Description-logic reasoner. **Status.** Not operationalised here; delegate to HermiT or an equivalent.

---

### K-A2 Term Incoherence

The theory is satisfiable but some term is not: a class equivalent to the empty class.

**Signature.** `O` consistent, yet `O ⊨ C ⊑ ⊥`.

**Definitional example.** A class defined as a subclass of two disjoint upper-level categories. The ontology remains consistent as long as nothing is asserted to instantiate the class; the class itself can have no members. This is the commonest reasoner finding in large extracted ontologies, and in extraction pipelines it is usually a translation defect rather than a source defect.

**Institutional example.** A statutory category whose eligibility conditions cannot be jointly satisfied by anyone: a benefit requiring both continuous residence for the preceding five years and first entry within the preceding twelve months. The statute is coherent; the category is empty.

**Near miss.** A category that happens to have no members — an offence nobody has committed, a disease nobody currently has — is not incoherent. Incoherence is a matter of the definition's satisfiability, not of the world's supply.

**Instrument.** Description-logic reasoner. **Status.** Not operationalised here.

---

### K-A3 Indeterminacy

Underconstraint: unintended models admitted, or membership undecided where practice requires a decision.

**Signature.** Intended and admitted models diverge; borderline membership underivable.

**Definitional example.** A polythetic category: membership on any five of nine criteria, with no shared essence across the family. Two individuals can both satisfy the definition with no criterion in common. The located type in a diagnostic classification is **CT-3 Threshold / Polythetic Incoherence** (K-A3 at `criteria`).

**Institutional example.** A standard of *reasonableness* with no further specification, applied by an assessor who must decide. Open texture, in Waismann's and Hart's sense: the term functions, and its borderline is not resolvable from the text.

**Near miss.** Deliberate delegation of judgement is not by itself a defect. A standard *intended* to be applied case by case has an underconstrained extension by design. K-A3 is diagnostic where the artifact's own purpose requires a determinate answer it cannot give.

**Note on resolution.** Three of Fuller's eight desiderata — generality, clarity, and constancy through time — all collapse into K-A3. Fuller is finer-grained at this locus than the kernel is. That is a real limitation of the kernel, recorded rather than explained away.

**Instrument.** Structural analysis of axioms. **Status.** Not operationalised here.

---

## Stratum B — definitional

*Precondition: a system of definitions. Ungated.*

### K-B1 Circularity

Non-wellfounded definition or grounding: a term's conditions depend transitively on the term itself, or a grounding order is inverted. The temporal case is inversion projected into time.

**Signature.** A cycle in the definition dependency graph, or inversion of a required grounding order.

**Definitional example.** A diagnostic category defined by the presence of impairment, where impairment is defined by reference to the functioning the category is supposed to explain. The definition returns to itself. The located type is **CT-2 Criterion Circularity** (K-B1 at `criteria`).

**Institutional example, temporal inversion.** A rule applied to conduct completed before the rule existed: the criteria are grounded in a state of affairs that postdates what they govern. This is the located type **Temporal Contradiction** (K-B1 at `criteria`), and it is Fuller's non-retroactivity desideratum at its coordinate.

**Near miss.** Mutual dependence that is *acknowledged and non-vicious* — a pair of terms defined together, as buyer and seller are — is not K-B1. The primitive requires that the cycle be doing definitional work the definition cannot support, or that a required grounding order be inverted.

**Instrument.** Reasoner for cyclic subsumption only; structural analysis for grounding cycles and temporal inversions. **Status.** Not operationalised here.

---

### K-B2 Equivocation

One item playing incompatible roles: a term, condition, or occupant doing double duty under conflicting demands.

**Signature.** One element bound to two roles with conflicting satisfaction conditions.

**Definitional example.** A single criterion serving both as an inclusion condition for a category and as an exclusion condition for its sibling, where the two uses impose incompatible thresholds on the same evidence. The located type is **CT-4 Criterion Double-Duty** (K-B2 at `criteria`).

**Institutional example.** A body that both promulgates a standard and adjudicates disputes about compliance with it, where the two functions impose conflicting demands on the same office — the drafter's interest in the standard's reach against the adjudicator's duty of independence. At the authority locus this is the located type **Authority Inflation** (K-B2 at `authority`).

**Near miss.** A term that is simply *ambiguous* across two contexts, disambiguated by each context, is a drafting infelicity rather than K-B2. The primitive requires that one element be bound to both roles *at once*, with conditions that cannot be jointly met.

**Instrument.** Structural analysis of axioms. **Status.** Not operationalised here.

---

### K-B3 Residual Definition

A term defined only by complement: membership fixed negatively, as what remains once the positive categories are exhausted.

**Signature.** `C ≡ ¬D₁ ⊓ ¬D₂ ⊓ …` with no positive differentia.

**Definitional example.** The *other specified* and *unspecified* pattern in a diagnostic classification: a residual category whose content is whatever the positive categories did not capture. Systematic in classification, and the located type **CT-5 Residual Indeterminacy** (K-B3 at `criteria`).

**Institutional example.** A catch-all provision reaching conduct not otherwise enumerated. Notable for its **rarity in law**: the legality principle, *nullum crimen sine lege*, structurally suppresses residual offence categories.

**Why this example is worth its space.** Law evolved an immune response to a Stratum B primitive that classification never developed. Neither literature could state that asymmetry on its own; it is visible only from a construction ranging over both, and it is the clearest small demonstration that the product does comparative work a flat catalogue cannot.

**Near miss.** A default rule — *if none of the above applies, then X* — is not K-B3 when X has positive content. The primitive requires that membership be fixed by exhaustion alone.

**Instrument.** Structural analysis of axioms. **Status.** Not operationalised here.

---

## Stratum C — meta-ontological

*Precondition: an upper ontology. Ungated.*

### K-C1 Category Violation

An entity forced under disjoint upper-ontological categories: the formalised category mistake.

**Signature.** `a : C` and `a : D`, with `C` and `D` disjoint at the upper level.

**Definitional example.** A class typed as both a continuant and an occurrent. In a machine-extracted formalisation, an entity that is grounded as a disposition and simultaneously given a *has disposition some …* restriction, which forces it under two disjoint BFO categories at once. In one build this collapsed 379 classes to unsatisfiability — and **the fault lay entirely in the translation**, which is why every finding of this shape must be adjudicated before it is attributed to a source.

**Institutional example.** A conferred status modelled as a disposition borne by an organism when the classification's own authority declines to assert that any such disposition exists. The located type in a classification is **CT-7 Type Contradiction**, sitting at the artifact body rather than at a chain link, because the failure is at the upper level rather than at a locus of the chain.

**Near miss.** A merely *unusual* typing is not a violation. K-C1 requires that the two categories be asserted disjoint at the upper level. This is why the primitive is upper-ontology-neutral: it needs disjointness axioms, not BFO specifically.

**Instrument.** Description-logic reasoner, given upper-level disjointness. **Status.** Not operationalised here.

---

### K-C2 Level Confusion

Representational levels conflated: a universal treated as a particular, a class as an instance, use as mention.

**Signature.** One element occupying two levels whose disciplines conflict.

**Definitional example.** A class used as an instance of itself in a way the formalism does not support, or an annotation about a term treated as an assertion about the term's referent. Metadata drifting into the object language.

**Institutional example.** A rule about how rules are to be made, treated as a rule of the same rank as those it governs — so that the amendment procedure can be amended by ordinary procedure, and the level distinction the system relies on is not represented in it.

**Near miss.** Deliberate punning, permitted in OWL 2 DL and used routinely, is not K-C2. The primitive requires that the two levels impose *conflicting* disciplines on the same element.

**Instrument.** Structural analysis of axioms. **Status.** Not operationalised here.

---

### K-C3 Dependence Violation

A dependent entity posited without its bearer, or a grounding link severed, including where one direction of a mutual dependence is enforced and the other denied.

**Signature.** A specifically dependent continuant without a bearer.

**Definitional example.** A quality or role asserted with no entity that bears it. Husserlian foundation, unmet.

**Institutional example.** An assessor licensed to apply criteria by an authority that does not exist, has lapsed, or never held the power it purported to delegate — so the act of conferral has no ground. This is the located type **Conferral Failure** (K-C3 at `assessor`). At the criteria locus in a classification, the same primitive gives **CT-6 Recognition Failure**: the act cannot track the criteria because the grounding between them is severed.

**Near miss.** A bearer that is merely *unrecorded* is not a missing bearer. The primitive is about the structure, not about the completeness of a database.

**Instrument.** Reasoner partially, via domain, range and cardinality axioms; otherwise structural. **Status.** Not operationalised here.

---

## Stratum D — pragmatic

*Precondition: acts. **Gated.*** This is the stratum that separates institutional ontologies from scientific reference ontologies, and the one the ontology-evaluation literature does not address — for the good reason that its objects do not have it.

### K-D1 Falsification

Assertion and world mismatched: triggering conditions fabricated, suppressed, or misrepresented. The artifact is coherent; its contact with reality is corrupted.

**Signature.** An asserted triggering condition with no worldly truthmaker.

**Institutional example.** A certification granted on an inspection that did not occur, or a status conferred on facts asserted and untrue. The chain is intact and every link performed; what fails is the correspondence between the presenting facts and the world.

**Second example.** A return filed with fabricated figures that satisfies every formal requirement of the filing. The law of evidence exists, in these terms, as an institutionalised detection apparatus for exactly this primitive.

**Near miss.** An *error* in the presenting facts, made in good faith, is K-D1 in structure but the primitive says nothing about culpability. The kernel measures a structural property, not a mental state.

**Why it is well-formed only at facts, act, effects and remedy.** Falsification needs something asserted about the world. Authority, criteria and role are conferred rather than asserted, so there is nothing there for the world to fail to match.

**Instrument.** World-facing data. **Status. Not operationalised, and it will not be.** Detection requires ground truth about whether asserted conditions obtained, which for text corpora is unavailable. This is a permanent limitation of text-internal analysis, not a gap awaiting a better parser.

---

### K-D2 Performative Self-Defeat

An act whose success conditions are undermined by its own performance: a norm whose compliance conditions preclude compliance.

**Signature.** Satisfying the act's content entails failure of its success conditions.

**Institutional example.** A confidentiality order whose terms cannot be complied with without disclosing the matter the order protects. Complying defeats the order; the success condition is undermined by the performance.

**Second example.** Fuller's possibility-of-compliance desideratum: a rule requiring the impossible. The rule is validly enacted and cannot be obeyed, and its being obeyed is what its own validity presupposes.

**Near miss.** A rule that is merely *onerous*, or that is obeyed at great cost, is not self-defeating. The primitive requires that satisfying the content entail failure of the success conditions, not that satisfaction be difficult.

**Instrument.** Process modelling, or text-internal structural analysis. **Status. Partial.** Only the text-internal case is implemented, and it is low recall by construction: self-defeat that shows up only in performance is invisible to a reader of the text.

---

### K-D3 Modal Clash (*de jure* / *de facto*)

A capacity present in structure but blocked in practice: possible according to the artifact, unrealisable in the institution implementing it.

**Signature.** `◇`-in-structure with `¬◇`-in-practice for the same capacity.

**Institutional example, the primary detector target.** A capacity conferred in the text with **no procedural pathway specified for invoking it**: a right to object with no route by which an objection is made, received, or decided. The capacity exists *de jure* and cannot be exercised. At the remedy locus this is the located type **Repair Failure** (K-D3 at `remedy`).

**Second example.** Fuller's congruence desideratum, and Pound's law in books against law in action: official action diverging from the declared rule, so that a capacity the rule confers is not one the institution delivers. At the act locus.

**Third example, the middle-value case.** An artifact that does not perform the act at all can still fail here. A classification specifies criteria to be applied by clinicians it does not license; if it specifies a determination the surrounding clinical institution cannot in fact make, the *de jure* half sits inside the document and the *de facto* half outside it. Rare, because the artifact is describing a promise made elsewhere rather than making one. **Not never** — and whether it is rare or never is the empirical question on which the three-valued gate stands or falls.

**Near miss.** A capacity that is *hard* to exercise, or expensive, or rarely used, is not a modal clash. And a capacity whose pathway lies in an instrument outside the corpus is **not a source-level failure at all**: it must be set aside as external and reported separately. A K-D3 rate that collapses when external references are excluded is not a finding.

**Instrument.** Process modelling, or text-internal structural analysis. **Status. Operationalised.** See `rkernel.extract.kd3` and §7 of the specification for the two-condition matcher requirement.

---

## The primitives at a glance

| ID | Name | Stratum | Instrument | Operationalised |
| --- | --- | --- | --- | --- |
| K-A1 | Inconsistency | A | reasoner | no |
| K-A2 | Term Incoherence | A | reasoner | no |
| K-A3 | Indeterminacy | A | structural | no |
| K-B1 | Circularity | B | reasoner (partial) | no |
| K-B2 | Equivocation | B | structural | no |
| K-B3 | Residual Definition | B | structural | no |
| K-C1 | Category Violation | C | reasoner | no |
| K-C2 | Level Confusion | C | structural | no |
| K-C3 | Dependence Violation | C | reasoner (partial) | no |
| K-D1 | Falsification | D | world-facing | **no, and will not be** |
| K-D2 | Performative Self-Defeat | D | process / text-internal | partial |
| K-D3 | Modal Clash | D | process / text-internal | **yes** |

One primitive in twelve has a working detector in this release. That is the honest state of the instrument, and it is why nothing here emits an aggregate score.
