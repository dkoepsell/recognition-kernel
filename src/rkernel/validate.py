"""Validation: the kernel, the schemas, and the OWL module must agree.

Five checks, each of which can fail independently:

1. **Kernel self-check.** Every primitive assigns every locus to exactly one of
   well_formed_at or excluded_at; every named type sits at a well-formed
   crossing.
2. **Schema validation.** kernel.json validates against kernel.schema.json, and
   every bundled chain against chain.schema.json.
3. **OWL agreement.** The locus mask asserted in the OWL module is the locus
   mask in kernel.json, primitive for primitive.
4. **Reasoning.** The example ABox is consistent; the gating-violation and
   mask-violation files are each inconsistent. The two negative tests are the
   load-bearing ones and they fail separately, because the gating rule can go
   inert while the locus mask still fires, and the reverse.
5. **Inference.** The named types are derived by a reasoner from the example
   ABox rather than looked up. If nothing classifies, a domain typology is not
   in fact a theorem of the product.

Checks 2-5 degrade gracefully when jsonschema, rdflib, or a reasoner is absent,
and say so rather than passing silently.

Reasoning needs the external terms declared. An undeclared obo:BFO_0000050 is
not an error in OWL, so every restriction built on it goes inert and both
negative tests pass vacuously. The reasoning check therefore loads either the
real ontologies (set RK_BFO_DIR) or spec/owl/bfo-stub.ttl, and reports which.
Whether those IRIs mean what the module claims is a separate question, answered
by tools/check_bfo.py.
"""

from __future__ import annotations

import json
from pathlib import Path

from .kernel import Kernel, default_kernel_path, load_kernel


def _root() -> Path:
    """Locate the repository root: the nearest ancestor holding `spec/schema`.

    When the package is installed, `kernel.json` resolves to the copy under
    `src/rkernel/data/`, whose parent is not the repository. Walking up for the
    spec directory finds the root in both layouts, and returns a path that
    simply does not exist when the package is installed standalone without the
    spec, which the checks below report as a skip rather than a failure.
    """
    for candidate in [Path.cwd(), *Path(__file__).resolve().parents]:
        if (candidate / "spec" / "schema").is_dir():
            return candidate
    return default_kernel_path().parent.parent


def check_kernel(kernel: Kernel) -> dict:
    problems = kernel.self_check()
    chain_loci = [locus.id for locus in kernel.chain_loci]
    return {
        "name": "kernel self-check",
        "ok": not problems,
        "problems": problems,
        "primitives": len(kernel.primitives),
        "loci": len(kernel.loci),
        "chain_loci": len(chain_loci),
        "well_formed_over_chain_loci": kernel.well_formed_cells(chain_loci),
        "cells_over_chain_loci": len(kernel.primitives) * len(chain_loci),
    }


def check_schemas(kernel_path: Path | None = None) -> dict:
    try:
        import jsonschema
    except ImportError:
        return {"name": "schema validation", "ok": None, "skipped": "jsonschema not installed"}

    root = _root()
    if not (root / "spec" / "schema").is_dir():
        return {
            "name": "schema validation",
            "ok": None,
            "skipped": "spec/ not present; run from a checkout of the repository",
        }
    problems: list[str] = []
    checked = 0

    pairs: list[tuple[Path, Path]] = [
        (kernel_path or default_kernel_path(), root / "spec" / "schema" / "kernel.schema.json")
    ]
    chain_schema = root / "spec" / "schema" / "chain.schema.json"
    for chain_file in sorted((root / "examples").rglob("*.chain.json")):
        pairs.append((chain_file, chain_schema))

    for instance_path, schema_path in pairs:
        if not instance_path.is_file() or not schema_path.is_file():
            problems.append(f"missing file: {instance_path} or {schema_path}")
            continue
        with instance_path.open(encoding="utf-8") as handle:
            instance = json.load(handle)
        with schema_path.open(encoding="utf-8") as handle:
            schema = json.load(handle)
        instance.pop("$schema", None)
        try:
            jsonschema.validate(instance, schema)
            checked += 1
        except jsonschema.ValidationError as error:
            problems.append(f"{instance_path.name}: {error.message} at {list(error.path)}")

    return {
        "name": "schema validation",
        "ok": not problems,
        "validated": checked,
        "problems": problems,
    }


