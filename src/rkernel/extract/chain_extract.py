"""Draft a recognition chain from a corpus.

The output is a **draft**, never a committed chain. Chain profiles in the
registered design are assigned by hand with evidence locators and committed
before detectors are run (paper §10.1), and the reliability of chain extraction
has not been established (§13). This module exists to give an analyst a
starting point and a set of locators to check, and it labels every status it
proposes with the evidence it used.

Status assignment rests on a single distinction the paper draws:

  internal  the system specifies the link and it is carried out under the
            system's own authority
  external  the link occurs but is neither specified nor governed by the system
  absent    the system has no such link at all

The heuristic reads *specification* from cue density and *externality* from
references to instruments outside the corpus at the same link.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Sequence

from ..chain import Chain, Link
from ..kernel import CHAIN_LINKS
from .lexicon import EXTERNAL_INSTRUMENT_RE, LINK_CUES
from .norms import Provision

MIN_HITS_FOR_INTERNAL = 3
MIN_HITS_FOR_PRESENT = 1


def score_links(provisions: Sequence[Provision]) -> dict[str, list[dict]]:
    """Return, per link, the provisions supplying cue evidence for it."""
    hits: dict[str, list[dict]] = defaultdict(list)
    for provision in provisions:
        lowered = provision.text.lower()
        for link_id, cues in LINK_CUES.items():
            matched = [cue for cue in cues if cue in lowered]
            if matched:
                hits[link_id].append(
                    {
                        "locator": provision.locator,
                        "cues": matched,
                        "external_reference": bool(EXTERNAL_INSTRUMENT_RE.search(provision.text)),
                    }
                )
    return dict(hits)


def draft_chain(
    provisions: Sequence[Provision],
    chain_id: str,
    label: str,
    corpus: str = "",
    max_evidence: int = 3,
) -> Chain:
    """Propose a chain from cue evidence. Review every status before use."""
    hits = score_links(provisions)
    links: dict[str, Link] = {}

    for link_id in CHAIN_LINKS:
        evidence = hits.get(link_id, [])
        count = len(evidence)
        external_share = (
            sum(1 for item in evidence if item["external_reference"]) / count if count else 0.0
        )

        if count < MIN_HITS_FOR_PRESENT:
            status = "absent"
            note = "No cue evidence for this link in the corpus."
        elif count >= MIN_HITS_FOR_INTERNAL and external_share < 0.5:
            status = "internal"
            note = f"{count} provisions carry cues for this link; specification appears internal."
        else:
            status = "external"
            note = (
                f"{count} provisions carry cues for this link, "
                f"{external_share:.0%} of them referring to outside instruments; "
                "the link appears to occur but not to be governed here."
            )

        links[link_id] = Link(
            id=link_id,
            status=status,  # type: ignore[arg-type]
            evidence=[
                {"locator": item["locator"], "note": ", ".join(item["cues"][:4])}
                for item in evidence[:max_evidence]
            ],
            confidence="low",
            note=note,
        )

    return Chain(
        chain_id=chain_id,
        system={
            "label": label,
            "corpus": corpus,
            "notes": (
                "DRAFT. Produced by rkernel.extract.chain_extract from cue density. "
                "Chain extraction has no established reliability (paper §13): two "
                "annotators independently extracting the seven links, with per-link "
                "agreement reported, is a precondition for use in the empirical "
                "design. Expect disagreement to concentrate at assessor-in-role and "
                "remedy."
            ),
        },
        links=links,
        assigned_by="rkernel.extract.chain_extract (draft, unreviewed)",
        committed_before_detection=False,
        provenance="cue-density heuristic over corpus provisions",
    )
