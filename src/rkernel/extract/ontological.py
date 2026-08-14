"""Entity-relation extractor: assertions of the form *X is a kind of Y*.

This is the instrument built for taxonomic structure. It is included in the
release not because it is needed for the typology but because running it
alongside the norm extractor, over the same chunks in the same pass, is the
controlled demonstration of precondition mismatch reported at paper §11.1.

On a reference ontology it yields many claims. On a procedural code it yields
nothing at all, and raises no error while doing so. A silent zero is what a
schema mismatch looks like from the outside, which is why both extractors are
run together and their yields reported side by side.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Iterable

from .lexicon import ONTOLOGICAL_PATTERNS
from .norms import Provision, _normalize, _sentences

_COMPILED = [(re.compile(pattern, re.IGNORECASE), relation) for pattern, relation in ONTOLOGICAL_PATTERNS]


@dataclass
class OntologicalClaim:
    claim_id: str
    provision_id: str
    locator: str
    subject: str
    relation: str
    object: str
    quote: str


def extract_claims(provisions: Iterable[Provision]) -> list[OntologicalClaim]:
    claims: list[OntologicalClaim] = []
    for provision in provisions:
        for index, sentence in enumerate(_sentences(provision.text)):
            for pattern, relation in _COMPILED:
                match = pattern.search(sentence)
                if not match:
                    continue
                subject = _normalize(sentence[: match.start()])
                obj = _normalize(sentence[match.end():])
                if not subject or not obj:
                    continue
                claims.append(
                    OntologicalClaim(
                        claim_id=f"{provision.id}#c{index}",
                        provision_id=provision.id,
                        locator=provision.locator,
                        subject=subject[-120:],
                        relation=relation,
                        object=obj[:120],
                        quote=sentence,
                    )
                )
                break
    return claims


def claims_to_dicts(claims: list[OntologicalClaim]) -> list[dict]:
    return [asdict(claim) for claim in claims]


def _reading(norms: int, claims: int) -> str:
    """State the mismatch in the direction the numbers actually run."""
    deontic_shape = norms > 0 and claims * 5 < norms
    ontological_shape = claims > 0 and norms * 5 < claims
    if deontic_shape:
        return (
            "Two extractors over identical input in a single pass. The near-zero yield "
            "from the entity-relation extractor is a precondition mismatch, not poor "
            "performance: this corpus states what an actor is required to do, not what "
            "kind of thing something is. An extractor looking for universals reads a "
            "procedural code and finds nothing, and raises no error while doing so."
        )
    if ontological_shape:
        return (
            "Two extractors over identical input in a single pass, with the yields "
            "reversed. This corpus asserts kinds and issues no directives, so the norm "
            "extractor returns almost nothing. Neither instrument is the better one. "
            "Each is built for a different kind of structure, and the pair of runs is "
            "what makes the mismatch a demonstration rather than an assertion."
        )
    return (
        "Both extractors returned material. This corpus carries both taxonomic and "
        "deontic structure, so neither yield diagnoses a precondition mismatch. Report "
        "the two counts and inspect a sample from each before drawing any conclusion."
    )


def control_report(provisions: list[Provision], norms_summary: dict, claims: list[OntologicalClaim]) -> dict:
    """The within-run control of §11.1, as a reportable object."""
    return {
        "provisions": len(provisions),
        "characters": sum(len(p.text) for p in provisions),
        "entity_relation_extractor": {
            "target_schema": "ontological claims",
            "yield": len(claims),
            "errors": 0,
        },
        "norm_tuple_extractor": {
            "target_schema": "deontic norms",
            "yield": norms_summary["tuples_unique"],
            "errors": 0,
        },
        "reading": _reading(norms_summary["tuples_unique"], len(claims)),
    }
