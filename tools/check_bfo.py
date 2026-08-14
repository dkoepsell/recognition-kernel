#!/usr/bin/env python3
"""Verify that every external IRI the module uses is declared upstream.

    python tools/check_bfo.py                       # resolve imports over the network
    python tools/check_bfo.py --local vendor/bfo    # resolve from a directory of ontologies

Why this exists
---------------
A mistyped OBO identifier does not fail. `obo:BFO_0000123` parses, serialises,
and reasons perfectly well; OWL simply treats it as a fresh class nobody has
said anything about. An ontology can therefore claim an alignment to BFO while
referring to terms BFO does not contain, and every reasoner in the pipeline will
report success.

So the alignment has to be checked as a separate act. For each external IRI the
module references, this script asks whether the imported ontologies declare it
as a class, an object property, or an annotation property, and whether the label
recorded in `data/kernel.json` matches the label upstream. A label mismatch is
reported as loudly as a missing term, because referring to the right IRI under
the wrong description is how a module comes to be wired up backwards while
passing every structural check.

The network is not available in every environment. Pass `--local` with a
directory containing bfo.owl, iao.owl and ro.owl, or set RK_BFO_DIR.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERNEL = ROOT / "data" / "kernel.json"
MODULE = ROOT / "spec" / "owl" / "recognition-kernel.ttl"

OBO = "http://purl.obolibrary.org/obo/"

REMOTE = {
    "BFO": "http://purl.obolibrary.org/obo/bfo/2020/bfo.owl",
    "IAO": "http://purl.obolibrary.org/obo/iao.owl",
    "RO": "http://purl.obolibrary.org/obo/ro.owl",
}

DECLARED_AS = {
    "http://www.w3.org/2002/07/owl#Class",
    "http://www.w3.org/2002/07/owl#ObjectProperty",
    "http://www.w3.org/2002/07/owl#AnnotationProperty",
    "http://www.w3.org/2002/07/owl#DatatypeProperty",
}


def load_upstream(local_dir: Path | None):
    from rdflib import Graph

    graph = Graph()
    loaded, failed = [], []

    if local_dir:
        files = sorted(
            path
            for pattern in ("*.owl", "*.ttl", "*.rdf")
            for path in local_dir.glob(pattern)
        )
        if not files:
            raise SystemExit(f"no ontology files found in {local_dir}")
        for path in files:
            try:
                graph.parse(path)
                loaded.append(str(path.name))
            except Exception as error:  # pragma: no cover
                failed.append(f"{path.name}: {error}")
    else:
        for name, url in REMOTE.items():
            try:
                graph.parse(url)
                loaded.append(name)
            except Exception as error:
                failed.append(f"{name} ({url}): {error}")

    return graph, loaded, failed


def external_iris(module_path: Path) -> set[str]:
    from rdflib import OWL, Graph, URIRef

    graph = Graph()
    graph.parse(module_path, format="turtle")

    # Importing an ontology is not referring to a term in it. The import
    # targets sit under the OBO prefix too, so without this they would be
    # reported as undeclared terms every run.
    imported = {str(o) for o in graph.objects(None, OWL.imports)}

    found = set()
    for triple in graph:
        for term in triple:
            if isinstance(term, URIRef) and str(term).startswith(OBO):
                if str(term) not in imported:
                    found.add(str(term))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--local",
        default=os.environ.get("RK_BFO_DIR"),
        help="directory containing bfo.owl, iao.owl and ro.owl",
    )
    args = parser.parse_args()

    try:
        from rdflib import RDF, RDFS, URIRef
    except ImportError:
        raise SystemExit("rdflib is required: pip install rdflib")

    with KERNEL.open(encoding="utf-8") as handle:
        registry = json.load(handle)["bfo"]["external_terms"]

    used = external_iris(MODULE)
    print(f"module references {len(used)} OBO terms")

    graph, loaded, failed = load_upstream(Path(args.local) if args.local else None)
    if failed:
        print("\ncould not load:")
        for item in failed:
            print(f"  {item}")
    if not loaded:
        print(
            "\nNo upstream ontology could be loaded, so the alignment is UNVERIFIED.\n"
            "This is not a pass. Re-run with network access, or with --local pointing\n"
            "at a directory containing bfo.owl, iao.owl and ro.owl."
        )
        return 2
    print(f"loaded: {', '.join(loaded)} ({len(graph)} triples)")

    missing, mislabelled, unregistered, ok = [], [], [], []
    for iri in sorted(used):
        local = iri.rsplit("/", 1)[-1]
        subject = URIRef(iri)
        declarations = {str(o) for o in graph.objects(subject, RDF.type)}
        if not declarations & DECLARED_AS:
            missing.append(local)
            continue
        upstream_labels = {str(o).lower() for o in graph.objects(subject, RDFS.label)}
        expected = registry.get(local)
        if expected is None:
            unregistered.append(local)
        elif upstream_labels and expected.lower() not in upstream_labels:
            mislabelled.append(f"{local}: registry says {expected!r}, upstream says {sorted(upstream_labels)}")
        else:
            ok.append(local)

    print(f"\ndeclared upstream: {len(ok) + len(mislabelled) + len(unregistered)}")
    print(f"verified against the registry: {len(ok)}")

    if unregistered:
        print(f"\nused but absent from data/kernel.json bfo.external_terms ({len(unregistered)}):")
        for item in unregistered:
            print(f"  {item}")
    if mislabelled:
        print(f"\nLABEL MISMATCH ({len(mislabelled)}):")
        for item in mislabelled:
            print(f"  {item}")
    if missing:
        print(f"\nNOT DECLARED UPSTREAM ({len(missing)}):")
        for item in missing:
            print(f"  {item}")
        print(
            "\nEach of these is being used as though it were a BFO, IAO or RO term while\n"
            "no such term exists. OWL created a fresh class for it and said nothing."
        )

    problems = bool(missing or mislabelled)
    print("\nFAIL" if problems else "\npass")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
