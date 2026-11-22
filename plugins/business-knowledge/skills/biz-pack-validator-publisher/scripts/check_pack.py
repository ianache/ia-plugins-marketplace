#!/usr/bin/env python3
"""Verifica la coherencia estructural de la línea base de negocio bajo <workspace>/business.

Comprueba, sin aprobar contenido: frontmatter OKF de cada documento, ruta y tipo según el pathmap, índices de
reglas (BR) y glosario (TRM), enlaces Markdown entre documentos, IDs de `related` y huecos de trazabilidad.
Con STD-OKF-001 v1.9.0-stable estos tipos están aprobados y ya no se emiten avisos `type propuesto`.
Salida: JSON. Código 1 si hay errores.
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_okf  # noqa: E402
import validate_pathmap  # noqa: E402

ID_RE = re.compile(r"^(TRM|BCP|BO|STK|BCAP|BR|IMD|BSN)-\d+")
LINK = re.compile(r"\]\(([^)#\s]+\.md)(?:#[^)]*)?\)")
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def load_meta(path):
    import yaml
    m = FRONT.match(path.read_text(encoding="utf-8"))
    try:
        return (yaml.safe_load(m.group(1)) or {}) if m else {}
    except Exception:
        return {}


def check(workspace):
    ws = pathlib.Path(workspace).resolve()
    base = ws / "business"
    errors, warnings, docs = [], [], {}
    if not base.is_dir():
        return {"errors": [f"No existe {base}"], "warnings": [], "documents": 0}
    files = sorted(base.rglob("*.md"))
    for p in files:
        rel = p.relative_to(ws).as_posix()
        meta = load_meta(p)
        t = str(meta.get("type", ""))
        for issue in validate_okf.validate(p):
            (warnings if issue.startswith("type propuesto") else errors).append(f"{rel}: {issue}")
        ok, msg = validate_pathmap.validate(ws, t, p)
        if not ok:
            errors.append(f"{rel}: {msg}")
        if meta.get("id"):
            if str(meta["id"]) in docs:
                errors.append(f"{rel}: id duplicado {meta['id']}")
            docs[str(meta["id"])] = {"path": p, "type": t, "meta": meta}
    for indexed_type in ("BR", "TRM"):
        if (ws / validate_pathmap.MAP[indexed_type]).is_dir():
            ok, msg = validate_pathmap.check_catalog(ws, indexed_type)
            if not ok:
                errors.append(f"{indexed_type}: {msg}")
    br_ids = {i for i, d in docs.items() if d["type"] == "BR"}
    for ident, d in docs.items():
        if d["type"] == "BSN":
            cited = set(re.findall(r"\bBR-\d{3,}\b", d["path"].read_text(encoding="utf-8")))
            for b in sorted(cited - br_ids):
                errors.append(f"{ident}: cita una regla inexistente en el pack: {b}")
            if not cited:
                warnings.append(f"{ident}: el escenario no cita ninguna regla BR (hueco de trazabilidad)")
    for ident, d in docs.items():
        for r in d["meta"].get("related") or []:
            if ID_RE.match(str(r)) and str(r) not in docs:
                errors.append(f"{ident}: related apunta a un ID inexistente: {r}")
        for target in LINK.findall(d["path"].read_text(encoding="utf-8")):
            if not (d["path"].parent / target).resolve().is_file():
                errors.append(f"{ident}: enlace roto: {target}")
    text = {i: d["path"].read_text(encoding="utf-8") for i, d in docs.items()}
    for ident, d in docs.items():
        mentioned = any(o != ident and (re.search(r"" + re.escape(ident) + r"", text[o])
                                        or ident in [str(x) for x in (od["meta"].get("related") or [])])
                        for o, od in docs.items())
        if d["type"] in ("BR", "BO", "BCAP") and not mentioned:
            warnings.append(f"{ident}: ningún documento lo referencia (hueco de trazabilidad)")
        if d["type"] == "IMD" and not re.search(r"TRM-\d+", text[ident]):
            warnings.append(f"{ident}: el modelo no enlaza ningún término del glosario (TRM)")
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
