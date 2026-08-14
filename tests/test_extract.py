"""Tests for the extractors and the K-D3 detector.

The load-bearing tests here are the ones that check the *discipline* rather than
the yield: that the two matcher vocabularies are disjoint, that fan-out is
reported unconditionally, that no detector emits a source-level provenance, and
that a capacity whose pathway lies outside the corpus is set aside rather than
scored.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rkernel import load_corpus
from rkernel.extract import lexicon
from rkernel.extract.kd3 import MatcherConfig, detect, fan_out_report
from rkernel.extract.norms import Provision, extract_norms, summarize
from rkernel.extract.ontological import control_report, extract_claims

ROOT = Path(__file__).resolve().parents[1]
FRCP = ROOT / "examples" / "frcp" / "corpus" / "frcp_demo.json"
GO = ROOT / "examples" / "go" / "corpus" / "go_demo.json"


@pytest.fixture(scope="module")
def frcp():
    return load_corpus(FRCP)


@pytest.fixture(scope="module")
def go():
    return load_corpus(GO)


# --------------------------------------------------------------------------
# Vocabulary disjointness: the fix at the centre of the release
# --------------------------------------------------------------------------


def test_matcher_vocabularies_are_disjoint():
    lexicon.assert_disjoint()


def test_content_tokens_exclude_every_procedural_marker():
    """Condition 1 must not be able to see condition 2's vocabulary. If it can,
    every procedural provision resembles every capacity and one test is doing
    the work of two."""
    text = " ".join(sorted(lexicon.PROCEDURAL_MARKERS))
    assert lexicon.content_tokens(text) == set()


def test_procedural_markers_are_visible_to_condition_two():
    markers = lexicon.procedural_markers_in(
        "The motion must be filed within 14 days and served on the opposing party."
    )
    assert {"motion", "filed", "within", "days", "served"} <= markers


def test_disjointness_failure_raises_rather_than_warns(monkeypatch):
    monkeypatch.setattr(
        lexicon, "PROCEDURAL_MARKERS", lexicon.PROCEDURAL_MARKERS | {"the"}
    )
    with pytest.raises(AssertionError):
        lexicon.assert_disjoint()


# --------------------------------------------------------------------------
# The within-run control: two extractors, same input, same pass
# --------------------------------------------------------------------------


def test_deontic_corpus_yields_norms_and_almost_no_ontological_claims(frcp):
    provisions, _ = frcp
    norms = extract_norms(provisions)
    claims = extract_claims(provisions)
    summary = summarize(norms)
    assert summary["tuples_unique"] > 20
    assert len(claims) == 0
    report = control_report(provisions, summary, claims)
    assert report["entity_relation_extractor"]["errors"] == 0
    assert "precondition mismatch" in report["reading"]


def test_taxonomic_corpus_yields_claims_and_almost_no_norms(go):
    provisions, _ = go
    norms = extract_norms(provisions)
    claims = extract_claims(provisions)
    assert len(claims) > 10
    assert summarize(norms)["tuples_unique"] == 0


def test_the_control_reads_the_mismatch_in_both_directions(frcp, go):
    """The point is symmetric. Neither instrument is the better one."""
    readings = []
    for provisions, _ in (frcp, go):
        norms = extract_norms(provisions)
        claims = extract_claims(provisions)
        readings.append(control_report(provisions, summarize(norms), claims)["reading"])
    assert readings[0] != readings[1]


# --------------------------------------------------------------------------
# Norm extraction
# --------------------------------------------------------------------------


def test_modalities_are_distinguished():
    provisions = [
        Provision("p1", "Rule 1", "The clerk must enter the default."),
        Provision("p2", "Rule 2", "A party may not file a second motion."),
        Provision("p3", "Rule 3", "A party may move for summary judgment."),
        Provision("p4", "Rule 4", "A party may bring a copy of the exhibit."),
    ]
    modalities = {n.locator: n.modality for n in extract_norms(provisions)}
    assert modalities["Rule 1"] == "duty"
    assert modalities["Rule 2"] == "prohibition"
    assert modalities["Rule 3"] == "power"


def test_capacities_are_the_power_tuples(frcp):
    provisions, _ = frcp
    capacities = [n for n in extract_norms(provisions) if n.is_capacity]
    assert capacities
    assert all(n.modality == "power" for n in capacities)


def test_deadlines_and_conditions_are_captured():
    norms = extract_norms(
        [Provision("p", "Rule 59(b)", "A motion for a new trial must be filed no later than 28 days after the entry of judgment.")]
    )
    assert norms[0].deadline is not None


def test_byte_identical_quotes_are_collapsed():
    """One norm counted twice under a mis-assigned locator is an extraction
    artifact, not two findings."""
    text = "A party may move for an order compelling discovery."
    norms = extract_norms(
        [Provision("a", "Rule 37(a)", text), Provision("b", "Rule 26(c)", text)]
    )
    assert len(norms) == 2
    assert summarize(norms)["duplicates_collapsed"] == 1
    assert norms[1].duplicate_of == norms[0].norm_id


# --------------------------------------------------------------------------
# K-D3 detection
# --------------------------------------------------------------------------


def test_fan_out_is_reported_unconditionally(frcp):
    provisions, _ = frcp
    result = detect(extract_norms(provisions), provisions)
    for key in ("n", "min", "median", "mean", "p90", "max", "histogram", "interpretation"):
        assert key in result["fan_out"], key


def test_fan_out_report_is_populated_even_with_no_capacities():
    report = fan_out_report([])
    assert report["n"] == 0
    assert "not a null finding" in report["interpretation"]


def test_high_fan_out_refuses_a_rate():
    report = fan_out_report([12] * 40 + [219])
    assert "Do not report a rate" in report["interpretation"]


def test_no_finding_claims_a_source_level_provenance(frcp):
    provisions, _ = frcp
    result = detect(extract_norms(provisions), provisions)
    for finding in result["findings"]:
        assert finding["provenance"] == "undetermined"
        assert finding["status"] in ("candidate", "external")


def test_external_capacities_are_set_aside_and_reported_separately(frcp):
    provisions, _ = frcp
    result = detect(extract_norms(provisions), provisions)
    assert result["set_aside_external"] >= 1
    assert result["rates"]["candidates_over_scored"] is not None
    assert result["rates"]["candidates_over_all_capacities"] is not None
    externals = [f for f in result["findings"] if f["status"] == "external"]
    assert all(f["external_reference"] for f in externals)


def test_both_conditions_are_required_for_a_pathway():
    """A provision that is topically on point but supplies no procedural marker
    is not a pathway, and a procedural provision about something else is not
    a pathway either."""
    capacity = Provision(
        "cap", "Rule 90(a)", "A party may seek disgorgement of unjust enrichment proceeds."
    )
    topical_only = Provision(
        "t", "Rule 91", "Disgorgement of unjust enrichment proceeds is measured at fair value."
    )
    procedural_only = Provision(
        "p", "Rule 92", "A motion must be filed within 14 days and served on the parties."
    )
    provisions = [capacity, topical_only, procedural_only]
    result = detect(extract_norms(provisions), provisions)
    assert result["candidates"] == 1, "neither provision should count as a pathway"


def test_a_genuine_pathway_is_matched():
    capacity = Provision(
        "cap", "Rule 90(a)", "A party may seek disgorgement of unjust enrichment proceeds."
    )
    pathway = Provision(
        "p",
        "Rule 91",
        "A motion for disgorgement of unjust enrichment proceeds must be filed within 14 days "
        "and served on the opposing party.",
    )
    provisions = [capacity, pathway]
    result = detect(extract_norms(provisions), provisions)
    assert result["candidates"] == 0
    assert result["fan_out"]["max"] == 1


def test_matcher_parameters_travel_with_every_finding():
    capacity = Provision("cap", "Rule 90(a)", "A party may seek an unusual bespoke remedy.")
    result = detect(extract_norms([capacity]), [capacity], MatcherConfig(min_shared_content_terms=3))
    for finding in result["findings"]:
        parameters = finding["detector"]["parameters"]
        assert parameters["min_shared_content_terms"] == 3
        assert parameters["vocabularies_disjoint"] is True


def test_act_empty_corpus_produces_no_capacities(go):
    """The predicted result for cell 1, and not a null finding: the detector had
    nothing to run on."""
    provisions, _ = go
    result = detect(extract_norms(provisions), provisions)
    assert result["capacities_examined"] == 0
    assert result["candidates"] == 0
    assert "not a null finding" in result["fan_out"]["interpretation"]