def check_owl_agreement(kernel: Kernel) -> dict:
    try:
        from rdflib import Graph, Namespace, RDFS
    except ImportError:
        return {"name": "OWL agreement", "ok": None, "skipped": "rdflib not installed"}

    ttl = _root() / "spec" / "owl" / "recognition-kernel.ttl"
    if not ttl.is_file():
        return {
            "name": "OWL agreement",
            "ok": None,
            "skipped": "spec/owl/ not present; run from a checkout, or run tools/build_owl.py",
        }

    graph = Graph()
    graph.parse(ttl, format="turtle")
    RK = Namespace("https://sool.davidkoepsell.com/ontology/rk#")

    # Locus is mereology, so an exclusion is an unsatisfiable intersection of a
    # primitive class with 'part of some <kind of specification>'. The artifact
    # pseudo-locus is the one case with no specification class: it is part of
    # an artifact and part of no specification, so it is matched separately.
    chain_query = """
    SELECT ?p ?spec WHERE {
      ?axiom rdfs:subClassOf owl:Nothing ;
             owl:intersectionOf ?list .
      ?list rdf:rest*/rdf:first ?p .
      ?p a owl:Class .
      FILTER(isIRI(?p))
      ?list rdf:rest*/rdf:first ?r .
      ?r owl:onProperty obo:BFO_0000050 ; owl:someValuesFrom ?spec .
      ?spec rdfs:subClassOf rk:Specification .
    }
    """
    artifact_query = """
    SELECT ?p WHERE {
      ?axiom rdfs:subClassOf owl:Nothing ;
             owl:intersectionOf ?list .
      ?list rdf:rest*/rdf:first ?p .
      ?p a owl:Class .
      FILTER(isIRI(?p))
      ?list rdf:rest*/rdf:first ?body .
      ?body owl:intersectionOf ?inner .
      ?inner rdf:rest*/rdf:first ?r .
      ?r owl:onProperty obo:BFO_0000050 ; owl:someValuesFrom rk:Artifact .
    }
    """
    local = lambda iri: str(iri).split("#")[-1]  # noqa: E731
    owl_exclusions = {
        (local(primitive), local(spec)) for primitive, spec in graph.query(chain_query)
    }
    owl_exclusions |= {
        (local(primitive), "Artifact") for (primitive,) in graph.query(artifact_query)
    }

    def owl_name(primitive_id: str) -> str:
        return primitive_id.replace("-", "")

    def owl_locus(locus_id: str) -> str:
        if locus_id == "artifact":
            return "Artifact"
        return "".join(word.capitalize() for word in locus_id.split("_")) + "Specification"

    expected = {
        (owl_name(primitive.id), owl_locus(locus_id))
        for primitive in kernel.primitives
        for locus_id in primitive.excluded_at
    }

    missing = sorted(expected - owl_exclusions)
    extra = sorted(owl_exclusions - expected)
    return {
        "name": "OWL agreement",
        "ok": not missing and not extra,
        "exclusions_in_kernel": len(expected),
        "exclusions_in_owl": len(owl_exclusions),
        "missing_from_owl": missing,
        "not_in_kernel": extra,
    }


