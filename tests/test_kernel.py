"""Tests for the kernel, the gating rule, and the product construction.

The interesting tests are not the unit tests. They are the three that check the
construction against material it did not generate:

* `test_legal_grid_reproduces_table_7` — the locus mask reproduces the paper's
  published grid cell for cell.
* `test_fuller_lands_on_well_formed_crossings` — an independent eight-item list,
  arrived at by a theorist with no knowledge of this construction, lands inside
  the grid at determinate coordinates.
* `test_classificatory_typology_is_derived` — the seven classificatory types are
  regenerated from the ICD-11 chain rather than looked up.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from rkernel import Chain, generate, load_kernel
from rkernel.kernel import CHAIN_LINKS
from rkernel.typology import reference_grid

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


@pytest.fixture(scope="module")
def kernel():
    return load_kernel()


def chain(name: str) -> Chain:
    return Chain.load(next(EXAMPLES.rglob(f"{name}.chain.json")))


# --------------------------------------------------------------------------
# Kernel integrity
# --------------------------------------------------------------------------


def test_kernel_self_check_is_clean(kernel):
    assert kernel.self_check() == []


def test_twelve_primitives_in_four_strata(kernel):
    assert len(kernel.primitives) == 12
    assert len(kernel.strata) == 4
    assert [len(kernel.primitives_in(s.id)) for s in kernel.strata] == [3, 3, 3, 3]


def test_only_stratum_d_is_gated(kernel):
    gated = {s.id for s in kernel.strata if s.gated}
    assert gated == {"D"}


def test_seven_chain_loci_plus_one_pseudo_locus(kernel):
    assert [locus.id for locus in kernel.chain_loci] == list(CHAIN_LINKS)
    assert [locus.id for locus in kernel.pseudo_loci] == ["artifact"]


def test_no_stratum_d_primitive_is_well_formed_at_the_artifact_body(kernel):
    for primitive in kernel.primitives_in("D"):
        assert not primitive.is_well_formed_at("artifact"), primitive.id


def test_every_ungated_primitive_is_well_formed_at_the_artifact_body(kernel):
    """Required by the reference-ontology profile: A, B and C must fire in a
    system with no chain at all."""
    for stratum in ("A", "B", "C"):
        for primitive in kernel.primitives_in(stratum):
            assert primitive.is_well_formed_at("artifact"), primitive.id


# --------------------------------------------------------------------------
# The locus mask against the published grid
# --------------------------------------------------------------------------

#: Per-primitive counts of well-formed crossings over the seven chain loci,
#: read off the paper's Table 7.
TABLE_7_COUNTS = {
    "K-A1": 7, "K-A2": 6, "K-A3": 7,
    "K-B1": 6, "K-B2": 7, "K-B3": 4,
    "K-C1": 7, "K-C2": 7, "K-C3": 6,
    "K-D1": 4, "K-D2": 3, "K-D3": 6,
}


def test_legal_grid_reproduces_table_7(kernel):
    grid = reference_grid(kernel)
    for primitive_id, expected in TABLE_7_COUNTS.items():
        actual = sum(grid["rows"][primitive_id].values())
        assert actual == expected, f"{primitive_id}: expected {expected}, got {actual}"


def test_grid_total_is_computed_not_stored(kernel):
    """The paper's prose says sixty-nine of eighty-four; its Table 7 marks
    seventy. This implementation follows the table and computes the total, so
    the discrepancy is visible rather than absorbed."""
    grid = reference_grid(kernel)
    assert grid["cells_total"] == 84
    assert grid["well_formed"] == sum(TABLE_7_COUNTS.values()) == 70


# --------------------------------------------------------------------------
# The gating rule
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,expected",
    [("internal", "fires"), ("external", "rare"), ("absent", "cannot_fire")],
)
def test_gating_of_stratum_d(kernel, status, expected):
    assert kernel.firing_value("K-D3", "act", status) == expected


@pytest.mark.parametrize("status", ["internal", "external"])
def test_ungated_strata_fire_wherever_the_locus_exists(kernel, status):
    for primitive_id in ("K-A1", "K-B2", "K-C1"):
        assert kernel.firing_value(primitive_id, "criteria", status) == "fires"


def test_not_well_formed_is_distinguished_from_cannot_fire(kernel):
    # K-D1 is not well-formed at authority: there is no such coordinate.
    assert kernel.firing_value("K-D1", "authority", "internal") == "not_applicable"
    # K-D1 is well-formed at act but barred when the act is absent.
    assert kernel.firing_value("K-D1", "act", "absent") == "cannot_fire"


def test_no_locus_is_distinguished_from_not_applicable(kernel):
    """SPEC 5.1: an absent link is a system-level fact, not a kernel-level one.

    K-A1 is well-formed at authority, so a system lacking an authority link
    must not report the same value as a crossing that no system can have.
    """
    assert kernel.firing_value("K-A1", "authority", "absent") == "no_locus"
    # Whereas D at the artifact body is not well-formed for any system at all.
    assert kernel.firing_value("K-D1", "artifact", None) == "not_applicable"
    assert kernel.is_well_formed("K-A1", "authority")
    assert not kernel.is_well_formed("K-D1", "artifact")


def test_no_locus_is_reserved_for_ungated_strata(kernel):
    """Gated strata keep cannot_fire: the failure is barred, not relocated."""
    for primitive_id in ("K-D1", "K-D2", "K-D3"):
        assert kernel.firing_value(primitive_id, "act", "absent") == "cannot_fire"
    for primitive_id in ("K-A1", "K-B2", "K-C1"):
        assert kernel.firing_value(primitive_id, "criteria", "absent") == "no_locus"


def test_not_applicable_counts_exactly_the_not_well_formed_cells(kernel):
    """The invariant that makes not_applicable a kernel-level fact.

    Its tally must equal cells_total - well_formed for every chain, since it
    now means only 'this coordinate does not exist'.
    """
    for name in ("go", "icd11", "cfr205", "frcp"):
        counts = generate(chain(name), kernel)["counts"]
        assert counts["not_applicable"] == counts["cells_total"] - counts["well_formed"]


def test_chainless_ontology_relocates_its_failures_to_the_artifact(kernel):
    """GO has no chain: A/B/C must read no_locus at the chain loci and fire at
    the artifact body, rather than reading not_applicable everywhere."""
    typology = generate(chain("go"), kernel)
    by_locus = typology["profile_by_locus"]
    for stratum in ("A", "B", "C"):
        assert by_locus[stratum]["artifact"] == "fires"
        for locus in ("authority", "criteria", "assessor", "facts", "act", "effects", "remedy"):
            assert by_locus[stratum][locus] == "no_locus", (stratum, locus)
        # The summary still reports the relocated failure.
        assert typology["profile"][stratum] == "fires"
    # D has nowhere to relocate to, so it stays barred.
    assert by_locus["D"]["artifact"] == "not_applicable"
    assert typology["profile"]["D"] == "cannot_fire"


# --------------------------------------------------------------------------
# The four profiles
# --------------------------------------------------------------------------

EXPECTED_PROFILES = {
    "go": ("reference_ontology", {"A": "fires", "B": "fires", "C": "fires", "D": "cannot_fire"}),
    "icd11": ("classification", {"A": "fires", "B": "fires", "C": "fires", "D": "rare"}),
    "cfr205": ("certification_scheme", {"A": "fires", "B": "fires", "C": "fires", "D": "rare"}),
    "frcp": ("legal_order", {"A": "fires", "B": "fires", "C": "fires", "D": "fires"}),
}


@pytest.mark.parametrize("name", sorted(EXPECTED_PROFILES))
def test_profiles_match_the_published_table(kernel, name):
    expected_kind, expected_profile = EXPECTED_PROFILES[name]
    typology = generate(chain(name), kernel)
    assert typology["computed_kind"] == expected_kind
    assert typology["profile"] == expected_profile


@pytest.mark.parametrize("name", sorted(EXPECTED_PROFILES))
def test_declared_kind_agrees_with_computed_kind(kernel, name):
    typology = generate(chain(name), kernel)
    assert not typology["kind_mismatch"], (
        f"{name}: declared {typology['declared_kind']}, computed {typology['computed_kind']}"
    )


def test_abc_columns_are_constant_across_kinds(kernel):
    for name in EXPECTED_PROFILES:
        profile = generate(chain(name), kernel)["profile"]
        assert profile["A"] == profile["B"] == profile["C"] == "fires"


def test_classification_and_certification_differ_below_the_summary(kernel):
    """Both are act-thin, so both summarise to `rare` at Stratum D. The
    measurement the registered design turns on is the difference the summary
    hides, and it must be recoverable from the output."""
    icd = generate(chain("icd11"), kernel)
    cfr = generate(chain("cfr205"), kernel)
    assert icd["profile"]["D"] == cfr["profile"]["D"] == "rare"
    assert icd["profile_by_locus"]["D"]["remedy"] == "rare"
    assert cfr["profile_by_locus"]["D"]["remedy"] == "fires"


def test_no_stratum_d_cell_fires_in_an_act_empty_system(kernel):
    typology = generate(chain("go"), kernel)
    for crossing in typology["crossings"]:
        if crossing["stratum"] == "D":
            assert crossing["firing"] in ("cannot_fire", "not_applicable"), crossing


def test_ungated_strata_still_fire_in_an_act_empty_system(kernel):
    """An empty pragmatic stratum is a diagnosis of kind, not a clean audit."""
    typology = generate(chain("go"), kernel)
    firing = [c for c in typology["crossings"] if c["firing"] == "fires"]
    assert firing, "a reference ontology can be as inconsistent as a legal code"
    assert {c["stratum"] for c in firing} == {"A", "B", "C"}
    assert {c["locus"] for c in firing} == {"artifact"}


# --------------------------------------------------------------------------
# Derivation of known typologies
# --------------------------------------------------------------------------


def test_sool_types_are_located_in_the_legal_grid(kernel):
    typology = generate(chain("frcp"), kernel)
    located = {
        crossing["named_type"]: (crossing["primitive"], crossing["locus"], crossing["firing"])
        for crossing in typology["crossings"]
        if crossing["named_type"]
    }
    expected = {
        "JC": ("K-A1", "effects"),
        "TC": ("K-B1", "criteria"),
        "AI": ("K-B2", "authority"),
        "CF": ("K-C3", "assessor"),
        "RF": ("K-D3", "remedy"),
    }
    for key, coordinates in expected.items():
        assert key in located, f"{key} not located in the legal grid"
        assert located[key][:2] == coordinates
        assert located[key][2] == "fires"


def test_classificatory_typology_is_derived(kernel):
    """The seven classificatory types are regenerated from the ICD-11 chain."""
    typology = generate(chain("icd11"), kernel)
    located = {c["named_type"] for c in typology["crossings"] if c["named_type"]}
    assert {f"CT-{n}" for n in range(1, 8)} <= located


def test_classificatory_typology_has_no_stratum_d_member(kernel):
    """Explained by the construction rather than stipulated: a manual contains
    no acts of its own."""
    for named in kernel.named_types:
        if named.system_kind == "classification":
            assert kernel.primitive(named.primitive).stratum != "D", named.key


def test_classificatory_typology_clusters_at_criteria(kernel):
    """Every member but CT-7 sits at or adjacent to the criteria locus, because
    criteria are the only link a classification specifies in full."""
    off_criteria = [
        named.key
        for named in kernel.named_types
        if named.system_kind == "classification" and named.locus != "criteria"
    ]
    assert off_criteria == ["CT-7"]


def test_fuller_lands_on_well_formed_crossings(kernel):
    """An independent eight-item list lands inside the grid at determinate
    coordinates. This is a check on the kernel, not on Fuller."""
    items = kernel.external_lists["fuller_1964"]["items"]
    assert len(items) == 8
    for item in items:
        assert kernel.is_well_formed(item["primitive"], item["locus"]), item["desideratum"]


def test_fuller_arrows_are_manifestation_pointers_not_second_crossings(kernel):
    """Table 9 writes 'Criteria -> Effects' for possibility of compliance, while
    Table 7 marks K-D2 as not well-formed at effects. Read as a manifestation
    pointer the two tables agree; read as a second crossing they do not. This
    test pins the reading so that the tension is visible if anyone changes it."""
    items = kernel.external_lists["fuller_1964"]["items"]
    arrowed = {i["desideratum"]: i for i in items if i.get("manifests_at")}
    assert set(arrowed) == {"Promulgation", "Possibility of compliance"}
    assert not kernel.is_well_formed("K-D2", "effects")
    assert kernel.is_well_formed("K-D3", "act")


def test_fuller_is_finer_grained_than_the_kernel_at_criteria(kernel):
    """Generality, clarity and constancy all collapse to K-A3. Recorded as a
    limitation of the kernel rather than explained away."""
    items = kernel.external_lists["fuller_1964"]["items"]
    collapsed = [i["desideratum"] for i in items if i["primitive"] == "K-A3"]
    assert sorted(collapsed) == ["Clarity", "Constancy through time", "Generality"]


# --------------------------------------------------------------------------
# Reporting discipline
# --------------------------------------------------------------------------


def test_every_typology_carries_its_reporting_constraints(kernel):
    typology = generate(chain("frcp"), kernel)
    assert typology["reporting_constraints"]
    assert any("not_applicable" not in c for c in typology["reporting_constraints"])


def test_undetectable_primitives_are_flagged_not_zeroed(kernel):
    typology = generate(chain("frcp"), kernel)
    firing = [c for c in typology["crossings"] if c["firing"] in ("fires", "rare")]
    undetectable = [c for c in firing if not c["detectable_in_this_release"]]
    assert undetectable, "most primitives have no detector; that must be visible"
    assert typology["counts"]["detectable_in_this_release"] < len(firing)


def test_k_d1_is_marked_permanently_unoperationalised(kernel):
    primitive = kernel.primitive("K-D1")
    assert primitive.operationalized is False
    assert "will not be" in primitive.operationalization_note


# --------------------------------------------------------------------------
# Chains
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(EXPECTED_PROFILES))
def test_chains_are_committed_before_detection(name):
    assert chain(name).committed_before_detection is True


def test_redacted_skeleton_strips_the_domain():
    skeleton = chain("frcp").redacted_skeleton()
    serialised = json.dumps(skeleton).lower()
    for term in ("federal", "rule", "court", "judgment", "civil"):
        assert term not in serialised
    assert set(skeleton["links"]) == set(CHAIN_LINKS)
