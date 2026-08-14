"""Norm-tuple extractor for deontic corpora.

Extracts tuples of the form

    (bearer, modality, action, conditions, deadline, counterparty)

with modality in {duty, prohibition, permission, power}. Power tuples are the
*capacities* consumed by the K-D3 detector.

The extractor is rule-based and has no required dependencies. If spaCy is
installed and a model is available, `use_spacy=True` improves bearer
identification by using noun chunks; results are otherwise identical in shape.

Why a separate extractor exists at all: an extractor built for ontological
claims returns nothing on a procedural code, because a procedural code contains
almost no assertions about kinds. That is a precondition mismatch, not poor
performance, and `rkernel.extract.ontological` reproduces it as a control.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass, field
from typing import Iterable

from .lexicon import ACTORS, POWER_VERBS

MODALITIES = ("duty", "prohibition", "permission", "power")

_SENTENCE_RE = re.compile(r"(?<=[.;:])\s+(?=[A-Z(])|\n+")
_DEADLINE_RE = re.compile(
    r"(within\s+\d+\s+days?|no\s+later\s+than[^,.;]{0,60}|"
    r"at\s+least\s+\d+\s+days?\s+(?:before|after)[^,.;]{0,40}|"
    r"promptly|forthwith|before\s+trial|at\s+the\s+time[^,.;]{0,30})",
    re.IGNORECASE,
)
_CONDITION_RE = re.compile(
    r"\b(if|unless|when|whenever|where|upon|after|on\s+motion|provided\s+that|"
    r"in\s+the\s+event)\b([^,.;]{0,120})",
    re.IGNORECASE,
)
_COUNTERPARTY_RE = re.compile(
    r"\b(?:on|to|upon|against|with)\s+((?:the|a|an|any|each|every)\s+"
    r"(?:opposing\s+|moving\s+|adverse\s+)?"
    r"(?:court|clerk|party|parties|plaintiff|defendant|attorney|person|"
    r"witness|deponent|claimant|respondent|petitioner|agency|board|"
    r"administrator|secretary|certifying\s+agent))",
    re.IGNORECASE,
)

_PROHIBITION_RE = re.compile(
    r"\b(must\s+not|shall\s+not|may\s+not|cannot|is\s+prohibited|are\s+prohibited|"
    r"is\s+not\s+permitted)\b",
    re.IGNORECASE,
)
_DUTY_RE = re.compile(
    r"\b(must|shall|is\s+required\s+to|are\s+required\s+to|has\s+the\s+duty\s+to|"
    r"is\s+obligated\s+to)\b",
    re.IGNORECASE,
)
_PERMISSIVE_RE = re.compile(
    r"\b(may|is\s+permitted\s+to|are\s+permitted\s+to|is\s+entitled\s+to|"
    r"has\s+the\s+right\s+to|is\s+authorized\s+to)\b",
    re.IGNORECASE,
)
_EXPLICIT_POWER_RE = re.compile(
    r"\b(is\s+entitled\s+to|has\s+the\s+right\s+to|is\s+authorized\s+to|"
    r"in\s+its\s+discretion|sua\s+sponte)\b",
    re.IGNORECASE,
)


@dataclass
class Provision:
    """One addressable unit of a corpus: a rule, section, or subdivision."""

    id: str
    locator: str
    text: str
    chunk: int | None = None
    heading: str = ""

    @property
    def rule_number(self) -> str:
        match = re.match(r"(?:Rule\s*)?(\d+(?:\.\d+)?)", self.locator, re.IGNORECASE)
        return match.group(1) if match else self.locator


@dataclass
class NormTuple:
    norm_id: str
    provision_id: str
    locator: str
    modality: str
    bearer: str | None
    action: str
    conditions: list[str] = field(default_factory=list)
    deadline: str | None = None
    counterparty: str | None = None
    quote: str = ""
    quote_hash: str = ""
    duplicate_of: str | None = None

    @property
    def is_capacity(self) -> bool:
        return self.modality == "power"


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _sentences(text: str) -> list[str]:
    return [_normalize(part) for part in _SENTENCE_RE.split(text) if _normalize(part)]


def _find_bearer(sentence: str, modal_start: int, spacy_doc=None) -> str | None:
    head = sentence[:modal_start].lower()
    best: tuple[int, str] | None = None
    for actor in ACTORS:
        index = head.rfind(actor)
        if index != -1 and (best is None or index > best[0]):
            best = (index, actor)
    if best:
        return best[1]
    if spacy_doc is not None:  # pragma: no cover - optional dependency
        chunks = [chunk.text for chunk in spacy_doc.noun_chunks if chunk.start_char < modal_start]
        if chunks:
            return chunks[-1]
    fallback = _normalize(sentence[:modal_start])
    fallback = re.split(r"[,;]", fallback)[-1].strip()
    return fallback.lower() or None


def _stems(word: str) -> set[str]:
    """Crude morphological variants. Enough to catch `joined` for `join`.

    A lemmatizer would be better; spaCy supplies one when installed. This
    fallback keeps the extractor dependency-free, and its failure mode is
    under-recall rather than over-recall, which is the right direction for a
    detector whose candidates are inspected by hand.
    """
    forms = {word}
    for suffix, replacement in (("ies", "y"), ("ed", ""), ("ing", ""), ("es", ""), ("s", "")):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            stem = word[: len(word) - len(suffix)] + replacement
            forms.add(stem)
            forms.add(stem + "e")
    return forms


def _is_power_verb(word: str) -> bool:
    return bool(_stems(word) & POWER_VERBS)


def _classify_modality(sentence: str) -> tuple[str, int, int] | None:
    """Return (modality, match_start, match_end) for the governing modal."""
    prohibition = _PROHIBITION_RE.search(sentence)
    if prohibition:
        return "prohibition", prohibition.start(), prohibition.end()

    permissive = _PERMISSIVE_RE.search(sentence)
    duty = _DUTY_RE.search(sentence)

    if permissive and (not duty or permissive.start() <= duty.start()):
        tail = sentence[permissive.end():].lower()
        first_verbs = re.findall(r"[a-z]+", tail)[:5]
        explicit = _EXPLICIT_POWER_RE.search(sentence)
        if explicit or any(_is_power_verb(verb) for verb in first_verbs):
            return "power", permissive.start(), permissive.end()
        return "permission", permissive.start(), permissive.end()

    if duty:
        return "duty", duty.start(), duty.end()
    return None


def extract_norms(
    provisions: Iterable[Provision],
    use_spacy: bool = False,
    dedupe: bool = True,
) -> list[NormTuple]:
    """Extract norm tuples from provisions.

    Byte-identical quotes are collapsed when `dedupe` is set. The paper reports
    a pair of findings at Rule 18(b) and Rule 19 carrying byte-identical source
    quotes from adjacent chunks, which were one norm counted twice under a
    mis-assigned locator (§11.2). Deduplication is on by default for that
    reason, and every collapsed tuple retains a pointer to its survivor.
    """
    nlp = None
    if use_spacy:  # pragma: no cover - optional dependency
        try:
            import spacy

            nlp = spacy.load("en_core_web_sm")
        except Exception:
            nlp = None

    norms: list[NormTuple] = []
    seen: dict[str, str] = {}

    for provision in provisions:
        for index, sentence in enumerate(_sentences(provision.text)):
            classified = _classify_modality(sentence)
            if not classified:
                continue
            modality, modal_start, modal_end = classified

            doc = nlp(sentence) if nlp else None  # pragma: no cover
            bearer = _find_bearer(sentence, modal_start, doc)
            action = _normalize(sentence[modal_end:]) or _normalize(sentence)
            conditions = [
                _normalize(f"{cue} {rest}") for cue, rest in _CONDITION_RE.findall(sentence)
            ]
            deadline_match = _DEADLINE_RE.search(sentence)
            counterparty_match = _COUNTERPARTY_RE.search(sentence[modal_end:])

            quote = sentence
            quote_hash = hashlib.sha1(quote.encode("utf-8")).hexdigest()[:12]
            norm_id = f"{provision.id}#n{index}"

            duplicate_of = None
            if dedupe and quote_hash in seen:
                duplicate_of = seen[quote_hash]
            elif dedupe:
                seen[quote_hash] = norm_id

            norms.append(
                NormTuple(
                    norm_id=norm_id,
                    provision_id=provision.id,
                    locator=provision.locator,
                    modality=modality,
                    bearer=bearer,
                    action=action[:400],
                    conditions=conditions,
                    deadline=_normalize(deadline_match.group(0)) if deadline_match else None,
                    counterparty=(
                        _normalize(counterparty_match.group(1)) if counterparty_match else None
                    ),
                    quote=quote,
                    quote_hash=quote_hash,
                    duplicate_of=duplicate_of,
                )
            )

    return norms


def summarize(norms: list[NormTuple]) -> dict:
    counts = {modality: 0 for modality in MODALITIES}
    for norm in norms:
        if norm.duplicate_of is None:
            counts[norm.modality] += 1
    return {
        "tuples_total": len(norms),
        "tuples_unique": sum(1 for norm in norms if norm.duplicate_of is None),
        "duplicates_collapsed": sum(1 for norm in norms if norm.duplicate_of is not None),
        "by_modality": counts,
        "capacities": counts["power"],
    }


def norms_to_dicts(norms: list[NormTuple]) -> list[dict]:
    return [asdict(norm) for norm in norms]
