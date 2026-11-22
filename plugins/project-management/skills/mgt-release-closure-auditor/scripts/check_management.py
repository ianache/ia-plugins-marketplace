#!/usr/bin/env python3
"""Verifica la coherencia estructural de la gestión de entrega bajo <workspace>/management.

Comprueba, sin aprobar contenido: frontmatter OKF de cada documento, ruta y tipo según el pathmap, enlaces
Markdown entre documentos, IDs de `related` del pack, solicitudes de cambio sin decisión humana y registros de
riesgo sin dueño. Con STD-OKF-001 v1.9.0-stable estos tipos están aprobados y ya no se emiten avisos `type propuesto`.
Salida: JSON. Código 1 si hay errores.
"""
import argparse
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_okf  # noqa: E402
import validate_pathmap  # noqa: E402

ID_RE = re.compile(r"^(PCH|RMP|SSP|STR|RSK|CHG|CLS)-\d+")
LINK = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
PLACEHOLDER = re.compile(r"<[^>\n]+>")
DECIDED = re.compile(r"-\s*\*\*Estado:\*\*\s*(\w+)")
DECIDER = re.compile(r"-\s*\*\*Decidido por:\*\*\s*(.+)")


def meta_of(text):
    m = FRONT.match(text)
    try:
        return (yaml.safe_load(m.group(1)) or {}) if m else {}
    except yaml.YAMLError:
        return {}


def check(workspace):
    ws = pathlib.Path(workspace).resolve()
    base = ws / "management"
    errors, warnings, docs = [], [], {}
    if not base.is_dir():
        return {"errors": [f"No existe {base}"], "warnings": [], "documents": 0}
    for p in sorted(base.rglob("*.md")):
        rel = p.relative_to(ws).as_posix()
        text = p.read_text(encoding="utf-8")
        meta = meta_of(text)
        t = str(meta.get("type", ""))
        for issue in validate_okf.validate(p):
            (warnings if issue.startswith("type propuesto") else errors).append(f"{rel}: {issue}")
        ok, msg = validate_pathmap.validate(ws, t, p)
        if not ok:
            errors.append(f"{rel}: {msg}")
        if meta.get("id"):
            if str(meta["id"]) in docs:
                errors.append(f"{rel}: id duplicado {meta['id']}")
            docs[str(meta["id"])] = {"path": p, "type": t, "meta": meta, "text": text, "rel": rel}
    for ident, d in docs.items():
        for r in d["meta"].get("related") or []:
            if ID_RE.match(str(r)) and str(r) not in docs:
                errors.append(f"{ident}: related apunta a un ID inexistente: {r}")
        for target in LINK.findall(d["text"]):
            if not (d["path"].parent / target).resolve().is_file():
                errors.append(f"{ident}: enlace roto: {target}")
        if d["type"] == "CHG":
            state = DECIDED.search(d["text"])
            decider = DECIDER.search(d["text"])
            st = state.group(1) if state else ""
            if st in ("approved", "rejected", "deferred") and (not decider or PLACEHOLDER.search(decider.group(1)) or not decider.group(1).strip().startswith("human:")):
                errors.append(f"{ident}: decisión '{st}' sin 'Decidido por: human:<nombre>'")
            if st == "proposed":
                warnings.append(f"{ident}: solicitud de cambio pendiente de decisión")
        if d["type"] == "RSK":
            rows = [l for l in d["text"].splitlines() if re.match(r"\|\s*R-\d+\s*\|", l)]
            for row in rows:
                cells = [c.strip() for c in row.strip("|").split("|")]
                if len(cells) > 4 and (not cells[4] or PLACEHOLDER.search(cells[4])):
                    errors.append(f"{ident}: riesgo {cells[0]} sin dueño")
                if len(cells) > 7 and cells[7] == "open":
                    warnings.append(f"{ident}: riesgo {cells[0]} abierto")
        if d["type"] in ("SSP", "STR", "RMP") and not d["meta"].get("related"):
            warnings.append(f"{ident}: sin `related` hacia el acta, plan o riesgos (hueco de trazabilidad)")
    return {"errors": errors, "warnings": warnings, "documents": len(docs)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workspace", default=".")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    res = check(a.workspace)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 1 if res["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
