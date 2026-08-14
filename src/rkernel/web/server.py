"""Stdlib HTTP server exposing the kernel over JSON, plus the static frontend.

Single-user, localhost-oriented. There is no authentication and no upload
sandboxing, so bind to a loopback address (the default) unless you have
arranged access control yourself.
"""

from __future__ import annotations

import json
import mimetypes
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from ..chain import CHAIN_LINKS, Chain
from ..kernel import Kernel, load_kernel
from ..typology import compare, generate, reference_grid

STATIC_DIR = Path(__file__).resolve().parent / "static"
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "spec" / "schema" / "chain.schema.json"
MAX_BODY_BYTES = 8 * 1024 * 1024

# Mirrors spec/schema/chain.schema.json. Kept as a fallback so the builder still
# works from an installed wheel, where spec/ is not shipped alongside the package.
LINK_STATUSES = ["internal", "external", "absent"]
CONFIDENCES = ["high", "medium", "low"]
SYSTEM_KINDS = [
    "reference_ontology",
    "classification",
    "certification_scheme",
    "legal_order",
    "other",
]
LINK_FIELDS = ["status", "filler", "evidence", "confidence", "note", "specification"]


def _plain(obj: Any) -> Any:
    """Make kernel dataclasses JSON-serialisable."""
    if is_dataclass(obj) and not isinstance(obj, type):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_plain(v) for v in obj]
    return obj


def _kernel_summary(kernel: Kernel) -> dict[str, Any]:
    """The taxonomy the frontend needs to lay out the grid."""
    return {
        "kernel_version": kernel.kernel_version,
        "source": getattr(kernel, "source", None),
        "gating_rule": _plain(getattr(kernel, "gating_rule", None)),
        "strata": _plain(kernel.strata),
        "loci": _plain(kernel.loci),
        "primitives": _plain(kernel.primitives),
        "named_types": _plain(getattr(kernel, "named_types", [])),
    }


def _schema_info() -> dict[str, Any]:
    """Enums the builder's form needs, read from the schema when it is present."""
    info = {
        "chain_links": list(CHAIN_LINKS),
        "link_statuses": LINK_STATUSES,
        "system_kinds": SYSTEM_KINDS,
        "confidences": CONFIDENCES,
        "link_fields": LINK_FIELDS,
        "source": "builtin",
    }
    try:
        defs = json.loads(SCHEMA_PATH.read_text(encoding="utf-8")).get("$defs", {})
    except (OSError, ValueError):
        return info
    link_props = defs.get("link", {}).get("properties", {})
    if status := link_props.get("status", {}).get("enum"):
        info["link_statuses"] = status
    if conf := link_props.get("confidence", {}).get("enum"):
        info["confidences"] = conf
    if kinds := defs.get("systemKind", {}).get("enum"):
        info["system_kinds"] = kinds
    if link_props:
        info["link_fields"] = list(link_props)
    info["source"] = str(SCHEMA_PATH)
    return info


def _build_chain_doc(spec: dict[str, Any]) -> dict[str, Any]:
    """Assemble a schema-shaped chain document from the builder form's input.

    Every one of the seven links is required by the schema, so a link the caller
    omitted is written out as `absent` rather than left off. Blank optional
    fields are dropped so the exported document stays clean.
    """
    statuses = set(LINK_STATUSES)
    raw_links = spec.get("links") or {}
    if not isinstance(raw_links, dict):
        raise ValueError("'links' must be an object")

    links: dict[str, Any] = {}
    for name in CHAIN_LINKS:
        entry = raw_links.get(name) or {}
        if not isinstance(entry, dict):
            raise ValueError(f"link '{name}' must be an object")
        status = entry.get("status") or "absent"
        if status not in statuses:
            raise ValueError(
                f"link '{name}' has status '{status}'; expected one of {sorted(statuses)}"
            )
        link: dict[str, Any] = {"status": status}
        for field in ("filler", "evidence", "note", "confidence", "specification"):
            value = entry.get(field)
            if isinstance(value, str):
                value = value.strip()
            if value:
                link[field] = value
        links[name] = link

    system: dict[str, Any] = {"label": (spec.get("label") or "untitled system").strip()}
    for field in ("corpus", "version", "jurisdiction", "license", "notes"):
        value = spec.get(field)
        if isinstance(value, str) and value.strip():
            system[field] = value.strip()
    declared = spec.get("declared_kind")
    if declared:
        if declared not in SYSTEM_KINDS:
            raise ValueError(f"declared_kind '{declared}' is not a recognised system kind")
        system["declared_kind"] = declared

    doc: dict[str, Any] = {
        "chain_id": (spec.get("chain_id") or "draft").strip() or "draft",
        "system": system,
        "links": links,
    }
    if spec.get("committed_before_detection") is not None:
        doc["committed_before_detection"] = bool(spec["committed_before_detection"])
    for field in ("assigned_by", "assigned_on"):
        value = spec.get(field)
        if isinstance(value, str) and value.strip():
            doc[field] = value.strip()
    return doc


