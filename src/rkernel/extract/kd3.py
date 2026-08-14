"""K-D3 detector: a capacity conferred in the text with no invocation pathway.

Stage one extracts capacity-conferring provisions (norm tuples with modality
`power`). Stage two searches the corpus for an invocation pathway. A capacity
with no pathway is a *candidate* finding, never a finding.

Stage two satisfies **two independent conditions over disjoint vocabularies**
(paper §10.1). A provision counts as a pathway only if it is

  1. *about the same capacity* — established by explicit cross-reference, by
     position in the same rule, or by distinctive content-word overlap; and
  2. *supplies a procedural marker* — a filing or motion requirement, a named
     recipient, a deadline, a form specification, a hearing.

The vocabulary establishing condition 2 is excluded from condition 1 by
construction in `lexicon.py`. Where a single similarity test does both jobs,
every procedural provision resembles every capacity and the detector measures
the density of procedural language rather than the presence of pathways. That
is the failure documented at §11.2, where the median capacity matched twelve
pathway loci, the mean twenty-one, and one provision was returned as the
pathway for sixty-seven unrelated capacities.

Two further disciplines are enforced here:

*  Capacities whose pathway depends on an instrument outside the corpus are
   recorded as **external** and reported separately. A K-D3 rate that collapses
   when external references are excluded is not a finding, and both rates are
   returned side by side.
*  **Fan-out is always reported.** A rate produced by a matcher whose fan-out
   is unreported cannot be interpreted, so `detect()` returns the distribution
   of pathway matches per capacity whether or not anyone asked for it.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .lexicon import (
    CROSSREF_RE,
    EXTERNAL_INSTRUMENT_RE,
    content_tokens,
    procedural_markers_in,
)
from .norms import NormTuple, Provision

DETECTOR_NAME = "kd3.pathway"
DETECTOR_VERSION = "0.1.0"


@dataclass
class MatcherConfig:
    """Parameters of the two-condition matcher, recorded with every finding."""

    min_shared_content_terms: int = 2
    max_document_frequency: float = 0.25
    min_procedural_markers: int = 1
    same_rule_counts_as_topical: bool = True
    crossref_counts_as_topical: bool = True
    require_distinct_provision: bool = True

    def as_dict(self) -> dict:
        return {
            "min_shared_content_terms": self.min_shared_content_terms,
            "max_document_frequency": self.max_document_frequency,
            "min_procedural_markers": self.min_procedural_markers,
            "same_rule_counts_as_topical": self.same_rule_counts_as_topical,
            "crossref_counts_as_topical": self.crossref_counts_as_topical,
            "require_distinct_provision": self.require_distinct_provision,
            "condition_1_vocabulary": "content tokens (procedural markers and stopwords removed)",
            "condition_2_vocabulary": "PROCEDURAL_MARKERS",
            "vocabularies_disjoint": True,
        }


@dataclass
class PathwayMatch:
    locator: str
    provision_id: str
    topical_evidence: str
    shared_terms: list[str] = field(default_factory=list)
    procedural_markers: list[str] = field(default_factory=list)


def _document_frequencies(provisions: Sequence[Provision]) -> tuple[dict[str, int], int]:
    frequencies: Counter[str] = Counter()
    for provision in provisions:
        frequencies.update(content_tokens(provision.text))
    return dict(frequencies), len(provisions)


def _distinctive(tokens: set[str], frequencies: dict[str, int], total: int, cutoff: float) -> set[str]:
    """Content terms rare enough to individuate a capacity.

    The floor of two matters. A term shared between exactly the capacity and one
    candidate provision has a document frequency of two and is maximally
    distinctive, so a proportional cutoff alone would exclude every shared term
    on a small corpus and return every capacity as a candidate. The cutoff binds
    only once the corpus is large enough for it to mean something.
    """
    if total == 0:
        return set()
    allowed = max(2.0, cutoff * total)
    return {token for token in tokens if frequencies.get(token, 0) <= allowed}


def _subdivision(locator: str) -> str:
    match = re.search(r"\(([a-z0-9]+)\)", locator, re.IGNORECASE)
    return match.group(1) if match else ""


def _rule_number(locator: str) -> str:
    match = re.match(r"(?:Rule\s*|§\s*)?([0-9]+(?:\.[0-9]+)?)", locator.strip(), re.IGNORECASE)
    return match.group(1) if match else locator.strip()


def _crossrefs(text: str) -> set[str]:
    return {match.group(1).lower() for match in CROSSREF_RE.finditer(text)}


def detect(
    capacities: Iterable[NormTuple],
    provisions: Sequence[Provision],
    config: MatcherConfig | None = None,
) -> dict:
    """Run the K-D3 detector. Returns findings plus the fan-out report."""
    config = config or MatcherConfig()
    capacities = [
        capacity
        for capacity in capacities
        if capacity.is_capacity and capacity.duplicate_of is None
    ]
    by_id = {provision.id: provision for provision in provisions}
    frequencies, total = _document_frequencies(provisions)

    provision_index = []
    for provision in provisions:
        provision_index.append(
            (
                provision,
                content_tokens(provision.text),
                procedural_markers_in(provision.text),
                _crossrefs(provision.text),
                _rule_number(provision.locator),
            )
        )

    findings: list[dict] = []
    fan_out: list[int] = []
    external_count = 0
    scored_count = 0

    for capacity in capacities:
        source_provision = by_id.get(capacity.provision_id)
        capacity_text = capacity.quote
        capacity_tokens = _distinctive(
            content_tokens(capacity_text), frequencies, total, config.max_document_frequency
        )
        capacity_rule = _rule_number(capacity.locator)
        capacity_refs = _crossrefs(capacity_text)

        matches: list[PathwayMatch] = []
        for provision, tokens, markers, refs, rule in provision_index:
            if config.require_distinct_provision and provision.id == capacity.provision_id:
                continue

            # Condition 2 first: it is cheap and independent.
            if len(markers) < config.min_procedural_markers:
                continue

            # Condition 1, over vocabulary disjoint from condition 2.
            topical_evidence = ""
            shared: set[str] = set()
            if config.crossref_counts_as_topical and (
                _subdivision(provision.locator).lower() in {ref.lower() for ref in capacity_refs}
                or any(ref.startswith(rule) for ref in capacity_refs)
                or any(ref.startswith(capacity_rule) for ref in refs)
            ):
                topical_evidence = "cross-reference"
            elif config.same_rule_counts_as_topical and rule and rule == capacity_rule:
                topical_evidence = "same rule"
            else:
                shared = capacity_tokens & _distinctive(
                    tokens, frequencies, total, config.max_document_frequency
                )
                if len(shared) >= config.min_shared_content_terms:
                    topical_evidence = "distinctive content overlap"

            if not topical_evidence:
                continue

            matches.append(
                PathwayMatch(
                    locator=provision.locator,
                    provision_id=provision.id,
                    topical_evidence=topical_evidence,
                    shared_terms=sorted(shared),
                    procedural_markers=sorted(markers),
                )
            )

        fan_out.append(len(matches))

        is_external = bool(
            EXTERNAL_INSTRUMENT_RE.search(capacity_text)
            or (source_provision and EXTERNAL_INSTRUMENT_RE.search(source_provision.text))
        )

        if matches:
            continue  # a pathway exists; nothing to report

        if is_external:
            external_count += 1
            status = "external"
            external_reference = _external_reference(capacity_text, source_provision)
        else:
            scored_count += 1
            status = "candidate"
            external_reference = None

        findings.append(
            {
                "finding_id": f"kd3-{capacity.norm_id}",
                "primitive": "K-D3",
                "locus": "remedy" if _looks_like_remedy(capacity_text) else "act",
                "status": status,
                "provenance": "undetermined",
                "detector": {
                    "name": DETECTOR_NAME,
                    "version": DETECTOR_VERSION,
                    "parameters": config.as_dict(),
                },
                "capacity": {
                    "norm_id": capacity.norm_id,
                    "bearer": capacity.bearer,
                    "action": capacity.action,
                    "locator": capacity.locator,
                    "quote": capacity.quote,
                },
                "pathway_matches": [],
                "external_reference": external_reference,
                "duplicate_of": None,
                "note": (
                    "Candidate only. No invocation pathway was matched under a "
                    "two-condition matcher over disjoint vocabularies. Adjudicate "
                    "against source text before treating this as a finding, and set "
                    "provenance by hand."
                ),
            }
        )

    return {
        "detector": {"name": DETECTOR_NAME, "version": DETECTOR_VERSION,
                     "parameters": config.as_dict()},
        "capacities_examined": len(capacities),
        "set_aside_external": external_count,
        "scored": len(capacities) - external_count,
        "candidates": scored_count,
        "with_pathway": sum(1 for count in fan_out if count > 0),
        "findings": findings,
        "fan_out": fan_out_report(fan_out),
        "rates": {
            "candidates_over_scored": _safe_ratio(scored_count, len(capacities) - external_count),
            "candidates_over_all_capacities": _safe_ratio(scored_count, len(capacities)),
            "note": (
                "Both rates are reported. A K-D3 rate that collapses when external "
                "references are excluded is not a finding."
            ),
        },
        "reporting_constraints": [
            "Findings are candidates, not findings, until adjudicated against source text.",
            "provenance defaults to undetermined; the detector never emits 'source'.",
            "Fan-out is reported unconditionally: a rate produced by a matcher whose "
            "fan-out is unreported cannot be interpreted.",
        ],
    }


def _looks_like_remedy(text: str) -> bool:
    return bool(
        re.search(
            r"\b(appeal|review|reconsider|set\s+aside|vacate|revoke|suspend|"
            r"rescind|reopen|relief\s+from|decertif)\w*",
            text,
            re.IGNORECASE,
        )
    )


def _external_reference(capacity_text: str, provision: Provision | None) -> str | None:
    match = EXTERNAL_INSTRUMENT_RE.search(capacity_text)
    if not match and provision:
        match = EXTERNAL_INSTRUMENT_RE.search(provision.text)
    return match.group(0) if match else None


def _safe_ratio(numerator: int, denominator: int) -> float | None:
    return round(numerator / denominator, 4) if denominator else None


def fan_out_report(fan_out: Sequence[int]) -> dict:
    """Distribution of pathway matches per capacity.

    Mandated by paper §10.4. The §11.2 diagnosis was made from exactly these
    numbers: a median of twelve and a maximum of two hundred and nineteen is a
    matcher measuring vocabulary density, not pathway presence.
    """
    if not fan_out:
        return {
            "n": 0,
            "min": 0,
            "median": 0,
            "mean": 0.0,
            "p90": 0,
            "max": 0,
            "zero_matches": 0,
            "histogram": {},
            "interpretation": (
                "No capacities were extracted, so there is no fan-out to report. In an "
                "act-empty corpus this is the predicted result and not a null finding: "
                "the detector had nothing to run on because the system confers no "
                "capacities. Do not report it as an absence of K-D3."
            ),
        }
    ordered = sorted(fan_out)
    n = len(ordered)

    def percentile(p: float) -> int:
        index = min(n - 1, max(0, math.ceil(p * n) - 1))
        return ordered[index]

    return {
        "n": n,
        "min": ordered[0],
        "median": percentile(0.5),
        "mean": round(sum(ordered) / n, 2),
        "p90": percentile(0.9),
        "max": ordered[-1],
        "zero_matches": sum(1 for count in ordered if count == 0),
        "histogram": dict(sorted(Counter(ordered).items())),
        "interpretation": _interpret_fan_out(ordered),
    }


def _interpret_fan_out(ordered: Sequence[int]) -> str:
    n = len(ordered)
    median = ordered[n // 2]
    maximum = ordered[-1]
    if median > 5 or maximum > 50:
        return (
            "Fan-out is high. The matcher is likely awarding pathways on generic "
            "vocabulary, which inverts the interpretation of the zero-match cases: "
            "they become the capacities whose phrasing happened not to overlap with "
            "anything, rather than a structural fact about the corpus. Do not report "
            "a rate from this run."
        )
    if median <= 2 and maximum <= 20:
        return (
            "Fan-out is in a range where individual matches can be inspected by hand. "
            "Adjudicate a sample before reporting any rate."
        )
    return "Fan-out is moderate. Inspect the upper tail before reporting a rate."
