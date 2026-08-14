"""Lexicons for the rule-based extractors.

The central discipline enforced here is **vocabulary disjointness**. The K-D3
pathway matcher must satisfy two independent conditions: that a provision is
*about the same capacity*, and that it *supplies a procedural marker*. If one
vocabulary establishes both, every procedural provision resembles every
capacity and the detector measures the density of procedural language rather
than the presence of pathways. That failure is documented in the paper at
§11.2; the fix is specified at §10.1 and implemented here.

`assert_disjoint()` is called at import time. The vocabularies cannot silently
drift back into overlap.
"""

from __future__ import annotations

import re

# --------------------------------------------------------------------------
# Condition 2 vocabulary: what makes a provision a *pathway*.
# Excluded from topical matching by construction.
# --------------------------------------------------------------------------

PROCEDURAL_MARKERS: frozenset[str] = frozenset({
    # filing and service
    "file", "files", "filed", "filing", "serve", "serves", "served", "service",
    "submit", "submits", "submitted", "submission", "lodge", "lodged",
    # instruments of invocation
    "motion", "motions", "petition", "petitions", "application", "applications",
    "request", "requests", "requested", "demand", "demands",
    # notice and recipients
    "notice", "notify", "notified", "notification",
    # adjudicative response
    "hearing", "hearings", "order", "orders", "ordered", "entry", "entered",
    "docket", "docketed", "ruling", "rules",
    # timing
    "deadline", "within", "days", "day", "promptly", "forthwith", "time",
    "before", "after", "later",
    # form
    "form", "forms", "affidavit", "affidavits", "declaration", "certificate",
    "writing", "written", "signed", "signature",
})

# --------------------------------------------------------------------------
# Function words. Removed from every content comparison.
# --------------------------------------------------------------------------

STOPWORDS: frozenset[str] = frozenset({
    "a", "an", "the", "and", "or", "but", "if", "then", "than", "that", "this",
    "these", "those", "of", "to", "in", "on", "at", "by", "for", "with", "as",
    "is", "are", "was", "were", "be", "been", "being", "it", "its", "not", "no",
    "any", "all", "each", "such", "same", "other", "another", "may", "must",
    "shall", "should", "will", "would", "can", "could", "have", "has", "had",
    "do", "does", "did", "from", "into", "under", "upon", "about", "which",
    "who", "whom", "whose", "when", "where", "what", "unless", "until", "so",
    "also", "only", "more", "most", "less", "least", "one", "two", "part",
    "subdivision", "paragraph", "subparagraph", "rule",
})

# --------------------------------------------------------------------------
# Actors: candidate bearers of a norm.
# --------------------------------------------------------------------------

ACTORS: tuple[str, ...] = (
    "the court", "a court", "the clerk", "the judge", "the magistrate judge",
    "the plaintiff", "a plaintiff", "the defendant", "a defendant",
    "the party", "a party", "the parties", "any party", "each party",
    "the movant", "the moving party", "the opposing party", "the nonmovant",
    "the attorney", "an attorney", "counsel", "the marshal", "the officer",
    "a person", "the person", "any person", "a witness", "the witness",
    "the jury", "a juror", "the appellant", "the appellee", "the intervenor",
    "the claimant", "the respondent", "the petitioner", "the deponent",
    "the certifying agent", "the certifying body", "the accreditor",
    "the clinician", "the examiner", "the registrar", "the board",
    "the agency", "the administrator", "the secretary",
)

# --------------------------------------------------------------------------
# Modality cues.
# --------------------------------------------------------------------------

PROHIBITION_CUES: tuple[str, ...] = (
    "must not", "shall not", "may not", "cannot", "is prohibited", "are prohibited",
    "is not permitted", "no ... may",
)

DUTY_CUES: tuple[str, ...] = (
    "must", "shall", "is required to", "are required to", "has the duty",
    "is obligated to",
)

PERMISSION_CUES: tuple[str, ...] = ("may", "is permitted to", "are permitted to")

POWER_CUES: tuple[str, ...] = (
    "is entitled to", "has the right to", "may, on motion,", "on motion",
    "in its discretion", "sua sponte",
)

#: Verbs whose performance changes a normative position rather than merely
#: describing conduct. `may` plus one of these reads as a conferred capacity.
POWER_VERBS: frozenset[str] = frozenset({
    "move", "appeal", "object", "intervene", "amend", "join", "implead",
    "remove", "elect", "waive", "seek", "strike", "compel", "certify",
    "grant", "appoint", "dismiss", "sanction", "extend", "modify", "vacate",
    "reopen", "sever", "consolidate", "transfer", "stay", "enjoin", "quash",
    "set", "aside", "assert", "claim", "counterclaim", "crossclaim", "raise",
    "recover", "enforce", "revoke", "suspend", "decertify", "withdraw",
    "reconsider", "review", "reverse", "correct", "relieve", "excuse",
    "authorize", "permit", "allow", "deny", "refuse", "reject", "accept",
    "designate", "nominate", "substitute", "add", "drop", "bring", "commence",
    "institute", "initiate", "terminate", "dissolve", "issue", "impose",
    "sue", "implead", "interplead", "certify", "recover", "amend", "join",
    "abate", "discharge", "release", "settle", "compromise", "object",
})

# --------------------------------------------------------------------------
# References to instruments outside the corpus. A capacity whose pathway lies
# in one of these is recorded as *external* and reported separately: it cannot
# be scored as a source-level failure (paper §10.1).
# --------------------------------------------------------------------------

