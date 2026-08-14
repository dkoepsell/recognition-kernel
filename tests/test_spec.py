"""Tests that the specification artifacts agree with the kernel data.

The kernel, the JSON schemas, and the OWL module are three statements of one
thing. These tests check that they remain three statements of one thing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from rkernel.validate import (
    check_kernel,
    check_owl_agreement,
    check_reasoning,
    check_schemas,
    run_all,
)
from rkernel import load_kernel

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def kernel():
    return load_kernel()


def test_kernel_check_passes(kernel):
    assert check_kernel(kernel)["ok"] is True


def test_kernel_and_chains_validate_against_their_schemas():
    result = check_schemas()
    if result["ok"] is None:
        pytest.skip(result["skipped"])
    assert result["ok"] is True, result["problems"]
    assert result["validated"] >= 5, "kernel plus every bundled chain"


def test_owl_locus_mask_agrees_with_the_kernel(kernel):
    result = check_owl_agreement(kernel)
    if result["ok"] is None:
        pytest.skip(result["skipped"])
    assert result["ok"] is True, result
    assert result["exclusions_in_owl"] == result["exclusions_in_kernel"] == 17


def test_the_gating_rule_is_enforced_not_merely_documented():
    """The load-bearing check. Asserting a Stratum D crossing at an absent link
    must make the ontology inconsistent under a reasoner."""
    result = check_reasoning()
    if result["ok"] is None:
        pytest.skip(result.get("skipped", "reasoner unavailable"))
    assert result["example_abox" if "example_abox" in result else "example-abox"] == "consistent"
    assert result["gating-violation"] == "inconsistent"
    assert result["ok"] is True, result["problems"]


def test_run_all_reports_ok():
    report = run_all()
    assert report["ok"] is True
    assert "Validation report" in report["markdown"]


def test_owl_module_is_regenerable_and_unchanged():
    """The OWL module is generated from kernel.json. If regenerating it changes
    the file, the checked-in copy is stale."""
    import subprocess
    import sys

    ttl = ROOT / "spec" / "owl" / "recognition-kernel.ttl"
    if not ttl.is_file():
        pytest.skip("spec/owl not present")
    before = ttl.read_text(encoding="utf-8")
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "build_owl.py")],
        check=True, capture_output=True,
    )
    assert ttl.read_text(encoding="utf-8") == before, (
        "spec/owl/recognition-kernel.ttl is stale; run tools/build_owl.py and commit"
    )


def test_every_primitive_documented_in_primitives_md(kernel):
    doc = (ROOT / "spec" / "PRIMITIVES.md").read_text(encoding="utf-8")
    for primitive in kernel.primitives:
        assert f"### {primitive.id} " in doc, primitive.id


def test_spec_records_the_grid_total(kernel):
    """The 69/70 discrepancy must stay visible in the prose spec."""
    doc = (ROOT / "spec" / "SPEC.md").read_text(encoding="utf-8")
    assert "70 of 84" in doc
    assert "sixty-nine" in doc
