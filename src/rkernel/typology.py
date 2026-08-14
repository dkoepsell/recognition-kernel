"""The product construction: typology = kernel x chain.

Given a domain's chain and the kernel, this module returns the full typology,
the gated profile, and the predicted failure modes. Nothing here is compiled by
observation: every cell is derived from a locus mask and a link status.
"""

from __future__ import annotations

import datetime as _dt
from dataclasses import asdict, dataclass
from typing import Iterable

from .chain import Chain
from .kernel import FIRING_ORDER, Kernel, load_kernel

GENERATOR = "rkernel.typology"
VERSION = "0.2.0"

REPORTING_CONSTRAINTS = [
    "Absence of a flag is not evidence of absence of the failure. Where a primitive was "
    "not operationalized, its cells are marked detectable_in_this_release=false and must "
    "never be reported as zero.",
    "A reasoner is necessary and never sufficient: half the kernel is invisible to "
    "description logic in principle, so a pipeline reporting only reasoner output has "
    "silently scored the rest as zero.",
    "Every finding carries a provenance field distinguishing defects in the source from "
    "defects in the translation of it, defaulting to undetermined rather than to source.",
    "Firing values are predictions about what can occur, not detections of what has. A "
    "cell marked 'fires' asserts possibility, not incidence.",
]


@dataclass
class Crossing:
    primitive: str
    stratum: str
    locus: str
    link_status: str | None
    well_formed: bool
    well_formedness_reason: str
    firing: str
    gated: bool
    named_type: str | None
    named_type_label: str | None
    instrument: str | None
    operationalized: bool | str
    detectable_in_this_release: bool


