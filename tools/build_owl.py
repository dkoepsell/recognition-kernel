#!/usr/bin/env python3
"""Generate the BFO 2020 conformant OWL module from data/kernel.json.

    python tools/build_owl.py

Writes, into spec/owl/:

    recognition-kernel.ttl   the module, Turtle
    recognition-kernel.owl   the same graph, RDF/XML
    bfo-stub.ttl             bare declarations of the external terms

What the module asserts
-----------------------
A contradiction is an information content entity, a continuant part of the
artifact bearing it. Locus is mereology: a contradiction *at the criteria
locus* is one that is `part of` a criteria specification. There is no locus
relation and there are no crossing individuals, because `BFO_0000050` already
does the work.

Three things are made machine-checkable, and they fail separately:

1. The locus mask. A contradiction of a given class, part of a specification of
   a kind the mask excludes, is unsatisfiable.
2. The gating rule. A Stratum D contradiction part of an artifact with no act
   specification is unsatisfiable.
3. The named types. Each is a *defined* class, so a reasoner classifies a
   contradiction into it rather than looking the answer up.

The artifact body is the third of these that needs care. Because `part of` is
transitive, a contradiction part of a criteria specification is also part of
the artifact. "At the artifact body" therefore means part of the artifact and
part of no specification, which is exactly what the kernel's own definition of
the pseudo-locus says: the content considered apart from any chain link.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "data" / "kernel.json"
OUT_DIR = ROOT / "spec" / "owl"

BASE = "https://sool.davidkoepsell.com/ontology/rk"
OBO = "http://purl.obolibrary.org/obo/"

PREFIXES = """@prefix rk:   <https://sool.davidkoepsell.com/ontology/rk#> .
@prefix owl:  <http://www.w3.org/2002/07/owl#> .
@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix xsd:  <http://www.w3.org/2001/XMLSchema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dct:  <http://purl.org/dc/terms/> .
@prefix obo:  <http://purl.obolibrary.org/obo/> .
"""

#: The class each chain locus contributes. The artifact pseudo-locus is not a
#: specification and is handled separately.
SPEC_CLASS = {
    "authority": "AuthoritySpecification",
    "criteria": "CriteriaSpecification",
    "assessor": "AssessorSpecification",
    "facts": "FactsSpecification",
    "act": "ActSpecification",
    "effects": "EffectsSpecification",
    "remedy": "RemedySpecification",
}


def esc(text: str) -> str:
    """Escape a string for a Turtle triple-quoted literal."""
    return str(text).replace("\\", "\\\\").replace('"""', '\\"\\"\\"')


def camel(primitive_id: str) -> str:
    """K-A1 -> KA1, so the local name is a legal Turtle name."""
    return primitive_id.replace("-", "")


def at_locus(locus_id: str) -> str:
    """The class expression for 'part of a <locus>', as a Turtle blank node."""
    if locus_id == "artifact":
        # Part of the artifact, and part of no specification: the body of the
        # artifact considered apart from any chain link.
        return (
            "[ a owl:Class ; owl:intersectionOf (\n"
            "        [ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;\n"
            "          owl:someValuesFrom rk:Artifact ]\n"
            "        [ a owl:Class ; owl:complementOf\n"
            "          [ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;\n"
            "            owl:someValuesFrom rk:Specification ] ] ) ]"
        )
    return (
        "[ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;\n"
        f"          owl:someValuesFrom rk:{SPEC_CLASS[locus_id]} ]"
    )


