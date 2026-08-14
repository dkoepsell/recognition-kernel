#!/usr/bin/env python3
"""Build an FRCP corpus from an authoritative source.

The corpus that ships with this repository is an abridged demonstration
fixture. Nothing computed from it is a result about the Federal Rules. Use this
script to build a corpus you can actually report from.

The script does not scrape. It takes a local file you have obtained yourself —
the plain-text or HTML rules from uscourts.gov, or a PDF you have converted —
and segments it into the provision structure the extractors consume:

    python tools/fetch_frcp.py path/to/frcp.txt -o examples/frcp/corpus/frcp_full.json

Segmentation is by rule and subdivision heading. Check the output before using
it: a chunking error puts a provision under the wrong locator, and a
mis-assigned locator is how one norm gets counted twice.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

RULE_RE = re.compile(r"^\s*Rule\s+(\d+(?:\.\d+)?)\.\s*(.+?)\s*$", re.MULTILINE)
SUBDIVISION_RE = re.compile(r"^\s*\(([a-z])\)\s*(.*)$", re.MULTILINE)


def segment(text: str) -> list[dict]:
    provisions: list[dict] = []
    matches = list(RULE_RE.finditer(text))
    for index, match in enumerate(matches):
        number, heading = match.group(1), match.group(2)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[start:end]

        subdivisions = list(SUBDIVISION_RE.finditer(body))
        if not subdivisions:
            provisions.append(
                {
                    "id": f"frcp-{number}",
                    "locator": f"Rule {number}",
                    "heading": heading,
                    "chunk": index,
                    "text": " ".join(body.split()),
                }
            )
            continue

        for position, sub in enumerate(subdivisions):
            letter = sub.group(1)
            sub_start = sub.start()
            sub_end = (
                subdivisions[position + 1].start()
                if position + 1 < len(subdivisions)
                else len(body)
            )
            provisions.append(
                {
                    "id": f"frcp-{number}{letter}",
                    "locator": f"Rule {number}({letter})",
                    "heading": heading,
                    "chunk": index,
                    "text": " ".join(body[sub_start:sub_end].split()),
                }
            )
    return provisions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="local plain-text copy of the rules")
    parser.add_argument("-o", "--out", required=True)
    parser.add_argument("--label", default="Federal Rules of Civil Procedure")
    args = parser.parse_args()

    text = Path(args.source).read_text(encoding="utf-8", errors="replace")
    provisions = segment(text)
    if not provisions:
        raise SystemExit(
            "No rules matched. The segmenter expects headings of the form "
            "'Rule 12. Defenses and Objections'. Inspect the source and adjust "
            "RULE_RE rather than trusting an empty corpus."
        )

    payload = {
        "meta": {
            "label": args.label,
            "corpus_id": "frcp-full",
            "cell": "legal system",
            "copyright": "Work of the United States government; not subject to copyright.",
            "text_status": "verbatim",
            "source_file": str(args.source),
            "provisions_note": (
                "Segmented by tools/fetch_frcp.py. VERIFY THE SEGMENTATION before "
                "reporting anything: a mis-assigned locator is how one norm gets "
                "counted twice under two rule numbers."
            ),
        },
        "provisions": provisions,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}: {len(provisions)} provisions, "
          f"{sum(len(p['text']) for p in provisions)} characters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
