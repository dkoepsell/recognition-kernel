"""The recognition chain: seven links, each internal, external, or absent.

The chain is the index set over which the kernel is instantiated. Its only
load-bearing content is the status of each link, which is what the gating rule
consumes. Everything else in a chain file is provenance.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from .kernel import CHAIN_LINKS, LinkStatus

SystemKind = Literal[
    "reference_ontology", "classification", "certification_scheme", "legal_order", "other"
]


@dataclass
class Link:
    id: str
    status: LinkStatus
    specification: str = ""
    filler: str = ""
    evidence: list[dict] = field(default_factory=list)
    confidence: str = ""
    note: str = ""

    @property
    def present(self) -> bool:
        return self.status != "absent"


@dataclass
class Chain:
    chain_id: str
    system: dict
    links: dict[str, Link]
    assigned_by: str = ""
    assigned_on: str = ""
    committed_before_detection: bool | None = None
    annotator_agreement: dict = field(default_factory=dict)
    provenance: str = ""

    # -- access --------------------------------------------------------------

    def status(self, link_id: str) -> LinkStatus:
        return self.links[link_id].status

    @property
    def label(self) -> str:
        return self.system.get("label", self.chain_id)

    @property
    def declared_kind(self) -> str | None:
        return self.system.get("declared_kind")

    # -- derived properties --------------------------------------------------

    @property
    def act_thickness(self) -> str:
        """act-thick / act-thin / act-empty, from the recognition act link alone."""
        return {
            "internal": "act-thick",
            "external": "act-thin",
            "absent": "act-empty",
        }[self.status("act")]

    @property
    def repair_thickness(self) -> str:
        return {
            "internal": "repair-internal",
            "external": "repair-external",
            "absent": "repair-absent",
        }[self.status("remedy")]

    @property
    def thickness_summary(self) -> str:
        return f"{self.act_thickness}, {self.repair_thickness}"

    @property
    def computed_kind(self) -> SystemKind:
        """Classify the system from link statuses alone (paper §8.3 Table 10).

        This is the readable-from-shape claim in executable form: no substantive
        rule of the system is consulted, only which links it performs for itself.
        """
        act = self.status("act")
        remedy = self.status("remedy")
        present = [link_id for link_id in CHAIN_LINKS if self.links[link_id].present]

        if not present:
            return "reference_ontology"
        if act == "internal" and remedy == "internal":
            return "legal_order"
        if act == "external" and remedy == "internal":
            return "certification_scheme"
        if act == "external" and remedy in ("external", "absent"):
            return "classification"
        if act == "absent":
            # Some links present but no recognition act of its own.
            return "reference_ontology"
        return "other"

    @property
    def kind_mismatch(self) -> bool:
        declared = self.declared_kind
        return bool(declared) and declared != self.computed_kind

    def redacted_skeleton(self) -> dict:
        """The structural skeleton used for blind profile prediction (paper §10.3).

        Domain identifiers, subject matter and substantive rules are stripped,
        leaving only who is empowered, what is applied, by whom, with what
        effect, and what recourse. Fillers are dropped because they name the
        domain; only statuses survive.
        """
        return {
            "skeleton_id": f"skel-{abs(hash(self.chain_id)) % 100000:05d}",
            "links": {link_id: self.links[link_id].status for link_id in CHAIN_LINKS},
        }

    # -- io ------------------------------------------------------------------

    @classmethod
    def from_dict(cls, raw: dict) -> "Chain":
        links = {}
        for link_id in CHAIN_LINKS:
            item = raw["links"][link_id]
            links[link_id] = Link(
                id=link_id,
                status=item["status"],
                specification=item.get("specification", ""),
                filler=item.get("filler", ""),
                evidence=item.get("evidence", []),
                confidence=item.get("confidence", ""),
                note=item.get("note", ""),
            )
        return cls(
            chain_id=raw["chain_id"],
            system=raw["system"],
            links=links,
            assigned_by=raw.get("assigned_by", ""),
            assigned_on=raw.get("assigned_on", ""),
            committed_before_detection=raw.get("committed_before_detection"),
            annotator_agreement=raw.get("annotator_agreement", {}),
            provenance=raw.get("provenance", ""),
        )

    @classmethod
    def load(cls, path: str | Path) -> "Chain":
        with Path(path).open(encoding="utf-8") as handle:
            return cls.from_dict(json.load(handle))

    def to_dict(self) -> dict:
        return {
            "chain_id": self.chain_id,
            "system": self.system,
            "assigned_by": self.assigned_by,
            "assigned_on": self.assigned_on,
            "committed_before_detection": self.committed_before_detection,
            "links": {
                link_id: {
                    "status": link.status,
                    "specification": link.specification,
                    "filler": link.filler,
                    "evidence": link.evidence,
                    "confidence": link.confidence,
                    "note": link.note,
                }
                for link_id, link in self.links.items()
            },
            "provenance": self.provenance,
        }