def header(kernel: dict) -> str:
    return f"""{PREFIXES}
<{BASE}> a owl:Ontology ;
    dct:title "The Recognition Kernel"@en ;
    dct:description \"\"\"A domain-neutral kernel of twelve contradiction primitives in four strata, located by mereology over the seven links of a recognition chain. BFO 2020 conformant. Generated from data/kernel.json by tools/build_owl.py; do not edit by hand.

A contradiction is an information content entity, a continuant part of the artifact bearing it. A contradiction at the criteria locus is one that is part of a criteria specification: there is no locus-indexing relation and no crossing individual, because BFO_0000050 already does the work. An absent link is the absence of a part, never an individual carrying a status of 'absent'.

Three claims are machine-checkable and fail separately. The locus mask: a contradiction of a given class, part of a specification of a kind the mask excludes, is unsatisfiable. The gating rule: a Stratum D contradiction part of an artifact with no act specification is unsatisfiable. The named types: each is a defined class, so a reasoner classifies rather than looks up.\"\"\"@en ;
    dct:creator "David R. Koepsell" ;
    dct:license <https://creativecommons.org/licenses/by/4.0/> ;
    dct:source {json.dumps(kernel["source"])} ;
    owl:versionInfo "{kernel['kernel_version']}" ;
    owl:imports <http://purl.obolibrary.org/obo/bfo/2020/bfo.owl> ,
                <http://purl.obolibrary.org/obo/iao.owl> ,
                <http://purl.obolibrary.org/obo/ro.owl> .

# Where the imports cannot be resolved, load bfo-stub.ttl instead. That file
# declares these IRIs and asserts no BFO axiom, which keeps the module's own
# axioms checkable. It is not a pass on conformance: see spec/owl/README.md.
"""


def annotation_properties() -> str:
    return """
#################################################################
#    Annotation properties
#
#    These carry claims that are not about the world. A firing value is a rate
#    claim, and the middle value of the gate is an empirical claim that could
#    turn out false without anything in the ontology being wrong. They are
#    therefore annotations and never axioms.
#################################################################

rk:firingValue a owl:AnnotationProperty ;
    rdfs:label "firing value"@en ;
    rdfs:comment "fires, rare, cannot_fire, no_locus or not_applicable. A prediction about what can occur, not a detection of what has."@en .

rk:detectionInstrument a owl:AnnotationProperty ;
    rdfs:label "detection instrument"@en .

rk:operationalized a owl:AnnotationProperty ;
    rdfs:label "operationalized"@en .

rk:wellFormednessRationale a owl:AnnotationProperty ;
    rdfs:label "well-formedness rationale"@en .
"""


def object_properties() -> str:
    return """
#################################################################
#    Object properties
#
#    Two are local because nothing upstream has their shape. Everything else
#    the module uses is a BFO, IAO or RO term.
#################################################################

rk:prescribes a owl:ObjectProperty ;
    rdfs:label "prescribes"@en ;
    rdfs:domain obo:IAO_0000033 ;
    rdfs:range [ a owl:Class ; owl:unionOf ( obo:BFO_0000003 obo:BFO_0000017 ) ] ;
    rdfs:comment "Relates a directive information entity to the occurrent or realizable entity whose occurrence it directs. IAO has no relation of this shape. If one is adopted upstream, replace it and regenerate."@en .

rk:conferredBy a owl:ObjectProperty ;
    rdfs:label "conferred by"@en ;
    rdfs:domain rk:ConferredStatusRole ;
    rdfs:range rk:RecognitionAct ;
    rdfs:comment "Relates a role to the process in which it came to be borne."@en .
"""