def check_reasoning() -> dict:
    """Consistency of the ABox, inconsistency of the gating violation."""
    try:
        import owlready2
    except ImportError:
        return {"name": "reasoning", "ok": None, "skipped": "owlready2 not installed"}

    owl_dir = _root() / "spec" / "owl"
    rdfxml = owl_dir / "recognition-kernel.owl"
    if not rdfxml.is_file():
        return {
            "name": "reasoning",
            "ok": None,
            "skipped": "recognition-kernel.owl not built; run tools/build_owl.py",
        }

    results: dict[str, object] = {"name": "reasoning"}
    problems: list[str] = []

    support, mode = _external_support(owl_dir)
    results["external_terms"] = mode
    if not support:
        problems.append(
            "no external declarations available; every restriction on obo: terms "
            "would go inert and the negative tests would pass vacuously"
        )

    for label, abox, expect_consistent in (
        ("example-abox", owl_dir / "example-abox.ttl", True),
        ("gating-violation", owl_dir / "gating-violation.ttl", False),
        ("mask-violation", owl_dir / "mask-violation.ttl", False),
    ):
        if not abox.is_file():
            problems.append(f"{label}: {abox.name} is missing")
            continue
        consistent = _is_consistent(rdfxml, abox, support)
        results[label] = (
            "unavailable" if consistent is None
            else "consistent" if consistent else "inconsistent"
        )
        if consistent is None:
            problems.append(f"{label}: reasoner unavailable")
        elif consistent != expect_consistent:
            problems.append(
                f"{label}: expected {'consistent' if expect_consistent else 'inconsistent'}, "
                f"got {'consistent' if consistent else 'inconsistent'}"
            )

    results["ok"] = not problems
    results["problems"] = problems
    results["note"] = (
        "Two negative tests, and they must fail separately. gating-violation asserts a "
        "pragmatic contradiction in an act-empty artifact; mask-violation asserts a term "
        "incoherence at presenting facts. Either can go inert while the other still "
        "fires, so one test would not catch both. "
        + (
            "Resolved against the real BFO, IAO and RO."
            if mode == "imported"
            else "Ran against bfo-stub.ttl, which declares the external terms and asserts "
            "no BFO axiom. That keeps this module's own axioms checkable, but a "
            "consistency verdict reached without BFO's axioms present is a weaker claim "
            "than it appears. Run `make bfo` to check the alignment itself."
        )
    )
    return results


def check_inference(kernel: Kernel) -> dict:
    """The named types must be derived, not looked up.

    The example ABox asserts only that a contradiction is a primitive, part of
    a specification of some kind, in an artifact of some kind. It never states
    a named type. If a reasoner classifies those individuals into named types
    anyway, the claim that a domain typology is a theorem of the product is
    being made good on. If it derives nothing, the typology is a lookup table
    with a reasoner bolted to the side.
    """
    try:
        import owlready2
        from rdflib import Graph, URIRef
    except ImportError:
        return {"name": "inference", "ok": None, "skipped": "owlready2 or rdflib not installed"}

    import tempfile

    owl_dir = _root() / "spec" / "owl"
    rdfxml = owl_dir / "recognition-kernel.owl"
    abox = owl_dir / "example-abox.ttl"
    if not rdfxml.is_file() or not abox.is_file():
        return {"name": "inference", "ok": None, "skipped": "module or example ABox not built"}

    support, mode = _external_support(owl_dir)
    named_keys = {named.key for named in kernel.named_types}

    graph = Graph()
    graph.parse(rdfxml, format="xml")
    for path in support:
        graph.parse(path, format="turtle")
    graph.parse(abox, format="turtle")
    graph.remove((None, URIRef("http://www.w3.org/2002/07/owl#imports"), None))

    with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as handle:
        merged = Path(handle.name)
    graph.serialize(destination=merged, format="xml")

    derived: dict[str, list[str]] = {}
    try:
        world = owlready2.World()
        onto = world.get_ontology(merged.as_uri()).load()

        # Snapshot what was asserted before reasoning. sync_reasoner writes
        # inferred parents back into is_a, so reading it afterwards would show
        # every derived class as though it had been stated all along, and the
        # check would report nothing gained no matter what the reasoner did.
        asserted_by_name = {
            individual.name: {c.name for c in individual.is_a if hasattr(c, "name")}
            for individual in onto.individuals()
        }

        with onto:
            owlready2.sync_reasoner(world, infer_property_values=False, debug=0)

        for individual in onto.individuals():
            asserted = asserted_by_name.get(individual.name, set())
            inferred = {
                parent.name
                for parent in individual.INDIRECT_is_a
                if hasattr(parent, "name")
            }
            gained = sorted(
                name for name in inferred - asserted if _is_named_type(name, kernel)
            )
            if gained:
                derived[individual.name] = gained
    except owlready2.OwlReadyInconsistentOntologyError:
        return {
            "name": "inference",
            "ok": False,
            "problems": ["example ABox is inconsistent; cannot test inference"],
        }
    except Exception as error:  # pragma: no cover - reasoner or java missing
        return {"name": "inference", "ok": None, "skipped": f"reasoner unavailable: {error}"}
    finally:
        merged.unlink(missing_ok=True)

    problems = []
    if not derived:
        problems.append(
            "no individual was classified into any named type; the named types are "
            "being looked up rather than inferred"
        )
    return {
        "name": "inference",
        "ok": not problems,
        "external_terms": mode,
        "named_types_available": len(named_keys),
        "individuals_classified": derived,
        "problems": problems,
        "note": (
            "The example ABox never states a named type. Every classification listed "
            "above was derived by the reasoner from a primitive, a specification part "
            "and an artifact kind."
        ),
    }


