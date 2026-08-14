"""The contradiction kernel: twelve domain-neutral primitives in four strata.

The kernel is data, not code. `data/kernel.json` is the single source of truth;
this module loads it, validates it, and exposes it. The OWL module and the
human-readable specification are checked against the same file by the test
suite, so the three cannot drift apart silently.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Literal

FiringValue = Literal["fires", "rare", "cannot_fire", "no_locus", "not_applicable"]
LinkStatus = Literal["internal", "external", "absent"]

#: Ordering used when summarising a stratum over its loci. Strongest wins.
#:
#: The three weakest values are all "did not fire", and they are weak for three
#: different reasons, ranked by how much structure is present. `not_applicable`
#: says the coordinate does not exist: the crossing is not well-formed, in any
#: system. `no_locus` says the coordinate exists and this system has no link at
#: it. `cannot_fire` says the link exists and the primitive is barred there.
FIRING_ORDER: dict[str, int] = {
    "not_applicable": 0,
    "no_locus": 1,
    "cannot_fire": 2,
    "rare": 3,
    "fires": 4,
}

#: The seven links of the recognition chain, in chain order.
CHAIN_LINKS: tuple[str, ...] = (
    "authority",
    "criteria",
    "assessor",
    "facts",
    "act",
    "effects",
    "remedy",
)


def _package_root() -> Path:
    return Path(__file__).resolve().parent


def default_kernel_path() -> Path:
    """Locate data/kernel.json whether running from a source tree or installed."""
    candidates = [
        _package_root() / "data" / "kernel.json",          # installed (package data)
        _package_root().parents[1] / "data" / "kernel.json",  # src layout
        Path.cwd() / "data" / "kernel.json",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "kernel.json not found. Looked in: " + ", ".join(str(c) for c in candidates)
    )


@dataclass(frozen=True)
class Locus:
    id: str
    label: str
    definition: str
    pseudo_locus: bool = False
    rationale: str = ""


@dataclass(frozen=True)
class Stratum:
    id: str
    label: str
    precondition: str
    gated: bool
    definition: str = ""


@dataclass(frozen=True)
class Primitive:
    id: str
    stratum: str
    name: str
    definition: str
    well_formed_at: tuple[str, ...]
    excluded_at: tuple[str, ...] = ()
    formal_signature: str = ""
    instrument: str = ""
    well_formedness_rationale: str = ""
    precedents: tuple[str, ...] = ()
    operationalized: bool | str = False
    operationalization_note: str = ""

    def is_well_formed_at(self, locus: str) -> bool:
        return locus in self.well_formed_at

    @property
    def detectable_in_this_release(self) -> bool:
        return self.operationalized is True or self.operationalized == "partial"


@dataclass(frozen=True)
class NamedType:
    key: str
    label: str
    primitive: str
    locus: str
    system_kind: str | None = None
    reading: str | None = None
    source: str | None = None


@dataclass
class Kernel:
    kernel_version: str
    loci: list[Locus]
    strata: list[Stratum]
    primitives: list[Primitive]
    gating_rule: dict
    named_types: list[NamedType] = field(default_factory=list)
    external_lists: dict = field(default_factory=dict)
    admission_criteria: dict = field(default_factory=dict)
    source: str = ""

    # -- lookups -------------------------------------------------------------

    def locus(self, locus_id: str) -> Locus:
        for locus in self.loci:
            if locus.id == locus_id:
                return locus
        raise KeyError(f"unknown locus: {locus_id}")

    def primitive(self, primitive_id: str) -> Primitive:
        for primitive in self.primitives:
            if primitive.id == primitive_id:
                return primitive
        raise KeyError(f"unknown primitive: {primitive_id}")

    def stratum(self, stratum_id: str) -> Stratum:
        for stratum in self.strata:
            if stratum.id == stratum_id:
                return stratum
        raise KeyError(f"unknown stratum: {stratum_id}")

    def primitives_in(self, stratum_id: str) -> list[Primitive]:
        return [p for p in self.primitives if p.stratum == stratum_id]

    @property
    def chain_loci(self) -> list[Locus]:
        """The seven links, excluding the artifact pseudo-locus."""
        return [locus for locus in self.loci if not locus.pseudo_locus]

    @property
    def pseudo_loci(self) -> list[Locus]:
        return [locus for locus in self.loci if locus.pseudo_locus]

    def is_gated(self, primitive_id: str) -> bool:
        return self.stratum(self.primitive(primitive_id).stratum).gated

    def named_type_at(
        self, primitive_id: str, locus_id: str, system_kind: str | None = None
    ) -> NamedType | None:
        """Return a named type registered at these coordinates, if any.

        A type registered for a specific system kind matches only that kind;
        a type registered with no kind matches any.
        """
        fallback = None
        for named in self.named_types:
            if named.primitive != primitive_id or named.locus != locus_id:
                continue
            if named.system_kind is None:
                fallback = fallback or named
            elif named.system_kind == system_kind:
                return named
        return fallback

    # -- well-formedness -----------------------------------------------------

    def is_well_formed(self, primitive_id: str, locus_id: str) -> bool:
        """A crossing is well-formed when the locus supplies the structure the
        primitive presupposes (paper §7.2)."""
        return self.primitive(primitive_id).is_well_formed_at(locus_id)

    def grid_cells(self, loci: Iterable[str] | None = None) -> int:
        loci = list(loci) if loci is not None else [locus.id for locus in self.loci]
        return len(self.primitives) * len(loci)

    def well_formed_cells(self, loci: Iterable[str] | None = None) -> int:
        loci = list(loci) if loci is not None else [locus.id for locus in self.loci]
        return sum(
            1
            for primitive in self.primitives
            for locus in loci
            if primitive.is_well_formed_at(locus)
        )

    # -- gating --------------------------------------------------------------

    def firing_value(self, primitive_id: str, locus_id: str, status: LinkStatus | None) -> FiringValue:
        """Apply the gating rule (paper §8.1).

        Strata A, B and C are ungated: their preconditions live inside the
        artifact, so they fire wherever the locus exists at all. Stratum D is
        gated three ways by the status of the link.

        `status` is None for pseudo-loci, which are present unconditionally and
        treated as internal for ungated strata and as absent for Stratum D.
        """
        if not self.is_well_formed(primitive_id, locus_id):
            return "not_applicable"

        gated = self.is_gated(primitive_id)
        if status is None:  # pseudo-locus
            status = "absent" if gated else "internal"

        table = self.gating_rule["values"] if gated else self.gating_rule["ungated_values"]
        return table[status]  # type: ignore[return-value]

    # -- construction --------------------------------------------------------

    @classmethod
    def from_dict(cls, raw: dict) -> "Kernel":
        return cls(
            kernel_version=raw["kernel_version"],
            source=raw.get("source", ""),
            loci=[
                Locus(
                    id=item["id"],
                    label=item["label"],
                    definition=item["definition"],
                    pseudo_locus=item.get("pseudo_locus", False),
                    rationale=item.get("rationale", ""),
                )
                for item in raw["loci"]
            ],
            strata=[
                Stratum(
                    id=item["id"],
                    label=item["label"],
                    precondition=item["precondition"],
                    gated=item["gated"],
                    definition=item.get("definition", ""),
                )
                for item in raw["strata"]
            ],
            primitives=[
                Primitive(
                    id=item["id"],
                    stratum=item["stratum"],
                    name=item["name"],
                    definition=item["definition"],
                    well_formed_at=tuple(item["well_formed_at"]),
                    excluded_at=tuple(item.get("excluded_at", ())),
                    formal_signature=item.get("formal_signature", ""),
                    instrument=item.get("instrument", ""),
                    well_formedness_rationale=item.get("well_formedness_rationale", ""),
                    precedents=tuple(item.get("precedents", ())),
                    operationalized=item.get("operationalized", False),
                    operationalization_note=item.get("operationalization_note", ""),
                )
                for item in raw["primitives"]
            ],
            gating_rule=raw["gating_rule"],
            named_types=[
                NamedType(
                    key=item["key"],
                    label=item["label"],
                    primitive=item["primitive"],
                    locus=item["locus"],
                    system_kind=item.get("system_kind"),
                    reading=item.get("reading"),
                    source=item.get("source"),
                )
                for item in raw.get("named_types", [])
            ],
            external_lists=raw.get("external_lists", {}),
            admission_criteria=raw.get("admission_criteria", {}),
        )

    def self_check(self) -> list[str]:
        """Internal consistency checks. Returns a list of problems, empty if clean."""
        problems: list[str] = []
        locus_ids = {locus.id for locus in self.loci}
        stratum_ids = {stratum.id for stratum in self.strata}

        for primitive in self.primitives:
            if primitive.stratum not in stratum_ids:
                problems.append(f"{primitive.id}: unknown stratum {primitive.stratum}")
            unknown = set(primitive.well_formed_at) - locus_ids
            if unknown:
                problems.append(f"{primitive.id}: well_formed_at names unknown loci {sorted(unknown)}")
            overlap = set(primitive.well_formed_at) & set(primitive.excluded_at)
            if overlap:
                problems.append(f"{primitive.id}: locus in both well_formed_at and excluded_at: {sorted(overlap)}")
            covered = set(primitive.well_formed_at) | set(primitive.excluded_at)
            if covered != locus_ids:
                missing = sorted(locus_ids - covered)
                problems.append(f"{primitive.id}: loci neither included nor excluded: {missing}")

        for named in self.named_types:
            if not self.is_well_formed(named.primitive, named.locus):
                problems.append(
                    f"named type {named.key} sits at a crossing that is not well-formed: "
                    f"{named.primitive} x {named.locus}"
                )
        return problems


@lru_cache(maxsize=8)
def load_kernel(path: str | Path | None = None) -> Kernel:
    """Load and cache the kernel. Pass a path to use a variant kernel."""
    resolved = Path(path) if path else default_kernel_path()
    with resolved.open(encoding="utf-8") as handle:
        raw = json.load(handle)
    return Kernel.from_dict(raw)
