"""Command-line interface.

    rkernel grid                      the kernel's own well-formedness grid
    rkernel typology CHAIN.json       generate a typology from a chain
    rkernel profile CHAIN.json        the gated profile only
    rkernel compare A.json B.json     profiles side by side
    rkernel extract CORPUS.json       norm tuples plus the ontological control
    rkernel detect CORPUS.json        run the K-D3 detector
    rkernel draft-chain CORPUS.json   propose a chain from a corpus (draft)
    rkernel validate                  check kernel, schemas, and OWL agree
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import load_corpus
from .chain import Chain
from .kernel import load_kernel
from .render import (
    comparison_markdown,
    crossings_csv,
    grid_markdown,
    predicted_markdown,
    profile_markdown,
    report_markdown,
    status_row,
)
from .typology import compare, generate, reference_grid


def _emit(payload, args, markdown: str | None = None) -> None:
    if args.format == "json":
        text = json.dumps(payload, indent=2, ensure_ascii=False)
    elif args.format == "csv":
        text = crossings_csv(payload)
    else:
        text = markdown if markdown is not None else json.dumps(payload, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        print(text)


def cmd_grid(args) -> int:
    kernel = load_kernel(args.kernel)
    grid = reference_grid(kernel)
    lines = ["| | " + " | ".join(grid["loci"]) + " |", "| --- " * (len(grid["loci"]) + 1) + "|"]
    for primitive_id in grid["primitives"]:
        row = grid["rows"][primitive_id]
        lines.append(
            f"| {primitive_id} | "
            + " | ".join("\u2713" if row[locus] else "\u00b7" for locus in grid["loci"])
            + " |"
        )
    lines.append(
        f"\n*{grid['well_formed']} of {grid['cells_total']} crossings well-formed "
        f"over the seven chain loci.*"
    )
    _emit(grid, args, "\n".join(lines))
    return 0


def cmd_typology(args) -> int:
    kernel = load_kernel(args.kernel)
    chain = Chain.load(args.chain)
    typology = generate(chain, kernel)
    _emit(typology, args, report_markdown(typology, kernel))
    return 0


def cmd_profile(args) -> int:
    kernel = load_kernel(args.kernel)
    chain = Chain.load(args.chain)
    typology = generate(chain, kernel)
    markdown = "\n\n".join(
        [
            f"### {typology['system_label']}",
            status_row(typology, kernel),
            f"Computed kind: **{typology['computed_kind'].replace('_', ' ')}** "
            f"({typology['chain_thickness']['summary']})",
            profile_markdown(typology, kernel),
        ]
    )
    payload = {
        "chain_id": typology["chain_id"],
        "computed_kind": typology["computed_kind"],
        "declared_kind": typology["declared_kind"],
        "kind_mismatch": typology["kind_mismatch"],
        "chain_thickness": typology["chain_thickness"],
        "profile": typology["profile"],
        "counts": typology["counts"],
    }
    _emit(payload, args, markdown)
    return 0


def cmd_compare(args) -> int:
    kernel = load_kernel(args.kernel)
    typologies = [generate(Chain.load(path), kernel) for path in args.chains]
    comparison = compare(typologies)
    _emit(comparison, args, comparison_markdown(comparison, kernel))
    return 0


def cmd_extract(args) -> int:
    from .extract.norms import extract_norms, norms_to_dicts, summarize
    from .extract.ontological import claims_to_dicts, control_report, extract_claims

    provisions, meta = load_corpus(args.corpus)
    norms = extract_norms(provisions, use_spacy=args.spacy)
    claims = extract_claims(provisions)
    summary = summarize(norms)
    payload = {
        "corpus": meta,
        "summary": summary,
        "control": control_report(provisions, summary, claims),
        "norms": norms_to_dicts(norms),
        "ontological_claims": claims_to_dicts(claims),
    }
    control = payload["control"]
    markdown = "\n".join(
        [
            f"### {meta.get('label', args.corpus)}",
            "",
            "| Extractor | Target schema | Yield | Errors |",
            "| --- | --- | --- | --- |",
            f"| Entity-relation | ontological claims | "
            f"{control['entity_relation_extractor']['yield']} | 0 |",
            f"| Norm tuple | deontic norms | {control['norm_tuple_extractor']['yield']} | 0 |",
            "",
            f"By modality: {summary['by_modality']}. "
            f"Capacities: {summary['capacities']}. "
            f"Duplicates collapsed: {summary['duplicates_collapsed']}.",
            "",
            control["reading"],
        ]
    )
    _emit(payload, args, markdown)
    return 0


def cmd_detect(args) -> int:
    from .extract.kd3 import MatcherConfig, detect
    from .extract.norms import extract_norms

    provisions, meta = load_corpus(args.corpus)
    norms = extract_norms(provisions)
    config = MatcherConfig(
        min_shared_content_terms=args.min_shared,
        max_document_frequency=args.max_df,
    )
    result = detect(norms, provisions, config)
    result["corpus"] = meta
    fan = result["fan_out"]
    markdown = "\n".join(
        [
            f"### K-D3 over {meta.get('label', args.corpus)}",
            "",
            f"Capacities examined: {result['capacities_examined']}. "
            f"Set aside as external: {result['set_aside_external']}. "
            f"Scored: {result['scored']}. Candidates: {result['candidates']}.",
            "",
            "| Fan-out | n | min | median | mean | p90 | max |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            f"| pathway matches per capacity | {fan['n']} | {fan['min']} | {fan['median']} | "
            f"{fan['mean']} | {fan['p90']} | {fan['max']} |",
            "",
            fan["interpretation"],
            "",
            "| Candidate | Locator | Bearer | Action |",
            "| --- | --- | --- | --- |",
        ]
        + [
            f"| {finding['finding_id']} | {finding['capacity']['locator']} | "
            f"{finding['capacity']['bearer'] or '\u2014'} | "
            f"{finding['capacity']['action'][:80]} |"
            for finding in result["findings"]
            if finding["status"] == "candidate"
        ]
        + ["", "Every row above is a candidate, not a finding. Provenance is undetermined."]
    )
    _emit(result, args, markdown)
    return 0


def cmd_draft_chain(args) -> int:
    from .extract.chain_extract import draft_chain

    provisions, meta = load_corpus(args.corpus)
    chain = draft_chain(
        provisions,
        chain_id=args.chain_id or Path(args.corpus).stem,
        label=meta.get("label", args.corpus),
        corpus=str(args.corpus),
    )
    payload = chain.to_dict()
    markdown = json.dumps(payload, indent=2, ensure_ascii=False)
    _emit(payload, args, markdown)
    return 0


def cmd_validate(args) -> int:
    from .validate import run_all

    report = run_all(kernel_path=args.kernel)
    _emit(report, args, report["markdown"])
    return 0 if report["ok"] else 1


def cmd_serve(args: argparse.Namespace) -> int:
    from .web import serve

    serve(host=args.host, port=args.port, kernel_path=args.kernel, root=args.root)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rkernel",
        description="Contradiction kernel: specification, extractor, and typology generator.",
    )
    parser.add_argument("--kernel", default=None, help="path to a kernel.json (default: bundled)")
    parser.add_argument("--format", choices=["md", "json", "csv"], default="md")
    parser.add_argument("--out", default=None, help="write to this path instead of stdout")

    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("grid", help="the kernel's own well-formedness grid").set_defaults(func=cmd_grid)

    typology = sub.add_parser("typology", help="generate a typology from a chain")
    typology.add_argument("chain")
    typology.set_defaults(func=cmd_typology)

    profile = sub.add_parser("profile", help="the gated profile only")
    profile.add_argument("chain")
    profile.set_defaults(func=cmd_profile)

    comparison = sub.add_parser("compare", help="profiles side by side")
    comparison.add_argument("chains", nargs="+")
    comparison.set_defaults(func=cmd_compare)

    extract = sub.add_parser("extract", help="norm tuples plus the ontological control")
    extract.add_argument("corpus")
    extract.add_argument("--spacy", action="store_true", help="use spaCy noun chunks for bearers")
    extract.set_defaults(func=cmd_extract)

    detect = sub.add_parser("detect", help="run the K-D3 detector")
    detect.add_argument("corpus")
    detect.add_argument("--min-shared", type=int, default=2)
    detect.add_argument("--max-df", type=float, default=0.25)
    detect.set_defaults(func=cmd_detect)

    draft = sub.add_parser("draft-chain", help="propose a chain from a corpus (draft)")
    draft.add_argument("corpus")
    draft.add_argument("--chain-id", default=None)
    draft.set_defaults(func=cmd_draft_chain)

    sub.add_parser("validate", help="check kernel, schemas, and OWL agree").set_defaults(
        func=cmd_validate
    )

    web = sub.add_parser("serve", help="local web UI for typologies and profiles")
    web.add_argument("--host", default="127.0.0.1")
    web.add_argument("--port", type=int, default=8080)
    web.add_argument("--root", default=None, help="directory searched for example chains")
    web.set_defaults(func=cmd_serve)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
