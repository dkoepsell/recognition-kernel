# Worked example 2 — ICD-11

**Cell 2 of the registered design. Act-thin, repair-external. The classification case.**

```bash
rkernel typology examples/icd11/icd11.chain.json
```

No corpus ships with this example. **ICD-11 is copyright WHO and no ICD-11 text is reproduced in this repository.** The chain file records structural facts about the classification's published architecture, with locators, and nothing else. To run detectors against ICD-11 you must obtain the classification yourself under WHO's terms.

## The chain

| Link | Status | Specification | Why |
| --- | --- | --- | --- |
| authority | internal | internal | WHO fixes the classification and does so itself |
| criteria | **external** | **internal** | specified in full, applied by clinicians WHO does not license |
| assessor | external | external | the clinician, licensed elsewhere |
| facts | external | external | the presentation, which the classification neither establishes nor governs |
| act | external | external | a manual does not diagnose |
| effects | external | external | conferred by payers, courts and agencies |
| remedy | external | external | revision happens *to* the manual, not within it |

**The criteria row is the one to read twice.** `status` answers the performance question: does the system carry the link out under its own authority? `specification` answers the specification question: does the system write the link down? For a classification these come apart, and they come apart at exactly the link the classification is thickest at.

Recording criteria as `internal` on the strength of specification alone reports Stratum D as firing at that locus at full rate — the reading the gating rule exists to rule out. A manual that writes criteria for someone else to apply has not thereby performed the link. Only `status` is consumed by the rule; `specification` is documentation, and it exists so that criteria-layer thickness stays visible without corrupting the gate.

**The remedy row is the second.** There is a revision process, and it is real. But it revises the *criteria*; there is no pathway by which a particular conferral is revisited. Those are different links, and conflating them is the commonest error in assigning this chain.

## What the generator produces

Stratum D summarises to `rare`. The per-locus profile shows `rare` at every link except `authority`, where WHO performs the link itself and K-D3 therefore fires at full rate — a derived prediction, not something anyone put in.

The seven classificatory types come out at their coordinates:

| | derived at |
| --- | --- |
| CT-1 Disjointness / Overlap Failure | K-A1 × criteria |
| CT-2 Criterion Circularity | K-B1 × criteria |
| CT-3 Threshold / Polythetic Incoherence | K-A3 × criteria |
| CT-4 Criterion Double-Duty | K-B2 × criteria |
| CT-5 Residual Indeterminacy | K-B3 × criteria |
| CT-6 Recognition Failure | K-C3 × criteria |
| CT-7 Type Contradiction | K-C1 × artifact body |

Two features of that list are explained by the construction rather than stipulated by it. **No member is Stratum D**, because a manual contains no acts of its own. **Every member but CT-7 sits at criteria**, because criteria are the only link a classification specifies in full. Both fall out of the gating rule; neither was decided by hand.

## The withdrawn result

A prior audit layer over a BFO-aligned ICD-11 formalisation returned an **empty Stratum D**, matching the prediction exactly. **It is withdrawn as evidence.**

That layer operationalised four of twelve primitives, all of them A, B or C. An empty D is precisely what one would observe if the gating rule held, and equally what one would observe if the tooling for that stratum did not exist. The run does not distinguish the two hypotheses, and a confirming null produced by a detector that was never built is the failure mode a registered design exists to prevent.

This cell must be re-run with a working D detector before its emptiness counts for anything. Until then the correct entry in the results table is *awaiting re-run*, not *no findings*.

## Chapter 26 and the forced choice

Chapter 26 codes traditional-medicine patterns. WHO declines to endorse their efficacy or safety, deliberately chose *disorder* over *disease* because *disease* implies a clearly defined entity in ICD usage, and requires dual coding alongside a category from Chapters 01–25.

A BFO-aligned extraction pipeline built by someone with no stake in this argument, working to a realist scheme, reached that chapter with three options: type the patterns as dispositions, which asserts a biological claim WHO explicitly withholds; leave them untyped, breaking the scheme; or open a category for entities that exist because they are recorded and recognised. It chose the third and typed them as **generically dependent continuants**, flagging the typing as contestable in its own comment.

Two cautions on how much weight that carries. **It is not a machine discovery** — the typing was a modelling decision, recorded as such. And the blanket K-C1 flag subsequently applied to all 154 extracted members of the branch is a construction decision, not a per-class detection; removing it collapses the branch's flag density from 1.123 to 0.129, *below* the disease branch, and **the strong within-manual gradient is therefore not established**. What survives is weaker: 606 pathogen and genetic classes carry zero flags while every branch with a syndromal or recognition-constituted element carries some, so the floor holds and the extremes match the prediction. The middle does not.

What the episode does show is a forced choice, and the forcing is the point. The alternative account — that the builder simply erred and Chapter 26 patterns are dispositions like everything else — has to explain why WHO chose *disorder* over *disease*, why it mandates dual coding, and why it disclaims efficacy in print. All three are on the record, and all three are what one says about a status conferred rather than a disposition found.

The second neutrality of the framework — bracketing whether a real kind is *warranted*, while insisting it is real — is in this instance **WHO's, not the framework's**. It is applied by WHO to a chapter of WHO's own classification, in print.
