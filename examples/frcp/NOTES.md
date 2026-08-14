# Worked example 1 — Federal Rules of Civil Procedure

**Cell 4 of the registered design. Act-thick, repair-internal. The positive control.**

```bash
rkernel typology examples/frcp/frcp.chain.json
rkernel extract  examples/frcp/corpus/frcp_demo.json
rkernel detect   examples/frcp/corpus/frcp_demo.json
```

## Why this cell exists

Every other cell is interpretable only if this one is non-empty. If Stratum D fails to fire in a system that performs every link itself, then either the detector is invalid or the gating rule is false, and in either case the programme stops until that is resolved. A negative result anywhere else could otherwise always be blamed on a missing instrument.

## The chain

All seven links internal. The Rules specify who is empowered, what standard applies, who applies it, on what showing, with what effect, and by what route a conferral is revisited — and all of it is carried out under the courts' own authority. The generator computes `legal_order` from the statuses alone, without reading a single substantive rule.

Two assignments are worth defending rather than assuming.

**Effects: internal, confidence medium.** Rules 64 and 69 route enforcement through the procedure of the state where the court sits. The effect is nonetheless conferred by the judgment the system itself enters, so the link is recorded as internal with the outward-facing dependence noted. An annotator who recorded `external` would produce a different Stratum D profile at that locus, which is exactly the kind of disagreement the reliability study exists to measure.

**Remedy: internal.** Appellate review lies outside this instrument. But repair-internal does not require that *all* repair be internal, only that the system provide repair pathways of its own — and Rules 55(c), 59 and 60(b) are exactly that.

## What the generator produces

79 crossings fire. Every stratum fires, including D, and the five located types of the Structural Ontology of Law appear at their coordinates: **JC** at K-A1 × effects, **TC** at K-B1 × criteria, **AI** at K-B2 × authority, **CF** at K-C3 × assessor, **RF** at K-D3 × remedy. The generator does not look these up as a list; it derives the cells and then names those it recognises.

## The corpus

`corpus/frcp_demo.json` is **28 abridged provisions**, chosen to exercise the instrument: capacities whose pathway is in the corpus, one capacity whose pathway lies outside it, and a spread of modalities. The Federal Rules are a work of the United States government and not subject to copyright, but the text here is abridged and normalised and is **not authoritative**. Run `tools/fetch_frcp.py` to build a corpus from a real source before reporting anything.

## The extractor pair

| Extractor | Target schema | Yield | Errors |
| --- | --- | --- | --- |
| Entity-relation | ontological claims | 0 | 0 |
| Norm tuple | deontic norms | 36 | 0 |

Same corpus, same provisions, same pass. The entity-relation extractor did not perform poorly. It produced nothing whatever and raised no error while doing so, because a procedural code contains almost no assertions about kinds. *A summons must name the court and the parties* is a rule about what an actor must do, not a claim about what kind of thing a summons is.

A silent zero is what a precondition mismatch looks like from the outside. Running both instruments over the same input in the same pass is what converts that from an explanation into a demonstration. Run the same pair over `examples/go/corpus/go_demo.json` and the yields reverse.

## K-D3 on this fixture

14 capacities extracted, 1 set aside as external (Rule 62(f), whose stay depends on state law), 13 scored, **0 candidates**. Median fan-out 3, maximum 6.

**None of that is a result about the Federal Rules.** A 28-provision fixture is too small to produce a rate, and a rate is not what this run is for. What it demonstrates is that the instrument runs end to end, that the external set-aside fires, and that fan-out is reported whether or not anyone asked.

The fan-out numbers are the point of comparison. A run over the full corpus with one similarity test doing both matcher jobs returned a median of twelve, a mean of twenty-one, a maximum of two hundred and nineteen, and one provision awarded as the pathway for sixty-seven unrelated capacities. At those numbers the zero-match cases invert: they stop being a structural fact about the corpus and become the capacities whose phrasing happened not to overlap with anything.

## What to expect when the corrected matcher meets the full corpus

**More candidates, not fewer.** The correction withdraws pathways that were awarded on vocabulary alone. That expectation is recorded here, in the specification, and in the paper, so that it cannot be adjusted after the fact.

Three of the previously returned seven were checked by hand and the obvious pathway was present in the extracted corpus and missed — Rule 22(a)(2) against Rule 13, Rule 23(a) against Rule 23(c)(1) and 23(g), Rule 18(b) against Rules 18(a) and 8(a). A further pair carried byte-identical quotes from adjacent chunks and were one norm counted twice. The deduplication in `extract_norms` addresses the second problem; the two-condition matcher addresses the first. Neither has been validated at scale.