def _is_named_type(class_name: str, kernel: Kernel) -> bool:
    """True if `class_name` is one of the kernel's named types.

    Matches on the generated class name, which build_owl.py derives from the
    named type's label.
    """
    for named in kernel.named_types:
        generated = "".join(
            part for part in str(named.label or named.key).replace("/", " ").split()
        ).replace("-", "")
        if generated == class_name:
            return True
    return False


def _external_support(owl_dir: Path) -> tuple[list[Path], str]:
    """The external declarations to reason with, and which mode that is.

    Uses the real ontologies when RK_BFO_DIR points at them, and bfo-stub.ttl
    otherwise. The stub is the default deliberately: reasoning over BFO, IAO
    and RO together takes minutes, and what these three ABoxes test is whether
    *this module's* axioms fire, which the stub is sufficient for. Whether the
    IRIs mean what the module claims is a different question, and
    tools/check_bfo.py is where it gets answered.

    The network is never tried here. A validation run should not depend on it.
    """
    import os

    configured = os.environ.get("RK_BFO_DIR")
    if configured:
        vendor = Path(configured)
        if vendor.is_dir():
            files = sorted(
                path
                for pattern in ("*.ttl", "*.owl", "*.rdf")
                for path in vendor.glob(pattern)
            )
            if files:
                return files, "imported"
    stub = owl_dir / "bfo-stub.ttl"
    if stub.is_file():
        return [stub], "stub"
    return [], "none"


def _is_consistent(
    tbox_path: Path, abox_path: Path, support: list[Path] | None = None
) -> bool | None:
    """Merge TBox, supporting declarations and ABox, then run HermiT.

    `support` carries the external declarations. Passing nothing is not a
    neutral choice: an undeclared obo:BFO_0000050 is not an error in OWL, so
    every restriction built on it goes inert and both negative tests come back
    consistent for entirely the wrong reason. Callers must supply either the
    real ontologies or bfo-stub.ttl.
    """
    import tempfile

    try:
        from rdflib import Graph, URIRef
        import owlready2
    except ImportError:  # pragma: no cover
        return None

    graph = Graph()
    graph.parse(tbox_path, format="xml")
    for path in support or []:
        graph.parse(path, format="turtle")
    graph.parse(abox_path, format="turtle")
    # owlready2 chokes on owl:imports it cannot resolve; everything the module
    # needs has already been merged into this graph by hand.
    graph.remove((None, URIRef("http://www.w3.org/2002/07/owl#imports"), None))

    with tempfile.NamedTemporaryFile(suffix=".owl", delete=False) as handle:
        merged = Path(handle.name)
    graph.serialize(destination=merged, format="xml")

    world = owlready2.World()
    try:
        onto = world.get_ontology(merged.as_uri()).load()
        with onto:
            owlready2.sync_reasoner(world, infer_property_values=False, debug=0)
        return True
    except owlready2.OwlReadyInconsistentOntologyError:
        return False
    except Exception:  # pragma: no cover - reasoner or java missing
        return None
    finally:
        merged.unlink(missing_ok=True)


def run_all(kernel_path: str | Path | None = None) -> dict:
    kernel = load_kernel(kernel_path)
    checks = [
        check_kernel(kernel),
        check_schemas(Path(kernel_path) if kernel_path else None),
        check_owl_agreement(kernel),
        check_reasoning(),
        check_inference(kernel),
    ]
    ok = all(check["ok"] is not False for check in checks)

    lines = ["# Validation report", ""]
    for check in checks:
        if check["ok"] is None:
            mark = "skipped"
        elif check["ok"]:
            mark = "pass"
        else:
            mark = "FAIL"
        lines.append(f"- **{check['name']}**: {mark}")
        for key, value in check.items():
            if key in ("name", "ok") or not value:
                continue
            lines.append(f"    - {key}: {value}")
    lines.append("")
    lines.append(
        f"Kernel {kernel.kernel_version}: {len(kernel.primitives)} primitives over "
        f"{len(kernel.chain_loci)} chain loci plus the artifact body."
    )

    return {"ok": ok, "checks": checks, "markdown": "\n".join(lines)}
