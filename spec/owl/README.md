# The OWL module

BFO 2020 conformant. Generated from `../../data/kernel.json` by `tools/build_owl.py`; do not edit by hand.

| File | What it is |
| --- | --- |
| `recognition-kernel.ttl` | the module, Turtle |
| `recognition-kernel.owl` | the same graph, RDF/XML, for Protégé and owlready2 |
| `bfo-stub.ttl` | bare declarations of the external terms, for offline reasoning only |
| `example-abox.ttl` | three artifacts and a sample of contradictions; must be **consistent** |
| `gating-violation.ttl` | a pragmatic contradiction in an act-empty artifact; must be **inconsistent** |
| `mask-violation.ttl` | a term incoherence at presenting facts; must be **inconsistent** |

## Verifying it

```bash
make validate        # locus mask, gating rule, and inferred classification
make bfo             # alignment to the real BFO, IAO and RO
```

The two are different checks and neither substitutes for the other.

`make validate` runs a reasoner over the module and the three ABoxes. Where BFO cannot be resolved it falls back to `bfo-stub.ttl`, which declares the external terms and asserts no BFO axiom. That fallback is necessary and is not a pass on conformance: an undeclared `obo:BFO_0000050` is not an error in OWL, so every restriction built on it goes inert, the gating axiom silently stops firing, and the run reports consistent for entirely the wrong reason. The validation report states which mode it ran in.

`make bfo` is what checks the alignment. A mistyped OBO identifier parses, serialises and reasons perfectly well; OWL simply mints a fresh class nobody has said anything about. So each external IRI is looked up in the real ontologies and its label compared against the registry in `kernel.json`, and a label mismatch is reported as loudly as a missing term, because referring to the right IRI under the wrong description is how a module ends up wired backwards while passing every structural check.

## What the module asserts

**Contradictions are information content entities**, continuant parts of the artifact bearing them. Not qualities: two printings of one code carry the same contradiction, so the entity is generically dependent rather than inhering in a material bearer.

**Locus is mereology.** A contradiction at the criteria locus is one that is `BFO_0000050 part of` a criteria specification. There is no `atLocus` relation and no crossing individual.

**Absence is absence of a part.** An artifact either has a specification part of a given kind or it does not. Nothing is minted to represent a link a system lacks.

**The locus mask and the gating rule are unsatisfiability axioms**, and they fail separately, which is why there are two negative tests.

**Named types are defined classes.** A reasoner classifies a modal clash part of a remedy specification as a repair failure without being told. A domain typology is a theorem of the product, and this is what that amounts to in practice.

**Conferred status is two-part**: a `ConferredStatusRole` inhering in the bearer, and a `StatusDeclaration` about it. `DeclarationWithoutBorneRole` exists to make a position statable rather than to be inferred, and nothing will classify there without a closure axiom. It is the configuration WHO occupies for ICD-11 Chapter 26.

## What is local, and why

Two properties are not imported.

`rk:prescribes` relates a directive information entity to the occurrent or realizable entity whose occurrence it directs. IAO has no relation of this shape. If one is adopted upstream, replace it and regenerate.

`rk:conferredBy` relates a role to the process in which it came to be borne.

Everything else uses BFO, IAO and RO terms. Three annotation properties (`rk:firingValue`, `rk:detectionInstrument`, `rk:operationalized`) carry claims that are not about the world: a firing value is a rate claim, and the middle value could turn out false without anything in the ontology being wrong.
