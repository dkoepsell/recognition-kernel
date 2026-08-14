"""rkernel: a reference implementation of the contradiction kernel.

    typology = kernel x chain

Three things are released here: the kernel as a formal specification (OWL, JSON
Schema, prose, worked examples), a rule-based chain and norm extractor with a
K-D3 detector, and a domain typology generator that takes a chain and returns
the full typology, the gated profile, and the predicted failure modes.

Reference: Koepsell, D. R., *The Recognition Layer: A Generative Typology of
Structural Contradiction for Recognition-Constituted Domains* (working draft).
"""

from __future__ import annotations

import json
from pathlib import Path

from .chain import Chain
from .kernel import Kernel, load_kernel
from .typology import generate, reference_grid, compare

__version__ = "0.2.0"

__all__ = [
    "Chain",
    "Kernel",
    "load_kernel",
    "generate",
    "reference_grid",
    "compare",
    "load_corpus",
    "__version__",
]


def load_corpus(path: str | Path):
    """Load a demo corpus file into Provision objects.

    A corpus file is a JSON object with a `provisions` array; each provision has
    `id`, `locator`, and `text`. Provenance fields are preserved on the object
    but are not consumed by the extractors.
    """
    from .extract.norms import Provision

    with Path(path).open(encoding="utf-8") as handle:
        raw = json.load(handle)
    return [
        Provision(
            id=item["id"],
            locator=item["locator"],
            text=item["text"],
            chunk=item.get("chunk"),
            heading=item.get("heading", ""),
        )
        for item in raw["provisions"]
    ], raw.get("meta", {})