def generate(chain: Chain, kernel: Kernel | None = None) -> dict:
    """Return the full typology for one chain as a plain dict.

    The dict validates against spec/schema/typology.schema.json.
    """
    kernel = kernel or load_kernel()
    computed_kind = chain.computed_kind

    crossings: list[Crossing] = []
    for primitive in kernel.primitives:
        for locus in kernel.loci:
            status = None if locus.pseudo_locus else chain.status(locus.id)
            well_formed = primitive.is_well_formed_at(locus.id)
            firing = kernel.firing_value(primitive.id, locus.id, status)
            named = kernel.named_type_at(primitive.id, locus.id, computed_kind)
            if well_formed:
                reason = primitive.well_formedness_rationale
            else:
                reason = (
                    f"{locus.label} does not supply the structure {primitive.id} "
                    f"presupposes. {primitive.well_formedness_rationale}"
                ).strip()
            crossings.append(
                Crossing(
                    primitive=primitive.id,
                    stratum=primitive.stratum,
                    locus=locus.id,
                    link_status=status,
                    well_formed=well_formed,
                    well_formedness_reason=reason,
                    firing=firing,
                    gated=kernel.is_gated(primitive.id),
                    named_type=named.key if named else None,
                    named_type_label=named.label if named else None,
                    instrument=primitive.instrument or None,
                    operationalized=primitive.operationalized,
                    detectable_in_this_release=primitive.detectable_in_this_release,
                )
            )

    # The stratum summary. Ungated strata take the strongest value over their
    # well-formed loci, which is always `fires` for an artifact that exists.
    # Gated strata are summarised at the recognition act locus rather than by a
    # maximum, because Stratum D is the stratum of acts and the act link is its
    # natural index. Taking a maximum instead would report `fires` for any
    # system with one internal link anywhere, which would collapse precisely
    # the distinction the gating rule is about. The per-locus profile below
    # keeps the detail the summary discards, and it is where the certification
    # and classification cases visibly differ even when their summaries agree.
    profile: dict[str, str] = {}
    for stratum in kernel.strata:
        stratum_crossings = [
            crossing
            for crossing in crossings
            if crossing.stratum == stratum.id and crossing.well_formed
        ]
        if not stratum_crossings:
            profile[stratum.id] = "not_applicable"
            continue
        if stratum.gated:
            at_act = [c.firing for c in stratum_crossings if c.locus == "act"]
            profile[stratum.id] = (
                at_act[0]
                if at_act
                else max((c.firing for c in stratum_crossings), key=lambda v: FIRING_ORDER[v])
            )
        else:
            profile[stratum.id] = max(
                (c.firing for c in stratum_crossings), key=lambda v: FIRING_ORDER[v]
            )

    profile_by_locus: dict[str, dict[str, str]] = {}
    for stratum in kernel.strata:
        row: dict[str, str] = {}
        for locus in kernel.loci:
            values = [
                crossing.firing
                for crossing in crossings
                if crossing.stratum == stratum.id
                and crossing.locus == locus.id
                and crossing.well_formed
            ]
            row[locus.id] = (
                max(values, key=lambda value: FIRING_ORDER[value]) if values else "not_applicable"
            )
        profile_by_locus[stratum.id] = row

    predicted = []
    for crossing in sorted(
        (c for c in crossings if c.firing in ("fires", "rare")),
        key=lambda c: (-FIRING_ORDER[c.firing], c.stratum, c.primitive, c.locus),
    ):
        named = kernel.named_type_at(crossing.primitive, crossing.locus, computed_kind)
        predicted.append(
            {
                "primitive": crossing.primitive,
                "primitive_name": kernel.primitive(crossing.primitive).name,
                "stratum": crossing.stratum,
                "locus": crossing.locus,
                "firing": crossing.firing,
                "named_type": crossing.named_type,
                "reading": named.reading if named else None,
                "instrument": crossing.instrument,
                "detectable_in_this_release": crossing.detectable_in_this_release,
            }
        )

    counts = {
        "loci_total": len(kernel.loci),
        "chain_loci_total": len(kernel.chain_loci),
        "primitives_total": len(kernel.primitives),
        "cells_total": len(crossings),
        "well_formed": sum(1 for c in crossings if c.well_formed),
        "fires": sum(1 for c in crossings if c.firing == "fires"),
        "rare": sum(1 for c in crossings if c.firing == "rare"),
        "cannot_fire": sum(1 for c in crossings if c.firing == "cannot_fire"),
        "no_locus": sum(1 for c in crossings if c.firing == "no_locus"),
        "not_applicable": sum(1 for c in crossings if c.firing == "not_applicable"),
        "detectable_in_this_release": sum(
            1 for c in crossings if c.firing in ("fires", "rare") and c.detectable_in_this_release
        ),
        "named_types_located": sum(1 for c in crossings if c.named_type and c.well_formed),
    }

    return {
        "generated_by": f"{GENERATOR} {VERSION}",
        "generated_on": _dt.date.today().isoformat(),
        "kernel_version": kernel.kernel_version,
        "chain_id": chain.chain_id,
        "system_label": chain.label,
        "declared_kind": chain.declared_kind,
        "computed_kind": computed_kind,
        "kind_mismatch": chain.kind_mismatch,
        "chain_thickness": {
            "act": chain.act_thickness,
            "repair": chain.repair_thickness,
            "summary": chain.thickness_summary,
        },
        "crossings": [asdict(c) for c in crossings],
        "profile": profile,
        "profile_by_locus": profile_by_locus,
        "profile_summary_rule": (
            "Ungated strata are summarised by the strongest value over their well-formed "
            "loci. Gated strata are summarised at the recognition act locus, since Stratum "
            "D is the stratum of acts. Consult profile_by_locus before comparing two "
            "systems: two systems can share a summary and differ at remedy, which is the "
            "difference between a classification and a certification scheme."
        ),
        "predicted_failure_modes": predicted,
        "counts": counts,
        "reporting_constraints": REPORTING_CONSTRAINTS,
    }


def reference_grid(kernel: Kernel | None = None, loci: Iterable[str] | None = None) -> dict:
    """The kernel's own well-formedness grid, independent of any chain.

    This is Table 7 of the paper when restricted to the seven chain loci: the
    product for a system in which every link is internal.
    """
    kernel = kernel or load_kernel()
    locus_ids = list(loci) if loci is not None else [locus.id for locus in kernel.chain_loci]
    rows = {}
    for primitive in kernel.primitives:
        rows[primitive.id] = {
            locus_id: primitive.is_well_formed_at(locus_id) for locus_id in locus_ids
        }
    return {
        "kernel_version": kernel.kernel_version,
        "loci": locus_ids,
        "primitives": [p.id for p in kernel.primitives],
        "rows": rows,
        "cells_total": len(kernel.primitives) * len(locus_ids),
        "well_formed": kernel.well_formed_cells(locus_ids),
    }


def compare(typologies: list[dict]) -> dict:
    """Line up several generated typologies for the contrast table of §8.3."""
    return {
        "systems": [
            {
                "chain_id": typology["chain_id"],
                "label": typology["system_label"],
                "computed_kind": typology["computed_kind"],
                "thickness": typology["chain_thickness"]["summary"],
                "profile": typology["profile"],
                "profile_by_locus": typology["profile_by_locus"],
                "fires": typology["counts"]["fires"],
                "rare": typology["counts"]["rare"],
                "cannot_fire": typology["counts"]["cannot_fire"],
                "well_formed": typology["counts"]["well_formed"],
            }
            for typology in typologies
        ]
    }