EXTERNAL_INSTRUMENT_PATTERNS: tuple[str, ...] = (
    r"\bU\.?S\.?C\.?\b",
    r"\bC\.?F\.?R\.?\b",
    r"\bstate\s+(law|statute|court|rule)\b",
    r"\bfederal\s+statute\b",
    r"\blocal\s+rule\b",
    r"\bapplicable\s+law\b",
    r"\bstatute\b",
    r"\btreaty\b",
    r"\bconstitution\b",
    r"\banother\s+(rule|title|act|chapter|part)\b",
    r"\bincorporated\s+by\s+reference\b",
    r"\bas\s+provided\s+by\s+law\b",
)

EXTERNAL_INSTRUMENT_RE = re.compile("|".join(EXTERNAL_INSTRUMENT_PATTERNS), re.IGNORECASE)

# --------------------------------------------------------------------------
# Cross-references inside the corpus, e.g. "Rule 26(c)(1)", "§ 205.405(a)".
# --------------------------------------------------------------------------

CROSSREF_RE = re.compile(
    r"(?:Rule|Rules|§|Section|Sec\.)\s*([0-9]+(?:\.[0-9]+)?(?:\([a-z0-9]+\))*)",
    re.IGNORECASE,
)

# --------------------------------------------------------------------------
# Ontological-claim cues, used by the entity-relation extractor. This is the
# instrument built for taxonomic structure; running it on a procedural code is
# the within-run control of paper §11.1.
# --------------------------------------------------------------------------

ONTOLOGICAL_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\bis\s+a\s+kind\s+of\b", "is_a"),
    (r"\bis\s+a\s+type\s+of\b", "is_a"),
    (r"\bis\s+a\s+subtype\s+of\b", "is_a"),
    (r"\bis\s+a\s+subclass\s+of\b", "is_a"),
    (r"\bare\s+kinds\s+of\b", "is_a"),
    (r"\bis\s+defined\s+as\b", "definition"),
    (r"\bis\s+a\s+form\s+of\b", "is_a"),
    (r"\bhas\s+part\b", "has_part"),
    (r"\bhas\s+parts\b", "has_part"),
    (r"\bis\s+part\s+of\b", "part_of"),
    (r"\bconsists\s+of\b", "has_part"),
    (r"\bis\s+composed\s+of\b", "has_part"),
    (r"\bdepends\s+on\b", "depends_on"),
    (r"\bis\s+dependent\s+on\b", "depends_on"),
    (r"\binheres\s+in\b", "inheres_in"),
    (r"\bparticipates\s+in\b", "participates_in"),
    (r"\bis\s+borne\s+by\b", "bearer_of"),
    (r"\bis\s+realized\s+in\b", "realized_in"),
)

# --------------------------------------------------------------------------
# Cues for classifying a provision to a chain link. Used by the chain
# extractor, whose output is a *draft* for an analyst, never a committed chain.
# --------------------------------------------------------------------------

LINK_CUES: dict[str, tuple[str, ...]] = {
    "authority": (
        "authority", "authorized", "empowered", "promulgat", "enacted",
        "pursuant to", "under the authority", "delegated", "jurisdiction",
        "governed by", "adopted by", "prescribed by",
    ),
    "criteria": (
        "criteria", "criterion", "standard", "requirement", "must meet",
        "qualifies", "eligible", "conditions for", "definition", "means",
        "threshold", "specification", "conformance",
    ),
    "assessor": (
        "the court", "the clerk", "the judge", "examiner", "officer",
        "certifying agent", "accredited", "designated", "appointed",
        "qualified", "licensed", "in the role of", "acting as",
    ),
    "facts": (
        "evidence", "showing", "affidavit", "testimony", "the facts",
        "presented", "alleged", "supporting", "record", "documentation",
        "exhibit", "finding of fact",
    ),
    "act": (
        "shall enter", "enters", "issues", "grants", "confers", "determines",
        "certifies", "declares", "adjudges", "renders", "judgment", "decision",
        "determination", "conferral", "diagnosis",
    ),
    "effects": (
        "shall be binding", "takes effect", "is entitled to", "liability",
        "entitlement", "consequence", "results in", "operates as",
        "is effective", "shall have the effect",
    ),
    "remedy": (
        "appeal", "review", "reconsider", "set aside", "vacate", "revoke",
        "suspend", "rescind", "reopen", "relief from", "may be challenged",
        "contest", "objection to", "petition for review", "decertif",
    ),
}


def assert_disjoint() -> None:
    """Fail loudly if the two matcher vocabularies overlap.

    Condition 1 (topical correspondence) is computed over content tokens;
    condition 2 (procedural marker) over PROCEDURAL_MARKERS. If a token could
    serve both, one test is doing the work of two.
    """
    overlap = PROCEDURAL_MARKERS & STOPWORDS
    if overlap:
        raise AssertionError(
            "PROCEDURAL_MARKERS and STOPWORDS overlap, which makes marker "
            f"detection depend on stopword removal order: {sorted(overlap)}"
        )
    power_overlap = PROCEDURAL_MARKERS & POWER_VERBS
    if power_overlap:
        raise AssertionError(
            "PROCEDURAL_MARKERS and POWER_VERBS overlap; a capacity would be "
            f"identified by the same vocabulary that identifies its pathway: {sorted(power_overlap)}"
        )


def content_tokens(text: str) -> set[str]:
    """Tokens available to condition 1: everything except stopwords, procedural
    markers, and bare numerals."""
    tokens = re.findall(r"[a-z]+", text.lower())
    return {
        token
        for token in tokens
        if len(token) > 2
        and token not in STOPWORDS
        and token not in PROCEDURAL_MARKERS
    }


def procedural_markers_in(text: str) -> set[str]:
    """Tokens available to condition 2."""
    tokens = set(re.findall(r"[a-z]+", text.lower()))
    return tokens & PROCEDURAL_MARKERS


assert_disjoint()