def upper_classes() -> str:
    return """
#################################################################
#    The artifact and its specification parts
#################################################################

rk:Artifact a owl:Class ;
    rdfs:subClassOf obo:IAO_0000030 ;
    rdfs:label "recognition artifact"@en ;
    obo:IAO_0000115 "An information content entity that constitutes, in whole or in part, a system of recognition: a code, a standard, a rule set, an ontology."@en .

rk:Specification a owl:Class ;
    rdfs:subClassOf obo:IAO_0000033 ;
    rdfs:label "chain specification"@en ;
    obo:IAO_0000115 "A directive information entity that is part of a recognition artifact and supplies one link of its chain."@en .

rk:ActEmptyArtifact a owl:Class ;
    rdfs:label "act-empty artifact"@en ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        rk:Artifact
        [ a owl:Class ; owl:complementOf
          [ a owl:Restriction ; owl:onProperty obo:BFO_0000051 ;
            owl:someValuesFrom rk:ActSpecification ] ] ) ] ;
    obo:IAO_0000115 "A recognition artifact with no act specification part. Typing an individual here is a closure assertion: OWL will not conclude the absence of a part on its own."@en .

#################################################################
#    Conferred status, in two parts
#
#    A role alone asserts that something inheres in the bearer. A generically
#    dependent continuant alone gives no bearer for the assertion to be made or
#    withheld about. Only the two-part model can represent a system that
#    records and mandates a status while declining to assert that anything
#    inheres in anyone, which is WHO's stated position on ICD-11 Chapter 26.
#################################################################

rk:RecognitionAct a owl:Class ;
    rdfs:subClassOf obo:BFO_0000015 ;
    rdfs:label "recognition act"@en ;
    obo:IAO_0000115 "A process in which criteria are applied to facts and a status is conferred."@en .

rk:ConferredStatusRole a owl:Class ;
    rdfs:subClassOf obo:BFO_0000023 ,
        [ a owl:Restriction ; owl:onProperty obo:RO_0000052 ;
          owl:someValuesFrom obo:BFO_0000004 ] ;
    rdfs:label "conferred status role"@en ;
    obo:IAO_0000115 "A role borne by an entity in virtue of a recognition act. Every such role is characteristic of some independent continuant: that is what having a bearer amounts to, and it is precisely what a status declaration does not assert."@en .

rk:StatusDeclaration a owl:Class ;
    rdfs:subClassOf obo:IAO_0000030 ;
    rdfs:label "status declaration"@en ;
    obo:IAO_0000115 "An information content entity that is about a conferred status role."@en .

rk:DeclarationWithoutBorneRole a owl:Class ;
    rdfs:label "declaration without borne role"@en ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        rk:StatusDeclaration
        [ a owl:Class ; owl:complementOf
          [ a owl:Restriction ; owl:onProperty obo:IAO_0000136 ;
            owl:someValuesFrom rk:ConferredStatusRole ] ] ) ] ;
    obo:IAO_0000115 "A status declaration that is about no borne role. This class exists to make a position statable, not to be inferred: nothing will classify here without a closure axiom."@en .
"""


def specification_classes(kernel: dict) -> str:
    lines = ["""
#################################################################
#    One specification class per chain link
#################################################################
"""]
    names = []
    for locus in kernel["loci"]:
        if locus.get("pseudo_locus"):
            continue
        cls = SPEC_CLASS[locus["id"]]
        names.append(f"rk:{cls}")
        lines.append(
            f"""rk:{cls} a owl:Class ;
    rdfs:subClassOf rk:Specification ;
    rdfs:label "{esc(locus['label'])}"@en ;
    obo:IAO_0000115 \"\"\"{esc(locus['definition'])}\"\"\"@en .
"""
        )
    lines.append(
        "[] a owl:AllDisjointClasses ;\n"
        f"    owl:members ( {' '.join(names)} ) .\n"
    )
    return "\n".join(lines)


def stratum_and_primitive_classes(kernel: dict) -> str:
    lines = ["""
#################################################################
#    Contradictions: the four strata and the twelve primitives
#################################################################

rk:Contradiction a owl:Class ;
    rdfs:subClassOf obo:IAO_0000030 ;
    rdfs:label "structural contradiction"@en ;
    obo:IAO_0000115 "An information content entity that is a continuant part of a recognition artifact and constitutes a structural defect in it. Not a quality: two printings of one code carry the same contradiction, so the entity is generically dependent rather than inhering in a material bearer."@en .
"""]

    stratum_names = []
    for stratum in kernel["strata"]:
        cls = f"Stratum{stratum['id']}Contradiction"
        stratum_names.append(f"rk:{cls}")
        gated = "true" if stratum.get("gated") else "false"
        lines.append(
            f"""rk:{cls} a owl:Class ;
    rdfs:subClassOf rk:Contradiction ;
    rdfs:label "{esc(stratum['label'])}"@en ;
    skos:note "precondition: {esc(stratum['precondition'])}; gated: {gated}"@en ;
    obo:IAO_0000115 \"\"\"{esc(stratum['definition'])}\"\"\"@en .
"""
        )
    lines.append(
        "[] a owl:AllDisjointClasses ;\n"
        f"    owl:members ( {' '.join(stratum_names)} ) .\n"
    )

    primitive_names = []
    for primitive in kernel["primitives"]:
        cls = camel(primitive["id"])
        primitive_names.append(f"rk:{cls}")
        source = esc(
            "; ".join(primitive.get("precedents") or []) or kernel["source"]
        )
        lines.append(
            f"""rk:{cls} a owl:Class ;
    rdfs:subClassOf rk:Stratum{primitive['stratum']}Contradiction ;
    rdfs:label "{esc(primitive['name'])}"@en ;
    skos:notation "{primitive['id']}" ;
    obo:IAO_0000115 \"\"\"{esc(primitive['definition'])}\"\"\"@en ;
    obo:IAO_0000119 \"\"\"{source}\"\"\"@en ;
    skos:note \"\"\"formal signature: {esc(primitive['formal_signature'])}\"\"\"@en ;
    rk:wellFormednessRationale \"\"\"{esc(primitive['well_formedness_rationale'])}\"\"\"@en ;
    rk:detectionInstrument "{esc(primitive.get('instrument') or 'none')}" ;
    rk:operationalized "{esc(primitive.get('operationalized', False))}" .
"""
        )
    lines.append(
        "[] a owl:AllDisjointClasses ;\n"
        f"    owl:members ( {' '.join(primitive_names)} ) .\n"
    )
    return "\n".join(lines)


