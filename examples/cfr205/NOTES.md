# Worked example 4 (bonus) — 7 CFR Part 205

**Cell 3 of the registered design. Act-thin, repair-internal. The cell that matters.**

```bash
rkernel typology examples/cfr205/cfr205.chain.json
rkernel compare  examples/*/[a-z]*.chain.json
```

The paper's brief asks for three worked examples spanning act-thick, act-thin and act-empty. This is a fourth, included because it is the only cell whose result could distinguish the three-valued gate from a two-valued one, and because a release that shipped only the three easy cells would be shipping the parts of the framework that are close to analytic.

## Why this cell is exposed

Three of the four cells test claims near enough to analytic that failing them would indicate a broken detector rather than a false theory. A reference ontology has no acts and cannot suffer act-failures; a legal order has all of them and can. Neither is news.

The National Organic Program is act-thin like a classification — the regulation does not itself certify — but repair-internal like a legal system, because accreditation and decertification are specified within it. If the three-valued gate is real, its Stratum D rate should sit **measurably between** the legal and classification cells.

**If it is statistically indistinguishable from both, the gate collapses to two values and that will be reported. The detector will not be adjusted to preserve the middle value.**

This cell has not been run. No corpus ships with it. 7 CFR Part 205 is a work of the United States government and is not subject to copyright, so building the corpus is straightforward; the reason it is absent is that the chain must be committed before the detector meets the text, and shipping both together would make that commitment unverifiable.

## What the summary hides, and where to look instead

Run `rkernel compare` across all four chains. The summary column reports Stratum D as `rare` for both this cell and ICD-11 — which is what the published profile table says, and which is exactly the coincidence the paper flags as the framework's soft spot.

The per-locus row is where they part:

| System | authority | criteria | assessor | facts | act | effects | remedy |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 7 CFR 205 | fires | fires | fires | rare | rare | rare | **fires** |
| ICD-11 | fires | rare | rare | rare | rare | rare | **rare** |

Three loci differ. The remedy locus is the sharpest: a certification scheme has an internal repair pathway (§205.662 noncompliance, §205.681 appeals) and a classification does not, so K-D3 fires at full rate in one and rarely in the other.

That difference is a **prediction, derived before any text was read**, and it converts §10.2's crux from an aggregate rate comparison into a per-locus one. Comparing at the summary level asks whether two numbers differ; comparing per locus asks where, which is a question the instrument can answer with far fewer corpora.

## The contested assignment

`assessor: internal`, confidence medium. The scheme accredits its own assessors under subpart F and specifies what they must do, which satisfies the definition. But the source text describes the scheme as thinner than a legal order at this link, and an annotator could defensibly record `external`.

This is one of the two links at which annotator disagreement is expected to concentrate — the other being remedy — and it should be resolved by an agreement study rather than by argument. Two annotators independently extracting the seven links from the same documents, with per-link agreement reported, is a precondition for the empirical design and **has not been run**. Every chain in this repository is a single unreviewed assignment.
