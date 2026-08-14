"""Extractors: norm tuples, ontological claims, chain drafts, K-D3 detection."""

from .norms import NormTuple, Provision, extract_norms, summarize  # noqa: F401
from .ontological import extract_claims, control_report  # noqa: F401
from .kd3 import MatcherConfig, detect, fan_out_report  # noqa: F401
from .chain_extract import draft_chain, score_links  # noqa: F401

__all__ = [
    "Provision",
    "NormTuple",
    "extract_norms",
    "summarize",
    "extract_claims",
    "control_report",
    "MatcherConfig",
    "detect",
    "fan_out_report",
    "draft_chain",
    "score_links",
]