def locus_mask_axioms(kernel: dict) -> str:
    """Every excluded coordinate becomes an unsatisfiability axiom."""
    lines = ["""
#################################################################
#    The locus mask
#
#    A contradiction of a given class, part of a specification of a kind the
#    mask excludes, is unsatisfiable. This is one of the two negative tests:
#    spec/owl/mask-violation.ttl must make the ontology inconsistent.
#################################################################
"""]
    count = 0
    for primitive in kernel["primitives"]:
        cls = camel(primitive["id"])
        for locus_id in primitive.get("excluded_at") or []:
            count += 1
            lines.append(
                f"""# {primitive['id']} is not well-formed at {locus_id}.
[ a owl:Class ; owl:intersectionOf (
        rk:{cls}
        {at_locus(locus_id)} ) ]
    rdfs:subClassOf owl:Nothing .
"""
            )
    lines.insert(1, f"# {count} excluded coordinates.\n")
    return "\n".join(lines)


def gating_axiom() -> str:
    return """
#################################################################
#    The gating rule
#
#    Stratum D presupposes acts. A pragmatic contradiction part of an artifact
#    with no act specification is unsatisfiable. This is the other negative
#    test: spec/owl/gating-violation.ttl must make the ontology inconsistent.
#
#    The two negative tests fail separately, which is why there are two.
#################################################################

[ a owl:Class ; owl:intersectionOf (
        rk:StratumDContradiction
        [ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;
          owl:someValuesFrom rk:ActEmptyArtifact ] ) ]
    rdfs:subClassOf owl:Nothing .
"""


def kind_class(system_kind: str) -> str:
    """reference_ontology -> rk:ReferenceOntology."""
    return "".join(part.capitalize() for part in str(system_kind).split("_"))


def artifact_kind_classes(kernel: dict) -> str:
    """One artifact subclass per system kind.

    These are load-bearing, not decorative. K-B1 at the criteria locus is a
    Temporal Contradiction in a legal order and a Criterion Circularity in a
    classification. Without the kind in the definition, the two named types
    would be equivalent by construction and a reasoner would say so.
    """
    kinds = sorted({
        named["system_kind"]
        for named in kernel.get("named_types") or []
        if named.get("system_kind")
    })
    lines = ["""
#################################################################
#    Artifact kinds
#
#    The same coordinates carry different names in different kinds of system,
#    so the kind is part of what a named type is defined by.
#################################################################
"""]
    names = []
    for kind in kinds:
        cls = kind_class(kind)
        names.append(f"rk:{cls}")
        lines.append(
            f"""rk:{cls} a owl:Class ;
    rdfs:subClassOf rk:Artifact ;
    rdfs:label "{esc(kind.replace('_', ' '))}"@en ;
    skos:notation "{esc(kind)}" .
"""
        )
    if len(names) > 1:
        lines.append(
            "[] a owl:AllDisjointClasses ;\n"
            f"    owl:members ( {' '.join(names)} ) .\n"
        )
    return "\n".join(lines)


