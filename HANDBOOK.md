# Building BFO-Compliant Social Ontologies

### A handbook

**For people who can read an OWL file but have not built a social ontology before.**

You will need: a text editor, Protégé or a reasoner, and Python 3.10 or later. No prior BFO experience is assumed. Where a chapter has a tool that does the work, it is named at the end of the chapter.

Companion documents: [`spec/SPEC.md`](spec/SPEC.md) is the normative specification, [`spec/PRIMITIVES.md`](spec/PRIMITIVES.md) the reference for the twelve primitives, [`spec/owl/README.md`](spec/owl/README.md) the OWL module.

---

## Contents

1. [Why the usual methods break](#1-why-the-usual-methods-break)
2. [The BFO you actually need](#2-the-bfo-you-actually-need)
3. [The recognition chain](#3-the-recognition-chain)
4. [Assigning link status, and the trap in it](#4-assigning-link-status-and-the-trap-in-it)
5. [Six modelling patterns](#5-six-modelling-patterns)
6. [The contradiction kernel](#6-the-contradiction-kernel)
7. [Well-formedness: where a failure can sit](#7-well-formedness-where-a-failure-can-sit)
8. [The gating rule and the four profiles](#8-the-gating-rule-and-the-four-profiles)
9. [Walkthrough: journal peer review](#9-walkthrough-journal-peer-review)
10. [Reasoning, and what a reasoner cannot tell you](#10-reasoning-and-what-a-reasoner-cannot-tell-you)
11. [Twelve mistakes, with the tell for each](#11-twelve-mistakes-with-the-tell-for-each)
12. [Reporting discipline](#12-reporting-discipline)
13. [Tool reference](#13-tool-reference)
14. [One-page checklist](#14-one-page-checklist)

---

## 1. Why the usual methods break

Applied ontology has excellent quality methods. OntoClean will tell you that you have put a role where a kind belongs. OOPS! will find dozens of defect patterns in a live ontology. The OntoUML anti-pattern catalogue is a genuine achievement of empirical engineering.

Now try to use any of them on a statute.

They will work, up to a point. They will find circular definitions, category errors, terms defined only by what they exclude. What they will not find is the thing that makes a statute a statute: that it confers powers people cannot exercise, that its officials act in ways it does not authorise, that its remedies exist on paper and nowhere else.

This is not an oversight in those tools. It is a fact about what they were built for. A gene ontology describes; it does not decide. Nothing in it can fail to be *carried out*, because nothing in it is carried out at all. The evaluation literature has no category for that class of failure because its objects do not have it.

The gap opens when you take an instrument built for descriptive artifacts and point it at an institution. You get a clean report and a false sense of security, because the failures the instrument cannot see are scored as absent.

**What this handbook gives you** is a way to tell, before you evaluate anything, what kind of artifact you are holding, and therefore which failures it can and cannot suffer. That turns out to be readable from a small amount of structure, and the structure is the same across law, medicine, certification, accreditation, professional licensing, and everything else where a status is conferred on a case.

### The one-line version

> **typology = kernel × chain**

A domain's failure typology is a *derived* thing: twelve domain-neutral primitives crossed with the positions in that domain's recognition chain. You do not compile a list of defects by observation. You derive one, and then check whether it happens.

---

## 2. The BFO you actually need

BFO is the Basic Formal Ontology, an ISO-standard upper ontology. It supplies a small set of top-level categories that everything else hangs from, and it asserts that some of those categories are disjoint. That disjointness is the whole reason it is useful to you: it is what makes certain mistakes into detectable contradictions rather than matters of taste.

You need about eight categories.

### The first cut: continuant or occurrent

**Continuants** persist through time and are wholly present whenever they exist. A judge, a document, a role, a certificate.

**Occurrents** unfold through time and have temporal parts. A hearing, a diagnosis, an inspection, an appeal.

These are disjoint. Nothing is both. If you find yourself wanting to type something as both, you have found a real modelling problem, not a limitation of BFO.

A useful test: can you point at all of it right now? A trial is not something you can point at all of right now; only today's part of it is happening. A courthouse you can.

### Among continuants: independent or dependent

**Independent continuants** do not need a bearer. People, buildings, documents-as-objects, organisations.

**Specifically dependent continuants** must inhere in some particular independent continuant, and cannot migrate. My fragility is mine; it cannot become yours. Qualities and realizable entities are of this kind.

**Generically dependent continuants** need *some* bearer but not a particular one. A novel needs to be inscribed somewhere, but it survives the destruction of any given copy. This is the category for patterns, and it is where nearly all social content ends up.

### The four you will use constantly

| Category | BFO IRI | What it is | Social example |
| --- | --- | --- | --- |
| Process | `BFO_0000015` | an occurrent | a certification decision |
| Role | `BFO_0000023` | a realizable entity a thing has because of how it is treated by others | judge, certifying agent, licensed pharmacist |
| Generically dependent continuant | `BFO_0000031` | a pattern needing some bearer | the text of a statute |
| Material entity | `BFO_0000040` | an independent continuant with matter | a person, a farm |

**Roles are the workhorse of social ontology.** A role is a realizable entity that a thing has *contingently*, because of the social context it sits in, and that is realized in processes. You are not born a judge. You become one because a body with the authority to do so confers the role, and the role is realized when you decide cases. Contrast a **disposition**, which a thing has because of how it is built: the fragility of glass is not conferred by anyone.

That distinction is going to matter enormously in Chapter 5, and getting it wrong is how ontologies come to assert biology they meant to stay neutral about.

### Information: IAO

BFO alone has no category for "the content of a document". The Information Artifact Ontology supplies it.

| Term | IRI | Use for |
| --- | --- | --- |
| Information content entity | `IAO_0000030` | the content of any document or record |
| Directive information entity | `IAO_0000033` | content that says what is to be done: rules, criteria, specifications |
| Data item | `IAO_0000027` | a measurement or record, including a detector's finding |
| is about | `IAO_0000136` | relates content to what it concerns |

An information content entity is a generically dependent continuant. The Federal Rules of Civil Procedure are not the paper. Burn every copy and reprint them and it is the same rules.

### Relations

Use imported relations wherever one exists. The important ones:

| Relation | IRI | Reads |
| --- | --- | --- |
| part of | `BFO_0000050` | x is a continuant part of y |
| has part | `BFO_0000051` | inverse of the above |
| characteristic of | `RO_0000052` | a dependent continuant is a characteristic of its bearer |
| has characteristic | `RO_0000053` | inverse |
| realizes | `BFO_0000055` | a process realizes a role or disposition |
| has participant | `BFO_0000057` | a process has a participant |
| is about | `IAO_0000136` | content is about a thing |
| has output | `RO_0002234` | a process has an output |

**Do not invent a relation that already exists.** Every local relation is a small tax you pay forever, in mappings, in review, in explaining yourself. This project ships exactly two local relations, and each has a note saying why nothing imported has its shape.

> ### ⚠ The silent-alignment failure
>
> Type `obo:BFO_0000123` into an ontology. It parses. It serialises. It reasons. Every tool reports success.
>
> There is no such BFO term. OWL simply created a fresh class that nobody has said anything about, and every restriction you build on it is inert.
>
> This means **you cannot verify an alignment with a reasoner**. A consistency check tells you nothing about whether your IRIs are real. You have to look them up, and you have to check their labels too, because referring to the right IRI under the wrong description is how a module ends up wired backwards while passing every structural check.

**Tool:** `make bfo` runs `tools/check_bfo.py`, which resolves BFO, IAO and RO and reports every IRI that is not declared upstream or whose label disagrees with your registry. Run it every time you touch an IRI.

---

## 3. The recognition chain

Here is the structure that repeats across every domain where a status is conferred on a case.

| # | Link | The question it answers |
| --- | --- | --- |
| 1 | **Source of authority** | who is entitled to fix the criteria? |
| 2 | **Criteria** | what standard is applied? |
| 3 | **Assessor in role** | who is licensed to apply it? |
| 4 | **Presenting facts** | what is it applied to? |
| 5 | **Recognition act** | the applying, in which a status is conferred |
| 6 | **Effects** | what follows from the conferral? |
| 7 | **Remedy** | how, if at all, is a conferral revisited? |

None of this is new. You will recognise the shape of a status function declaration in Searle, of power and liability positions in Hohfeld, of capacitative norms in the deontic logic literature. The contribution here is not the chain. It is using the chain as an **index set**: a set of positions over which to generate a typology of failure.

### Finding the chain in a real domain

Read the governing documents and answer the seven questions in order. Some tips.

**Authority is rarely where you first look.** It is not the person who signs; it is the source that entitles them to. For a professional licensing board it is usually the enabling statute, and the question is whether the board's own rules exercise that authority or merely cite it.

**Criteria and authority get confused** when one document does both. Separate the question *who may set the standard* from *what the standard says*.

**The assessor is a role, not a person.** Ask: who is licensed by the authority to apply the criteria, and what makes them licensed?

**Presenting facts are what the criteria are applied to.** An inspection report, a set of exam results, a clinical presentation. Note whether the system regulates how these are established.

**The recognition act is the moment of conferral.** A judgment, a certification, a diagnosis, a title award. If nothing is conferred, you may not have a chain at all, which is itself the answer.

**Effects are what changes because of the conferral.** Ask what the holder can now do, or is now liable for.

**Remedy is the link people get wrong most often.** See the box.

> ### ⚠ Revision is not remedy
>
> A classification that revises its criteria every few years has a revision process. It does not thereby have a remedy.
>
> A remedy revisits **a particular conferral**. Revision changes **what future acts will apply**. They sit at different links and they gate differently. Conflating them is the single commonest error in assigning a chain, and it will flip your system's computed kind from classification to certification scheme.
>
> Test: after the process runs, has any individual's status changed? If only the rule changed, it was revision.

### Exercise 3.1

Write out the seven links for a driving licence in your jurisdiction. Then for a university degree. Then for a Michelin star. One of the three has an interestingly thin remedy link.

---

## 4. Assigning link status, and the trap in it

Each link gets exactly one of three values.

| Status | Condition |
| --- | --- |
| **internal** | the system specifies the link **and** it is carried out under the system's own authority |
| **external** | the link occurs but is neither specified nor governed by the system |
| **absent** | the system has no such link at all |

That conjunction in "internal" is load-bearing, and it is where almost everyone goes wrong first.

> ### ⚠ Specification is not performance
>
> A diagnostic manual specifies its criteria in enormous detail. Hundreds of pages. It is the thickest thing in the document.
>
> Its criteria link is **external**.
>
> Why: the criteria are applied by clinicians the manual does not license. Specification without performance under the system's own authority does not satisfy the definition. Record it as internal and you will report the pragmatic stratum as firing at full rate on the artifact's thickest link, which is exactly the reading the whole framework exists to prevent.
>
> Because specification-thickness is nonetheless real and interesting, record it separately. Our chain schema has an optional `specification` field alongside `status`. Only `status` feeds the reasoning. The other is documentation.

### Reading the system's kind off the statuses

Once the seven statuses are fixed, the kind of system falls out without consulting a single substantive rule:

| Recognition act | Remedy | Kind |
| --- | --- | --- |
| absent (and no other link) | — | reference ontology |
| external | external or absent | classification |
| external | internal | certification scheme |
| internal | internal | legal order |

That is the first payoff. You can classify an institution from a redacted skeleton in which the domain, the subject matter, and every substantive rule have been stripped out.

### Writing the chain down

Chains are JSON, validated against [`spec/schema/chain.schema.json`](spec/schema/chain.schema.json):

```json
{
  "chain_id": "peer_review",
  "system": { "label": "Journal X editorial policy",
              "declared_kind": "certification_scheme" },
  "committed_before_detection": true,
  "links": {
    "criteria": {
      "status": "internal",
      "specification": "internal",
      "filler": "the journal's stated scope and review standards",
      "confidence": "high",
      "evidence": [{ "locator": "Editorial policy §2",
                     "note": "states the grounds for acceptance" }]
    }
  }
}
```

Three fields carry more weight than they look.

**`evidence`** is a locator for every status you assign. If you cannot cite a passage, you are guessing, and you should record `confidence: low` and say so.

**`confidence`** is where you flag the links you argued with yourself about. In practice disagreement concentrates at **assessor in role** and **remedy**. Expect it there and mark it.

**`committed_before_detection`** should be true. Fix the chain before you run any detector over the corpus. Otherwise you will tune the chain to the findings, which is how a framework comes to confirm itself.

**Tool:** `rkernel draft-chain corpus.json` proposes a chain from cue density. It is a *draft*. Chain extraction has no established reliability, and every status it proposes needs a human with the documents open.

### Exercise 4.1

Take the ICD-11 chain in `examples/icd11/icd11.chain.json`. Change `criteria.status` from `external` to `internal` and run `rkernel typology`. Watch what happens to the Stratum D row. That is what the trap costs.

---

## 5. Six modelling patterns

These are the patterns that recur. Each solves a problem that has a wrong answer people reach for first.

### 5.1 The chain is specifications, not links

**Wrong:** an object called `RecognitionChain` with seven parts, each carrying a status.

**Right:** the artifact is an information content entity. Each link it specifies is a directive information entity that is `part of` the artifact.

```turtle
rk:ChainSpecification a owl:Class ;
    rdfs:subClassOf obo:IAO_0000033 ;
    rdfs:subClassOf [ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;
                      owl:someValuesFrom rk:RecognitionArtifact ] .
```

Why this matters is the next pattern.

### 5.2 Absence is absence of a part

**Wrong:**

```turtle
rk:GOActLink a rk:ChainLink ; rk:hasStatus rk:Absent .
```

Read that aloud. It asserts that a thing exists, and then says of that thing that it does not exist. Under a realist reading it is incoherent, and it was in this repository until we caught it.

**Right:** the artifact simply has no part of that kind.

```turtle
rk:ActEmptyArtifact a owl:Class ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        rk:RecognitionArtifact
        [ a owl:Restriction ; owl:onProperty obo:BFO_0000051 ; owl:allValuesFrom
          [ a owl:Class ; owl:complementOf rk:RecognitionActSpecification ] ] ) ] .
```

The universal restriction (`allValuesFrom`) supplies closure that the open world assumption otherwise denies. Without it, a reasoner will always suppose there might be an act specification you have not mentioned.

**General rule: never mint an individual to represent something that does not exist.** If you need to say a thing is missing, say it about the whole, not about a stand-in for the part.

### 5.3 Conferred status is two-part

This is the pattern with the most at stake.

A status is conferred on a case. What kind of entity is it?

**Option A: a role.** Clean, BFO-natural, gives you a bearer. But typing a status as a role asserts that a realizable entity inheres in the bearer. For a certification that is fine. For a contested psychiatric category it asserts precisely the thing the classification's own authority may be declining to assert.

**Option B: a generically dependent continuant.** Neutral about the bearer, but *too* neutral: a GDC does not inhere in anything, so there is no bearer for the assertion to be made or withheld about. You cannot say who holds the status.

**Option C, and the right answer: both, separately.**

```turtle
rk:ConferredStatusRole a owl:Class ;
    rdfs:subClassOf obo:BFO_0000023 ;
    rdfs:subClassOf [ a owl:Restriction ; owl:onProperty rk:conferredBy ;
                      owl:someValuesFrom rk:RecognitionAct ] .

rk:StatusDeclaration a owl:Class ;
    rdfs:subClassOf obo:IAO_0000030 ;
    rdfs:subClassOf [ a owl:Restriction ; owl:onProperty obo:IAO_0000136 ;
                      owl:someValuesFrom obo:BFO_0000004 ] .
```

The declaration is content, about the bearer, produced as the output of the act. The role inheres in the bearer and is realized in the effects.

**Why go to the trouble:** because the two-part model can represent a configuration neither single-part model can, namely a system that records and mandates a status while declining to assert that anything inheres in anyone. That is not a hypothetical. It is WHO's published position on ICD-11 Chapter 26, where traditional-medicine patterns are recorded, dual coding is required, and efficacy is expressly not endorsed. In the module that configuration is `rk:DeclarationWithoutBorneRole`.

Note the honest limitation attached to it: under the open world assumption nothing will be *classified* there without a closure axiom. It exists to make a position statable, not to be inferred. Say so in an editor note rather than letting a reader assume it fires.

### 5.4 Locus is mereology

A contradiction "at the criteria locus" is just one that is `part of` a criteria specification. You do not need an `atLocus` relation and you should not build one.

```turtle
rk:CriterionCircularity a owl:Class ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        rk:Circularity
        [ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;
          owl:someValuesFrom rk:CriteriaSpecification ] ) ] .
```

Two benefits. You use an imported relation instead of a local one. And because the named type is now a **defined class**, a reasoner classifies into it. Assert a circularity part of a criteria specification and HermiT tells you it is a criterion circularity. Nobody looked anything up in a table.

### 5.5 Contradictions are information content entities

A contradiction is a `part of` the artifact bearing it, and it is content, not a quality.

The argument is short: two printings of the same code carry the same contradiction. A quality would inhere in a particular material bearer and could not do that. So the entity is generically dependent, and specifically it is information content.

This buys you something unexpectedly valuable. A **finding** is then a data item that `is about` a contradiction, which separates the defect from the report of the defect. And since a contradiction is part of *some* artifact, provenance becomes structural:

```turtle
rk:SourceLevelFinding      ≡ finding about a contradiction part of a SourceArtifact
rk:TranslationLevelFinding ≡ finding about a contradiction part of a FormalizedArtifact
```

The distinction between "the statute is incoherent" and "my formalisation of the statute is incoherent" stops being a discipline you have to remember and becomes a fact about which artifact the thing is part of.

### 5.6 Not everything is an entity

Strata are universals: a model-theoretic contradiction is a kind of contradiction, so it is a class. Fine.

Crossings are not. A crossing is a position in a classification scheme, not something in the world. Typing one as a BFO entity would be a category violation in the very ontology that defines category violation.

Firing values are not entities either. A firing value is a rate claim, and a rate is not something the world contains. Both live in annotations.

**General rule:** before you mint a class, ask whether instances of it exist in the world or only in your description of the world. Bookkeeping goes in annotations.

---

## 6. The contradiction kernel

Twelve primitives, in four strata. The strata are indexed by **the kind of structure a failure presupposes in order to be possible at all**, which is not how the existing defect catalogues are organised, and which is what makes the rest of this work.

### Stratum A, model-theoretic. Presupposes: a formal theory.

| | Primitive | Signature |
| --- | --- | --- |
| K-A1 | **Inconsistency** | jointly unsatisfiable assertions; no model |
| K-A2 | **Term Incoherence** | theory satisfiable, but some class is necessarily empty |
| K-A3 | **Indeterminacy** | underconstraint; unintended models, or borderline membership undecidable |

### Stratum B, definitional. Presupposes: a system of definitions.

| | Primitive | Signature |
| --- | --- | --- |
| K-B1 | **Circularity** | a definition cycle, or a grounding order inverted |
| K-B2 | **Equivocation** | one item bound to two roles with conflicting conditions |
| K-B3 | **Residual Definition** | membership fixed by complement, no positive differentia |

### Stratum C, meta-ontological. Presupposes: an upper ontology.

| | Primitive | Signature |
| --- | --- | --- |
| K-C1 | **Category Violation** | one entity under two disjoint upper-level categories |
| K-C2 | **Level Confusion** | universal treated as particular, class as instance, use as mention |
| K-C3 | **Dependence Violation** | a dependent entity with no bearer; grounding severed |

### Stratum D, pragmatic. Presupposes: **acts**.

| | Primitive | Signature |
| --- | --- | --- |
| K-D1 | **Falsification** | asserted triggering condition with no worldly truthmaker |
| K-D2 | **Performative Self-Defeat** | an act whose success conditions its own performance undermines |
| K-D3 | **Modal Clash** | a capacity present in structure, blocked in practice |

Stratum D is the one the evaluation literature does not address, for the good reason that its usual objects do not have acts.

### Telling neighbouring primitives apart

**A1 versus A2.** Inconsistency means the theory has no model. Term incoherence means the theory has a model but some class in it cannot be populated. Add an instance of the incoherent class and you get inconsistency.

**A3 versus B3.** Indeterminacy is underconstraint: the definition does not settle the borderline. Residual definition is negative definition: the term is *defined* as whatever is left over. A residual category is usually also indeterminate, but the reverse is not true.

**B1 versus C3.** Circularity is a cycle in a definitional or grounding order. Dependence violation is a *missing* ground. One goes round, the other stops short.

**C1 versus C2.** Category violation is being in two disjoint boxes. Level confusion is being on two levels of representation at once. A class asserted to be both a process and an object is C1. A class used as an instance of itself is C2.

**D2 versus D3.** In self-defeat, complying with the norm is what breaks it. In modal clash, the capacity is fine but the institution cannot deliver its exercise. Self-defeat is internal to the content; modal clash is a mismatch between content and world.

### Which instrument sees what

| Instrument | Primitives |
| --- | --- |
| Description-logic reasoner | A1, A2, C1; part of B1; part of C3 |
| Structural analysis of axioms | A3, B2, B3, C2; part of B1 |
| World-facing data | D1 |
| Process modelling or text-internal analysis | D2, D3 |

> ### ⚠ A reasoner is necessary and never sufficient
>
> Half the kernel is invisible to description logic **in principle**, not for want of a better reasoner. If your pipeline reports only reasoner output, it has covered Stratum A and part of C and silently scored the other half as zero.
>
> Report stratum by stratum. Never emit a single aggregate score over the kernel.

---

## 7. Well-formedness: where a failure can sit

Not every primitive makes sense at every link. Falsification needs something asserted about the world, and authority is conferred rather than asserted, so falsification at the authority link is not a rare failure but a non-coordinate.

Each primitive therefore carries a **locus mask**: the links at which it is well-formed. Over the seven links, 70 of the 84 cells are well-formed in this kernel.

Encode the mask as unsatisfiability axioms, so it is checkable rather than documentary:

```turtle
[ a owl:Class ;
  owl:intersectionOf ( rk:TermIncoherence
                       [ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;
                         owl:someValuesFrom rk:PresentingFactsSpecification ] ) ;
  rdfs:subClassOf owl:Nothing ] .
```

Assert a term incoherence at presenting facts and the ontology goes inconsistent, which is what you want: presenting facts are asserted, not defined, so there is no definition there to empty out.

### The pseudo-locus

There is an eighth position, the **artifact body**: the definitional content considered apart from any chain link.

It exists because a reference ontology performs no link and can still be inconsistent. Without a position present unconditionally, Strata A, B and C would have nowhere to sit in a chainless artifact. Every ungated primitive is well-formed there; no Stratum D primitive is.

### Distinguish two kinds of nothing

| Value | Means |
| --- | --- |
| `cannot_fire` | the crossing exists; the chain bars the primitive there |
| `not_applicable` | there is no such crossing; the locus does not supply the structure |

Collapsing these loses the difference between *this system has no remedy* and *this primitive could not sit at a remedy in any system*.

---

## 8. The gating rule and the four profiles

Here is the whole rule.

**Strata A, B and C are ungated.** Their preconditions are rules, definitions and top-level kinds, all of which live inside the artifact. The chain is irrelevant to them.

**Stratum D is gated three ways, per link:**

| Link status | Stratum D at that link |
| --- | --- |
| internal | **fires** |
| external | **fires only rarely** |
| absent | **cannot fire** |

That is it. And it yields:

| Kind | Thickness | A | B | C | D |
| --- | --- | --- | --- | --- | --- |
| Reference ontology | act-empty | fires | fires | fires | cannot fire |
| Classification | act-thin, repair-external | fires | fires | fires | rare |
| Certification scheme | act-thin, repair-internal | fires | fires | fires | rare |
| Legal order | act-thick, repair-internal | fires | fires | fires | fires |

The A, B and C columns are constant. That is not a weakness; it is the rule working. What differs between kinds of system is not whether they can fail definitionally, but whether they can fail pragmatically.

### On the middle value

Why not a binary rule: acts internal, pragmatic failure possible; otherwise not?

Because a system whose act is external still specifies what the act is *for*, and can therefore specify a capacity the surrounding institution cannot deliver. The *de jure* half sits inside the document and the *de facto* half outside it.

Such cases should be rare. **But rare and never are different, and the difference is empirical rather than definitional.** Nothing in the definition fixes that rate. It could be zero. It could be indistinguishable from the internal rate, in which case the gate does no work. Both outcomes are possible and both must be reported if found.

If you are building on this, that is where to point your effort: the certification cell, which is act-thin like a classification and repair-internal like a legal order, is the only one whose result could distinguish a three-valued gate from a two-valued one.

### Summarising a stratum

Summarise gated strata **at the recognition act**, not by taking a maximum over links. A maximum reports `fires` for any system with one internal link anywhere, which collapses exactly the distinction the rule is about.

But always emit the per-link detail too. Classification and certification share a Stratum D summary and differ at three links, most sharply at remedy:

```
| System     | authority | criteria | assessor | facts | act  | effects | remedy |
| 7 CFR 205  | fires     | fires    | fires    | rare  | rare | rare    | fires  |
| ICD-11     | fires     | rare     | rare     | rare  | rare | rare    | rare   |
```

Comparing at summary level asks whether two rates differ. Comparing per link asks *where*, which needs far fewer corpora to answer.

### Two consequences worth internalising

**Profiles are readable from shape.** You can predict the failure profile from a redacted skeleton, before reading a single substantive rule.

**Emptiness is informative, not reassuring.** An empty pragmatic stratum reports that the artifact describes rather than decides. Reading it as a clean audit is the natural error and the wrong one.

**Tool:** `rkernel typology chain.json`, `rkernel profile chain.json`, `rkernel compare a.json b.json`.

---

## 9. Walkthrough: journal peer review

Let us build one from nothing. Journal peer review is familiar, and it produces a genuine surprise.

### Step 1: the chain

Read the journal's editorial policy and answer the seven questions.

| Link | Filler | Status | Reasoning |
| --- | --- | --- | --- |
| authority | the editorial board, under the publisher's constitution | internal | the policy states who sets the standards and exercises that power itself |
| criteria | scope, novelty, methodological soundness | internal | specified in the policy, applied under the editor's authority |
| assessor | reviewers and the handling editor | **contested** | see below |
| facts | the submitted manuscript and reviewer reports | internal | the policy regulates what may be considered |
| act | the accept or reject decision | internal | the editor decides, under the journal's own procedure |
| effects | publication, citation, career credit | **external** | conferred by the field, not the journal |
| remedy | ? | **contested** | see below |

### Step 2: the two contested links

**Assessor.** Are reviewers licensed by the journal? They are invited by the editor, which looks like conferral. But their standing to review comes from their disciplinary reputation, which the journal neither confers nor governs. The *handling editor* is unambiguously internal; the *reviewers* look external.

You have to choose, record the choice, and mark it `confidence: low`. My reading: internal, because the editor is the assessor of record and the reviewers are advisory. Someone could reasonably disagree, and this is exactly the kind of disagreement an inter-annotator study exists to settle rather than an argument.

**Remedy.** Here is the surprise. Ask the test from Chapter 3: after the process runs, has any individual's status changed?

- *Appeal against rejection*: yes, a conferral is revisited. That is a remedy, and many journals have one.
- *Retraction*: a status is withdrawn, but it is a fresh act on new facts rather than a revisiting of the original decision. Arguably not remedy.
- *Corrigendum*: changes the content, not the status. Not remedy.

If the journal has an appeals process, remedy is internal and you have a **certification scheme** in the same structural family as an organic certification body. If it does not, remedy is absent and you have something act-thick with no repair, which is not one of the four canonical profiles at all.

That is a real finding about scholarly publishing, and it fell out of seven questions.

### Step 3: write the chain

```json
{
  "chain_id": "peer_review",
  "system": { "label": "Journal X editorial policy",
              "declared_kind": "certification_scheme" },
  "committed_before_detection": true,
  "links": {
    "authority": { "status": "internal", "confidence": "high",
                   "filler": "editorial board" },
    "criteria":  { "status": "internal", "specification": "internal",
                   "confidence": "medium",
                   "note": "Specified, but the standards are famously underdetermined; expect K-A3 at this locus." },
    "assessor":  { "status": "internal", "confidence": "low",
                   "note": "Handling editor internal; reviewers arguably external. Flagged for agreement study." },
    "facts":     { "status": "internal", "confidence": "medium" },
    "act":       { "status": "internal", "confidence": "high" },
    "effects":   { "status": "external", "confidence": "high",
                   "note": "Career credit is conferred by the field. The journal cannot deliver it." },
    "remedy":    { "status": "internal", "confidence": "low",
                   "note": "Appeals only. Retraction is a fresh act, not a revisiting." }
  }
}
```

### Step 4: generate and read

```bash
rkernel typology peer_review.chain.json
```

You get a computed kind, a profile, and about eighty predicted failure modes. Read them as hypotheses. Some that stand out:

- **K-A3 at criteria.** Underconstrained standards where the artifact's own purpose requires a determinate answer. This is the reproducibility literature's complaint, at a coordinate.
- **K-D3 at effects.** A capacity present in structure and blocked in practice: the journal confers publication and cannot confer the credit that publication is *for*, because effects are external. Predicted from the chain alone.
- **K-B2 at authority.** Equivocation where one body both sets standards and adjudicates compliance with them. Editors who both write the policy and apply it.
- **K-D3 at remedy.** A right of appeal with no specified pathway for making one. Directly testable against the policy text.

### Step 5: test one

Take K-D3 at remedy. The detector looks for capacities conferred in the text with no procedural pathway for invoking them, and it requires **two independent conditions over disjoint vocabularies**: that a provision is about the same capacity, and that it supplies a procedural marker. If one similarity test does both jobs, every procedural provision resembles every capacity and you are measuring the density of procedural language.

```bash
rkernel detect peer_review_policy.json
```

Read the fan-out before the rate. If the median capacity matches a dozen pathways, the zero-match cases are lexical accidents rather than structural facts and no rate from that run means anything.

### Exercise 9.1

Do the same for a professional licensing board, a sports federation's title system, and a university's academic misconduct procedure. Predict each computed kind before running the generator.

---

## 10. Reasoning, and what a reasoner cannot tell you

### Get one running

HermiT works under Java 21. **Pellet does not** and fails with `UnsupportedClassVersionError`. Use HermiT, through Protégé or through owlready2.

### The two-negative-test pattern

Anyone can write an axiom. The question is whether it is enforced.

For every rule you encode, ship an ABox that **must be inconsistent**, and test that it is:

| File | Asserts | Must be |
| --- | --- | --- |
| `example-abox.ttl` | three artifacts, several contradictions | consistent |
| `gating-violation.ttl` | a pragmatic contradiction in an act-empty artifact | **inconsistent** |
| `mask-violation.ttl` | a term incoherence at presenting facts | **inconsistent** |

Two negative tests, because the gating rule and the locus mask are separate claims that fail separately. A suite testing only the first would not notice the second being dropped.

### And test that inference happens

Because named types are defined classes, assert a modal clash part of a remedy specification and check that the reasoner returns `RepairFailure` without being told. If it does not, your definitions are subclass axioms where they should be equivalences.

### The open world will surprise you

OWL assumes anything not stated might still be true. So "this artifact has no recognition act specification" is not something you can assert by silence. Use a universal restriction to close the class, as in pattern 5.2.

More generally: **a reasoner cannot tell you that something is absent.** It can tell you that what you asserted is impossible. Those are different, and most of the interesting social-ontology questions are about absence.

> ### ⚠ Consistency can pass for the wrong reason
>
> We hit this in this repository. The module imports BFO. In an environment where the import cannot be resolved, `obo:BFO_0000050` is undeclared, every restriction built on it goes inert, the gating axiom silently stops firing, **and the consistency check passes**.
>
> A check that passes for the wrong reason is worse than a missing one, because it produces confidence.
>
> Two defences. Ship a declarations-only stub so your own axioms stay checkable offline, and have the validator **report which mode it ran in**. And keep the alignment check separate, because consistency was never going to verify it.

---

## 11. Twelve mistakes, with the tell for each

Every one of these was made, by us, in building this.

**1. Minting an entity to represent an absence.** Tell: an individual with a property whose value is "absent", "none", or "not applicable". Fix: absence of a part.

**2. Confusing specification with performance.** Tell: a document-heavy link marked internal because the document says a lot about it. Fix: ask who carries it out, under whose authority.

**3. Treating revision as remedy.** Tell: a classification coming out as a certification scheme. Fix: ask whether any individual's status changed.

**4. Treating curation as authority.** Tell: a reference ontology acquiring a chain. Fix: ask whether anyone is entitled to confer a status on a case. Curating a description is not that, and if you allow it, every scientific ontology becomes an institution and the framework says nothing.

**5. Trusting a consistency check to verify an alignment.** Tell: no separate IRI check in the pipeline. Fix: `make bfo`.

**6. Reporting reasoner output as coverage.** Tell: a single number for "defects found". Fix: report by stratum, and mark cells with no detector as undetectable, never as zero.

**7. Conflating source and translation.** Tell: a finding attributed to a statute that is actually an artifact of your OWL. The largest single source of artifactual incoherence in extraction pipelines has been a category misuse of `bearer-of`, in which a class correctly grounded as a disposition also gets a `has disposition some ...` restriction and is forced under two disjoint BFO categories. It presents exactly like a defect of the source. Fix: default provenance to `undetermined` and make no detector able to emit `source`.

**8. A matcher that measures vocabulary density.** Tell: high fan-out. Ours had a median of twelve, a mean of twenty-one, and one provision returned as the pathway for sixty-seven unrelated capacities. Fix: two conditions over disjoint vocabularies, and report fan-out unconditionally.

**9. Precondition mismatch mistaken for a null result.** Tell: an extractor returning zero with no errors. An ontological-claim extractor on a procedural code returns nothing at all, because a procedural code makes almost no claims about kinds. Fix: run two extractors over the same input in the same pass and report both yields.

**10. A confirming null from tooling that was never built.** Tell: an empty stratum from a pipeline that operationalised no primitive in that stratum. An empty Stratum D is what you observe if the gating rule holds, *and* what you observe if the detector does not exist. Fix: report "awaiting re-run", not "no findings".

**11. A tautological empirical claim.** Tell: an impressive fit statistic. Check whether your outcome variable is derived from the same inputs as your predictors. If a rule table computes the outcome from the same closures that determine your score, the score and the outcome are mutually entailed by construction and the number measures nothing.

**12. Two copies of the source of truth.** Tell: an edit that appears to have no effect. We had `data/kernel.json` and a packaged copy under `src/`, and the packaged one silently won. Fix: one canonical file, a resolver that prefers it, and a build step that syncs the rest.

---

## 12. Reporting discipline

Six rules. Put them in your output, not just in your head.

1. **Firing values are predictions about possibility, not detections of incidence.** A cell marked `fires` says the failure can occur.

2. **Not detected is not zero.** Mark every cell whose primitive has no detector.

3. **Provenance defaults to undetermined.** No detector may emit `source`.

4. **Fan-out is reported unconditionally.** A rate from a matcher whose fan-out is unreported cannot be interpreted.

5. **External dependencies are set aside and reported separately.** A capacity whose pathway lies outside the corpus is not a source-level failure. Report both rates, and if one collapses when externals are excluded, you have no finding.

6. **Record the expected direction of a fix before you make it.** We recorded, in advance, that correcting the matcher should *increase* the candidate count, since the correction withdraws pathways awarded on vocabulary alone. Write that down before running, or you will find yourself able to accept whichever result arrives.

---

## 13. Tool reference

```bash
make venv        # create .venv and install; PEP 668 blocks a system-wide pip
make             # build the OWL module, validate, test, regenerate out/
make bfo         # verify IRIs against the real BFO, IAO and RO
```

| Chapter | Command | What it does |
| --- | --- | --- |
| 2 | `tools/check_bfo.py` | verifies every external IRI is declared upstream with a matching label |
| 3–4 | `rkernel draft-chain corpus.json` | proposes a chain from cue density (a draft) |
| 5 | `tools/build_owl.py` | regenerates the OWL module and the offline stub from `kernel.json` |
| 6–8 | `rkernel typology chain.json` | full typology, profile, predicted failure modes |
| 8 | `rkernel compare a.json b.json` | profiles side by side, with the per-link Stratum D row |
| 9 | `rkernel extract corpus.json` | norm tuples plus the ontological control |
| 9 | `rkernel detect corpus.json` | the K-D3 detector, with fan-out |
| 10 | `rkernel validate` | kernel, schemas, OWL agreement, reasoning |

### Where things live

```
data/kernel.json        the single source of truth
spec/SPEC.md            normative specification
spec/PRIMITIVES.md      the twelve, with examples and near misses
spec/schema/            JSON Schema for kernels, chains, typologies, findings
spec/owl/               the OWL module and three reasoning tests
examples/               four worked cells, each with notes
```

### What this release does not do

One primitive in twelve has a working detector. K-D2 is partial. K-D1 is not operationalised and will not be, because detection needs world-facing ground truth. The other nine await structural detectors or delegation to a reasoner.

Nothing here emits an aggregate score, and neither should anything you build on it.

---

## 14. One-page checklist

**Chain**

- [ ] Seven links identified, each with an evidence locator
- [ ] Status assigned from **performance**, not specification
- [ ] Specification-thickness recorded separately if it matters
- [ ] Revision distinguished from remedy
- [ ] Low confidence marked at assessor and remedy
- [ ] Chain committed before any detector runs

**Ontology**

- [ ] Universals are classes; particulars are individuals
- [ ] Every class has an Aristotelian definition and a definition source
- [ ] Every class has an asserted path to a BFO category
- [ ] No entity minted for anything absent
- [ ] Imported relations used wherever one exists; every local relation justified in a note
- [ ] Bookkeeping in annotations, not classes
- [ ] Conferred status modelled in two parts

**Checking**

- [ ] Every external IRI verified against the real ontologies, labels included
- [ ] At least one ABox that must be consistent
- [ ] One ABox per rule that must be **inconsistent**
- [ ] Defined classes verified to be *inferred*, not merely present
- [ ] The validator reports whether upstream axioms were actually loaded

**Reporting**

- [ ] Results reported stratum by stratum, never aggregated
- [ ] Cells without detectors marked undetectable, not zero
- [ ] Provenance defaults to undetermined
- [ ] Fan-out reported
- [ ] External dependencies set aside, both rates given
- [ ] Expected direction of any fix recorded in advance

---

## Where to go next

Read [`spec/PRIMITIVES.md`](spec/PRIMITIVES.md) for two worked examples and a near miss for each of the twelve. Read [`examples/icd11/NOTES.md`](examples/icd11/NOTES.md) for the hardest of the four cells, including a result that had to be withdrawn. Read [`spec/SPEC.md`](spec/SPEC.md) when you want the normative statement.

Then pick a domain nobody has done, write its seven links, and see what the product predicts. That is the point of the thing.

---

*Handbook to the Recognition Kernel, v0.2.0. Code Apache-2.0; documentation CC BY 4.0.*
*Companion to Koepsell, D. R., "The Recognition Layer: A Generative Typology of Structural Contradiction for Recognition-Constituted Domains".*
