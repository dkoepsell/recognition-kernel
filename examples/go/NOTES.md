# Worked example 3 — Gene Ontology

**Cell 1 of the registered design. Act-empty, repair-absent. The reference-ontology case.**

```bash
rkernel typology examples/go/go.chain.json
rkernel extract  examples/go/corpus/go_demo.json
rkernel detect   examples/go/corpus/go_demo.json
```

## The chain: every link absent

This is the assignment most likely to be misread, so the reasoning is spelled out link by link in the chain file itself. The short version: **curatorial governance of a description is not a source of authority in the sense the chain requires.**

The GO Consortium curates the ontology, and does so with more rigour than most institutions manage. But the ontology does not confer on anyone an entitlement to fix criteria by which statuses are conferred on cases. No curator is licensed by GO to decide anything about anyone. Term obsoletion is curation, not repair of a conferral, because there is no conferral to revisit.

Collapsing that distinction would convert every scientific ontology into an institution, and the framework would lose the only contrast that makes it say anything.

The `criteria` link carries `status: absent` with `specification: internal`. GO does define its terms, thickly and well. What it does not do is apply them to a case. The pair of values makes the reference-ontology row legible: heavy definitional content, no chain.

## What the generator produces

Nine crossings fire — the nine ungated primitives at the artifact body. Stratum D is `cannot_fire` at every locus.

**That is not a clean bill of health.** It is a diagnosis of kind. An empty pragmatic stratum reports that the artifact describes or classifies but does not decide, which is as uninformative about quality as observing that a map has no moving parts. Reading it as a passed audit is the natural error and the wrong one.

And the nine that do fire matter. A reference ontology can be as inconsistent, as circular, and as category-violating as a legal code, because those failures need only a body of definitions and assertions. The A, B and C columns are constant across all four cells for exactly this reason.

## Why the ontology-evaluation literature has no pragmatic category

OntoClean, OOPS!, and the OntoUML anti-pattern catalogues have no Stratum D. On this account that is not an oversight: **their objects occupy this row, where Stratum D cannot fire by construction.** Those instruments are complete for the systems they were built to evaluate, and on the ground they cover they are better than anything here.

The gap opens only when instruments built for row one are applied to objects in rows two through four. That is the whole diagnosis, stated structurally.

Every Stratum C primitive in this kernel has a more developed treatment in OntoClean or in the anti-pattern catalogue, and OOPS! detects a wider range of real defects in real ontologies than anything implemented here. The right relationship is location, not competition: OntoClean occupies Stratum C almost entirely, the anti-patterns occupy Stratum C with UFO-specific refinements, and OOPS! spans A, B and C plus a body of engineering-practice concerns this kernel does not address and should not be asked to. Implementing the kernel as OOPS!-style checks, or as an extension of the anti-pattern catalogue into Stratum D, would be a better outcome than a competing tool.

## The corpus

`corpus/go_demo.json` is a **prose rendering** of `is_a` and `part_of` edges from a small GO fragment, written so the entity-relation extractor has surface forms to match. GO is distributed as OBO and OWL, not as prose. Definitions are paraphrased, not quoted. GO content is released by the Gene Ontology Consortium under CC BY 4.0 and is used here with attribution.

## The extractor pair, reversed

| Extractor | Target schema | Yield | Errors |
| --- | --- | --- | --- |
| Entity-relation | ontological claims | 25 | 0 |
| Norm tuple | deontic norms | 0 | 0 |

Exactly the inverse of the FRCP run. Neither instrument is the better one; each is built for a different kind of structure. Running both over both corpora is what turns the precondition claim from an explanation into a demonstration.

## K-D3 here

**0 capacities extracted, so nothing to detect.**

This is the predicted result and it is not a null finding. The detector had nothing to run on because the system confers no capacities, and the tool says so in its own output rather than reporting a zero that could be mistaken for a measurement. If Stratum D ever fires in this cell, the gating rule is false.