def named_type_axioms(kernel: dict) -> str:
    """Named types are defined classes, so the reasoner classifies into them."""
    lines = ["""
#################################################################
#    The named types
#
#    Each is a defined class: a reasoner classifies a modal clash part of a
#    remedy specification, in a legal order, as a repair failure without being
#    told. A domain typology is a theorem of the product, and this is what that
#    amounts to in practice.
#
#    The kind is part of the definition. K-B1 at criteria is a Temporal
#    Contradiction in a legal order and a Criterion Circularity in a
#    classification; omitting the kind would make those two classes equivalent.
#################################################################
"""]
    for named in kernel.get("named_types") or []:
        key = named.get("key")
        primitive = named.get("primitive")
        locus_id = named.get("locus")
        kind = named.get("system_kind")
        if not (key and primitive and locus_id):
            continue
        cls = "".join(
            part for part in str(named.get("label") or key).replace("/", " ").split()
        ).replace("-", "")
        source = esc(named.get("source") or kernel["source"])
        in_kind = (
            f"""
        [ a owl:Restriction ; owl:onProperty obo:BFO_0000050 ;
          owl:someValuesFrom rk:{kind_class(kind)} ]"""
            if kind
            else ""
        )
        lines.append(
            f"""rk:{cls} a owl:Class ;
    rdfs:subClassOf rk:Contradiction ;
    rdfs:label "{esc(named.get('label') or key)}"@en ;
    skos:notation "{esc(key)}" ;
    obo:IAO_0000115 "{esc(primitive)} located at the {esc(locus_id)} locus{f' in a {esc(str(kind).replace("_", " "))}' if kind else ''}."@en ;
    obo:IAO_0000119 \"\"\"{source}\"\"\"@en ;
    owl:equivalentClass [ a owl:Class ; owl:intersectionOf (
        rk:{camel(primitive)}
        {at_locus(locus_id)}{in_kind} ) ] .
"""
        )
    return "\n".join(lines)


def build_stub(kernel: dict) -> str:
    """Bare declarations of the external terms, for offline reasoning only."""
    terms = kernel["bfo"]["external_terms"]
    lines = [
        PREFIXES,
        f"""
<{BASE}/bfo-stub> a owl:Ontology ;
    rdfs:label "BFO stub"@en ;
    rdfs:comment \"\"\"Bare declarations of the external terms the module references, for
reasoning in environments where the real imports cannot be resolved.

This file asserts no BFO axiom. It exists so the module's own axioms stay
checkable, and it is NOT a pass on conformance: an undeclared obo:BFO_0000050
is not an error in OWL, so every restriction built on it would go inert and a
run could report consistent for entirely the wrong reason. Any validation
report produced against this file must say so. Use tools/check_bfo.py to check
the alignment itself.\"\"\"@en .
""",
    ]
    for iri, label in terms.items():
        kind = "owl:ObjectProperty" if iri.startswith(("BFO_000005", "RO_")) else None
        if iri in ("IAO_0000115", "IAO_0000119"):
            kind = "owl:AnnotationProperty"
        elif iri == "IAO_0000136":
            kind = "owl:ObjectProperty"
        elif kind is None:
            kind = "owl:Class"
        lines.append(f'obo:{iri} a {kind} ; rdfs:label "{esc(label)}"@en .')
    return "\n".join(lines) + "\n"


def main() -> int:
    kernel = json.loads(KERNEL.read_text(encoding="utf-8"))
    if "bfo" not in kernel:
        raise SystemExit("data/kernel.json has no 'bfo' block; cannot build the module")

    module = "".join(
        [
            header(kernel),
            annotation_properties(),
            object_properties(),
            upper_classes(),
            specification_classes(kernel),
            stratum_and_primitive_classes(kernel),
            artifact_kind_classes(kernel),
            locus_mask_axioms(kernel),
            gating_axiom(),
            named_type_axioms(kernel),
        ]
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ttl = OUT_DIR / "recognition-kernel.ttl"
    ttl.write_text(module, encoding="utf-8")
    print(f"wrote {ttl.relative_to(ROOT)}")

    stub = OUT_DIR / "bfo-stub.ttl"
    stub.write_text(build_stub(kernel), encoding="utf-8")
    print(f"wrote {stub.relative_to(ROOT)}")

    try:
        from rdflib import Graph
    except ImportError:
        print("rdflib not installed; skipped the RDF/XML serialisation")
        return 0

    graph = Graph()
    graph.parse(str(ttl), format="turtle")
    owl = OUT_DIR / "recognition-kernel.owl"
    graph.serialize(destination=str(owl), format="xml")
    print(f"wrote {owl.relative_to(ROOT)} ({len(graph)} triples)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