def _validate_doc(doc: dict[str, Any]) -> dict[str, Any]:
    """Best-effort schema check. jsonschema is an optional extra, so absence is
    reported as 'skipped' rather than treated as a pass."""
    try:
        import jsonschema  # noqa: PLC0415
    except ImportError:
        return {
            "status": "skipped",
            "detail": "jsonschema is not installed (pip install 'recognition-kernel[validate]')",
        }
    try:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"status": "skipped", "detail": f"schema unavailable: {exc}"}
    validator = jsonschema.Draft202012Validator(schema)
    errors = [
        {"path": "/".join(str(p) for p in e.path) or "(root)", "message": e.message}
        for e in sorted(validator.iter_errors(doc), key=lambda e: list(e.path))
    ]
    return {"status": "ok" if not errors else "invalid", "errors": errors}


def _discover_examples(root: Path) -> list[dict[str, str]]:
    """Chain files shipped with the repo, offered as one-click loads."""
    examples_dir = root / "examples"
    if not examples_dir.is_dir():
        return []
    found = []
    for path in sorted(examples_dir.rglob("*.chain.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        rel = path.relative_to(root).as_posix()
        found.append(
            {
                "path": rel,
                "chain_id": raw.get("chain_id", path.stem),
                "label": raw.get("system_label") or raw.get("label") or path.stem,
            }
        )
    return found


class _Handler(BaseHTTPRequestHandler):
    server_version = "rkernel-web"

    # Injected by serve().
    kernel: Kernel
    root: Path

    def log_message(self, fmt: str, *args: Any) -> None:  # quieter console
        pass

    # -- plumbing ---------------------------------------------------------

    def _send_json(self, payload: Any, status: int = 200) -> None:
        body = json.dumps(payload, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _error(self, message: str, status: int = 400) -> None:
        self._send_json({"error": message}, status)

    def _read_json(self) -> Any:
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            raise ValueError("empty request body")
        if length > MAX_BODY_BYTES:
            raise ValueError("request body too large")
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def _resolve_example(self, rel: str) -> Path:
        """Confine example loads to the repo's examples/ directory."""
        candidate = (self.root / rel).resolve()
        base = (self.root / "examples").resolve()
        if not candidate.is_file() or base not in candidate.parents:
            raise ValueError(f"not an example chain: {rel}")
        return candidate

    # -- routes -----------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        if path == "/api/kernel":
            self._send_json(_kernel_summary(self.kernel))
        elif path == "/api/examples":
            self._send_json(_discover_examples(self.root))
        elif path == "/api/grid":
            self._send_json(_plain(reference_grid(self.kernel)))
        elif path == "/api/schema":
            self._send_json(_schema_info())
        else:
            self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = self.path.split("?", 1)[0]
        try:
            if path == "/api/typology":
                self._send_json(self._typology(self._read_json()))
            elif path == "/api/compare":
                self._send_json(self._compare(self._read_json()))
            elif path == "/api/build":
                self._send_json(self._build(self._read_json()))
            else:
                self._error("no such endpoint", 404)
        except ValueError as exc:
            self._error(str(exc), 400)
        except Exception as exc:  # surface kernel errors to the UI
            self._error(f"{type(exc).__name__}: {exc}", 500)

    def _chain_from_request(self, req: dict[str, Any]) -> Chain:
        if "example" in req:
            return Chain.load(self._resolve_example(req["example"]))
        if "chain" in req:
            try:
                return Chain.from_dict(req["chain"])
            except KeyError as exc:
                raise ValueError(f"chain document is missing key {exc}") from exc
            except (TypeError, AttributeError) as exc:
                raise ValueError(f"malformed chain document: {exc}") from exc
        raise ValueError("request needs either 'example' or 'chain'")

    def _typology(self, req: dict[str, Any]) -> dict[str, Any]:
        chain = self._chain_from_request(req)
        return _plain(generate(chain, self.kernel))

    def _compare(self, req: dict[str, Any]) -> Any:
        entries = req.get("chains")
        if not isinstance(entries, list) or len(entries) < 2:
            raise ValueError("'chains' must be a list of at least two chains")
        typologies = [
            generate(self._chain_from_request(e), self.kernel) for e in entries
        ]
        return _plain(compare(typologies))

    def _build(self, req: dict[str, Any]) -> dict[str, Any]:
        """The typology builder: form input in, chain + typology + validation out."""
        doc = _build_chain_doc(req)
        validation = _validate_doc(doc)
        payload: dict[str, Any] = {"chain": doc, "validation": validation}
        try:
            payload["typology"] = _plain(generate(Chain.from_dict(doc), self.kernel))
        except Exception as exc:
            payload["typology"] = None
            payload["error"] = f"{type(exc).__name__}: {exc}"
        return payload

    # -- static -----------------------------------------------------------

    def _serve_static(self, path: str) -> None:
        rel = "index.html" if path in ("/", "") else path.lstrip("/")
        target = (STATIC_DIR / rel).resolve()
        if not target.is_file() or STATIC_DIR.resolve() not in target.parents:
            self._error("not found", 404)
            return
        body = target.read_bytes()
        ctype = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(
    host: str = "127.0.0.1",
    port: int = 8080,
    kernel_path: str | Path | None = None,
    root: str | Path | None = None,
) -> None:
    """Run the local UI until interrupted."""
    handler = type(
        "BoundHandler",
        (_Handler,),
        {
            "kernel": load_kernel(kernel_path),
            "root": Path(root or Path.cwd()).resolve(),
        },
    )
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"recognition kernel UI → http://{host}:{port}  (ctrl-c to stop)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
    finally:
        httpd.server_close()
