#!/usr/bin/env python3
"""Valida rutas, nombres, `type` y la correspondencia 1:1 entre cada documento y su catálogo CTLG, sin aprobar su contenido.

Uso:
    python validate_pathmap.py --workspace <raíz> --type TRM --file business/terms/TRM-001-cliente.md
    python validate_pathmap.py --workspace <raíz> --type CTLG --file business/rules/CTLG-BR.md
    python validate_pathmap.py --workspace <raíz> --check-catalog BR     # 1:1 entre BR-*.md y CTLG-BR.md
    python validate_pathmap.py --workspace <raíz> --check-catalog TRM    # 1:1 entre TRM-*.md y CTLG-TRM.md
"""
import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
_PM = json.loads((ROOT / "assets" / "pathmap.json").read_text(encoding="utf-8"))  # fuente única: assets/pathmap.json
MAP = {k: v.rstrip("/") for k, v in _PM["document_types"].items()}
CATALOGS = {k: v["dir"].rstrip("/") for k, v in _PM["catalogs"].items()}  # id CTLG -> directorio
CATALOG_OF = {k: v["indexes"] for k, v in _PM["catalogs"].items()}  # id CTLG -> tipo indexado
LINK = re.compile(r"\]\(([^)#\s]+\.md)\)")


def _fm(text):
    m = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    return m.group(1) if m else None


def _resolve(workspace, path):
    p = pathlib.Path(path)
    return (workspace / p).resolve() if not p.is_absolute() else p.resolve()


def validate(workspace, document_type, path, override=None):
    ws = pathlib.Path(workspace).resolve()
    actual = _resolve(ws, path)
    if not actual.is_relative_to(ws):
        return False, "La ruta sale del workspace"
    if not actual.is_file():
        return False, "Archivo no existe"
    fm = _fm(actual.read_text(encoding="utf-8"))
    if fm is None:
        return False, "Falta frontmatter YAML"
    found = re.search(r"(?m)^type:\s*['\"]?([A-Za-z0-9_-]+)", fm)
    if not found or found.group(1) != document_type:
        return False, "type OKF distinto del contrato"
    ident = re.search(r"(?m)^id:\s*['\"]?([A-Za-z0-9_-]+)", fm)
    if not ident or not actual.name.startswith(ident.group(1)):
        return False, "El nombre del archivo debe comenzar con el id del frontmatter"
    if override:
        target = _resolve(ws, override)
        if target.parent != actual.parent:
            return False, "La ruta no coincide con override explícito"
        return True, "Ruta, type e id conformes (validar OKF completo por separado)"
    if document_type == "CTLG":
        cid = ident.group(1)
        if cid in CATALOGS:
            expected = (ws / CATALOGS[cid]).resolve()
        else:
            # Catálogo narrativo genérico: declara el tipo que cataloga en `indexes` y vive en su directorio.
            ix = re.search(r"(?m)^indexes:\s*['\"]?([A-Za-z0-9_-]+)", fm)
            if ix and ix.group(1) == "AREA":
                # Índice de área: cataloga todo el área de negocio y vive en la raíz de business/.
                expected = (ws / "business").resolve()
            elif not ix or ix.group(1) not in MAP:
                return False, f"Catálogo sin mapeo en pathmap.json ni campo indexes válido: {cid}"
            else:
                expected = (ws / MAP[ix.group(1)]).resolve()
    elif document_type in MAP:
        expected = (ws / MAP[document_type]).resolve()
    else:
        return False, "Tipo sin mapeo; BLOCKED"
    if actual.parent != expected:
        return False, f"Directorio incorrecto: esperado {expected}"
    return True, "Ruta, type e id conformes (validar OKF completo por separado)"


def check_catalog(workspace, indexed_type):
    """1:1: cada documento `<TIPO>-*.md` tiene exactamente una fila en `CTLG-<TIPO>.md` y cada fila apunta a un documento existente.

    `index.md` queda prohibido: el catálogo CTLG es el único índice de un tipo.
    """
    ws = pathlib.Path(workspace).resolve()
    cat_id = next((k for k, v in CATALOG_OF.items() if v == indexed_type), None)
    if cat_id is None or indexed_type not in MAP:
        return False, f"Tipo indexado sin catálogo en pathmap.json: {indexed_type}"
    d = ws / CATALOGS[cat_id]
    if (d / "index.md").exists():
        return False, f"index.md obsoleto en {d}: elimínalo; el catálogo es {cat_id}.md (STD-OKF CTLG)"
    cat = d / f"{cat_id}.md"
    if not cat.is_file():
        return False, f"Falta {cat_id}.md en {d}"
    text = cat.read_text(encoding="utf-8")
    members = {p.name for p in d.glob(f"{indexed_type}-*.md")}
    links = [pathlib.PurePosixPath(x).name for x in LINK.findall(text)]
    rows = set(links)
    problems = []
    if len(rows) != len(links):
        dup = sorted({x for x in links if links.count(x) > 1})
        problems.append("Filas duplicadas en el catálogo: " + ", ".join(dup))
    if members - rows:
        problems.append("Documentos fuera del catálogo: " + ", ".join(sorted(members - rows)))
    if rows - members:
        problems.append("Filas del catálogo sin documento: " + ", ".join(sorted(rows - members)))
    if problems:
        return False, "; ".join(problems)
    return True, f"Catálogo {cat_id} consistente 1:1 en {CATALOGS[cat_id]} ({len(members)} documentos)"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--workspace", default=".")
    p.add_argument("--type")
    p.add_argument("--file")
    p.add_argument("--override")
    p.add_argument("--check-catalog", choices=sorted(CATALOG_OF.values()))
    a = p.parse_args()
    if a.check_catalog:
        ok, msg = check_catalog(a.workspace, a.check_catalog)
        print(json.dumps({"valid": ok, "message": msg}, ensure_ascii=False))
        return 0 if ok else 1
    if not a.type or not a.file:
        p.error("--type y --file son obligatorios (o usa --check-catalog)")
    ok, msg = validate(a.workspace, a.type, a.file, a.override)
    print(json.dumps({"valid": ok, "message": msg}, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
