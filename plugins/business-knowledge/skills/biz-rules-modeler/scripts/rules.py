#!/usr/bin/env python3
"""Mantiene las reglas de negocio: un documento OKF `type: BR` por regla (BR-NNN.md) en business/rules/ y su catálogo `type: CTLG` (CTLG-BR.md).

Uso (<dir> es la carpeta de reglas, normalmente <workspace>/business/rules):
    python rules.py new <dir> "<Título>" --product <PRODUCTO>      # crea BR-NNN.md vacío desde la plantilla
    python rules.py from-json <dir> <reglas.json> --product <P>    # un BR-NNN.md por regla del lote; todo o nada
    python rules.py build <dir>    # regenera CTLG-BR.md desde el frontmatter de los BR; elimina index.md obsoleto
    python rules.py check <dir>    # valida cada regla y la correspondencia 1:1 con el catálogo; código 1 si hay errores

Formato de <reglas.json>: lista de objetos con: title, description, statement, owner (obligatorios);
opcionales: id (BR-NNN; si se omite se asigna el siguiente), conditions, states, terms (TRM-NNN[]), capabilities (BCAP-NNN[]),
objectives (BO-NNN[]), sources ([{id, resource, title}]), open_questions (str[]).
Una regla sin sources exige al menos una pregunta abierta. Requiere PyYAML. No aprueba reglas: solo comprueba estructura.
"""
import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

import yaml

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "deliverable.md")
CATALOG_ID = "CTLG-BR"
CATALOG_FILE = CATALOG_ID + ".md"
BY = "biz-rules-modeler/2.0.0"
FILE_RE = re.compile(r"^BR-(\d{3,})\.md$")
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
LINK = re.compile(r"\]\(([^)#]+\.md)(?:#[^)]*)?\)")
PLACEHOLDER = re.compile(r"<[A-Za-zÁÉÍÓÚÑáéíóúñ][^<>\n]*>")
ID_TRM = re.compile(r"^TRM-\d{3,}$")
ID_BCAP = re.compile(r"^BCAP-\d{3,}$")
ID_BO = re.compile(r"^BO-\d{3,}$")
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?$")
STATUS = {"draft", "stable", "deprecated"}
CLASSIFICATIONS = ["public", "internal", "confidential", "restricted"]


def sort_key(text):
    text = text.lower().replace("ñ", "n\x7f")
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^0-9a-z\x7f ]", "", text).strip()


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


def _split(text):
    m = FRONT.match(text)
    if not m:
        return None, text
    return (yaml.safe_load(m.group(1)) or {}), text[m.end():]


def rule_files(folder):
    return sorted(p for p in glob.glob(os.path.join(folder, "BR-*.md")) if FILE_RE.match(os.path.basename(p)))


def next_id(folder):
    used = [int(FILE_RE.match(os.path.basename(p)).group(1)) for p in rule_files(folder)]
    return f"BR-{(max(used) if used else 0) + 1:03d}"


def term_file(folder, term_id):
    """Archivo del TRM en ../terms (el glosario es dueño de los términos)."""
    hits = glob.glob(os.path.join(folder, "..", "terms", f"{term_id}-*.md"))
    return os.path.basename(hits[0]) if len(hits) == 1 else None


def _bullets(items):
    return "\n".join(f"- {x}" for x in items) if items else "- Ninguna."


def _evidence_line(src):
    return f"{src['id']} {src.get('title', '')} ({src['resource']})".replace("  ", " ").strip()


def render_rule(item, rid, folder, now):
    """Texto de un BR-NNN.md a partir de un objeto del lote. Lanza ValueError si el objeto no es válido."""
    for key in ("title", "description", "statement", "owner"):
        if not str(item.get(key, "")).strip():
            raise ValueError(f"{rid}: falta '{key}'")
    sources = item.get("sources") or []
    questions = item.get("open_questions") or []
    if not sources and not questions:
        raise ValueError(f"{rid}: sin fuentes; registra al menos una pregunta abierta (open_questions)")
    terms = item.get("terms") or []
    links = []
    for t in terms:
        if not ID_TRM.match(t):
            raise ValueError(f"{rid}: término con formato inválido: {t}")
        f = term_file(folder, t)
        if f is None:
            raise ValueError(f"{rid}: el término {t} no existe en business/terms")
        links.append(f"[{t}](../terms/{f})")
    for cap in item.get("capabilities") or []:
        if not ID_BCAP.match(cap):
            raise ValueError(f"{rid}: capacidad con formato inválido: {cap}")
    for obj in item.get("objectives") or []:
        if not ID_BO.match(obj):
            raise ValueError(f"{rid}: objetivo con formato inválido: {obj}")
    related = list(terms) + list(item.get("capabilities") or []) + list(item.get("objectives") or [])
    meta = {
        "type": "BR",
        "id": rid,
        "title": item["title"].strip(),
        "description": " ".join(str(item["description"]).split()),
        "version": "0.1.0",
        "status": "draft",
        "owner": item["owner"].strip(),
        "classification": "internal",
        "tags": ["business", "br"],
        "product": item["product"],
        "pack": "business-knowledge",
        "skill": "biz-rules-modeler",
        "generated": {"by": BY, "at": now.isoformat(timespec="seconds")},
        "sources": [
            {"id": s.get("id", f"src-{i + 1}"), "resource": s["resource"], "title": s.get("title", "")}
            for i, s in enumerate(sources)
        ],
        "related": related,
    }
    head = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=10 ** 6).rstrip()
    evidence = [_evidence_line(s) for s in meta["sources"]]
    trace = [
        f"- **Términos:** {', '.join(links) if links else '—'}",
        f"- **Capacidades:** {', '.join(item.get('capabilities') or []) or '—'}",
        f"- **Objetivos:** {', '.join(item.get('objectives') or []) or '—'}",
        f"- **Evidencia:** {'; '.join(evidence) or '—'}",
    ]
    body = "\n".join([
        f"# {meta['title']}", "",
        "## Definición de regla", str(item["statement"]).strip(), "",
        "## Condiciones y excepciones", str(item.get("conditions") or "No registradas en las fuentes.").strip(), "",
        "## Estados, permisos e invariantes", str(item.get("states") or "No registrados en las fuentes.").strip(), "",
        "## Trazabilidad", *trace, "",
        "## Preguntas abiertas", _bullets(questions), "",
    ])
    return f"---\n{head}\n---\n\n{body}"


def cmd_new(folder, title, product):
    rid = next_id(folder)
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, f"{rid}.md")
    text = read(TEMPLATE).replace("BR-NNN", rid).replace("<PRODUCTO>", product).replace("Regla de negocio — <alcance>", title)
    write(path, text)
    print(path)


def cmd_from_json(folder, json_path, product, update=False):
    with open(json_path, encoding="utf-8") as fh:
        items = json.load(fh)
    if not isinstance(items, list):
        raise SystemExit("El JSON debe ser una lista de reglas")
    now = datetime.now(timezone.utc).astimezone()
    planned, taken = [], {os.path.basename(p) for p in rule_files(folder)}
    counter = int(next_id(folder)[3:]) - 1
    seen = set()
    for item in items:
        if not isinstance(item, dict):
            raise SystemExit("Cada regla debe ser un objeto")
        item = dict(item, product=product)
        if item.get("id"):
            if not re.match(r"^BR-\d{3,}$", item["id"]):
                raise SystemExit(f"id inválido: {item['id']}")
            rid = item["id"]
        else:
            counter += 1
            rid = f"BR-{counter:03d}"
        if rid in seen:
            raise SystemExit(f"{rid}: id repetido en el lote")
        seen.add(rid)
        if f"{rid}.md" in taken and not update:
            raise SystemExit(f"{rid}.md ya existe; usa --update para reemplazarlo")
        try:
            planned.append((rid, render_rule(item, rid, folder, now)))
        except ValueError as ex:
            raise SystemExit(f"ERROR {ex}") from None
    os.makedirs(folder, exist_ok=True)
    for rid, text in planned:
        write(os.path.join(folder, f"{rid}.md"), text)
        print(os.path.join(folder, f"{rid}.md"))
    print(f"{len(planned)} reglas escritas; ejecuta 'build' para regenerar {CATALOG_FILE}.")


def render_catalog_body(rules):
    out = ["# Catálogo de reglas de negocio", "",
           "> **Definición:** índice de las reglas de negocio (BR) del producto, ordenado por ID. Una regla se define únicamente en su documento `BR-NNN`.",
           "> **Regla:** este documento no repite el enunciado de ninguna regla. Generado con `rules.py build`; no editar a mano.", "",
           "| ID | Regla | Estado | Versión |", "|---|---|---|---|"]
    for m, _ in sorted(rules, key=lambda r: r[0].get("id", "")):
        title = str(m.get("title", "")).replace("|", "/")
        out.append(f"| {m.get('id')} | [{title}]({os.path.basename(m['_file'])}) | {m.get('status', '')} | {m.get('version', '')} |")
    return "\n".join(out).strip() + "\n"


def load_rules(folder):
    rules = []
    for p in rule_files(folder):
        meta, body = _split(read(p))
        meta = dict(meta or {}, _file=p)
        rules.append((meta, body))
    return rules


def render_catalog(folder, rules, now=None):
    path = os.path.join(folder, CATALOG_FILE)
    old_meta, old_body = {}, None
    if os.path.exists(path):
        old_meta, old_body = _split(read(path))
        old_meta = old_meta or {}
    body = render_catalog_body(rules)
    products = sorted({str(m.get("product")) for m, _ in rules if m.get("product")})
    owners = sorted({str(m.get("owner")) for m, _ in rules if m.get("owner")})
    meta = {
        "type": "CTLG",
        "id": CATALOG_ID,
        "title": f"Catálogo de reglas de negocio — {', '.join(products) if products else 'sin producto'}",
        "description": f"Índice ordenado de las {len(rules)} reglas de negocio del producto; cada regla se define en su propio documento BR.",
        "version": old_meta.get("version", "1.0.0"),
        "status": old_meta.get("status", "draft"),
        "owner": ", ".join(owners) if owners else "Por definir",
        "classification": "internal",
        "tags": ["business", "br", "catalogo"],
        "product": ", ".join(products) if products else "Por definir",
        "pack": "business-knowledge",
        "skill": "biz-rules-modeler",
        "generated": {"by": BY, "at": old_meta.get("generated", {}).get("at", "")},
        "sources": [{"id": f"src-{i + 1}", "resource": os.path.basename(m["_file"]), "title": str(m.get("title", ""))}
                    for i, (m, _) in enumerate(rules)],
        "related": [m.get("id") for m, _ in rules],
    }
    comparable = {k: v for k, v in meta.items() if k != "generated"}
    old_comparable = {k: v for k, v in old_meta.items() if k != "generated"}
    if old_body is not None and old_body == body and old_comparable == comparable:
        return read(path)
    meta["generated"]["at"] = (now or datetime.now(timezone.utc).astimezone()).isoformat(timespec="seconds")
    head = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=10 ** 6).rstrip()
    return f"---\n{head}\n---\n\n{body}"


def check_rule(path, meta, body):
    errors = []
    name = os.path.basename(path)
    if not FILE_RE.match(name):
        errors.append("el nombre debe ser BR-NNN.md")
    if meta is None:
        return ["frontmatter no encontrado"]
    if meta.get("type") != "BR":
        errors.append("el frontmatter debe tener type: BR")
    if meta.get("id") != name[:-3]:
        errors.append(f"el id '{meta.get('id')}' no coincide con el archivo")
    for key in ("title", "description", "owner", "product", "pack", "skill", "version", "status"):
        v = meta.get(key)
        if not v or str(v).startswith("<"):
            errors.append(f"frontmatter sin '{key}'")
    if meta.get("status") not in STATUS:
        errors.append(f"status '{meta.get('status')}' no válido")
    if not SEMVER.match(str(meta.get("version", ""))):
        errors.append("version debe ser SemVer")
    if meta.get("title") and not re.search(r"^# " + re.escape(str(meta["title"])) + r"\s*$", body, flags=re.M):
        errors.append(f"falta el encabezado '# {meta['title']}' igual al title")
    found = PLACEHOLDER.search(body)
    if found:
        errors.append(f"texto de plantilla sin completar: {found.group(0)}")
    sources = meta.get("sources") or []
    open_q = re.search(r"## Preguntas abiertas\n(.*?)(?=\n## |\Z)", body, re.S)
    has_questions = bool(open_q and re.search(r"^- (?!Ninguna\.)\S", open_q.group(1), re.M))
    if not sources and not has_questions:
        errors.append("sin fuentes: registra la afirmación como pregunta abierta con responsable")
    for r in meta.get("related") or []:
        if not re.match(r"^[A-Z][A-Z0-9]*-\d{3,}$", str(r)):
            errors.append(f"related con ID no reconocido: {r}")
    return errors


def cmd_check(folder):
    rules = load_rules(folder)
    errors, ids = [], {}
    for meta, body in rules:
        path = meta["_file"]
        name = os.path.basename(path)
        clean = {k: v for k, v in meta.items() if k != "_file"}
        errors += [f"{name}: {e}" for e in check_rule(path, clean, body)]
        rid = clean.get("id")
        if rid in ids:
            errors.append(f"{name}: ID duplicado (también en {ids[rid]})")
        ids[rid] = name
    files = {os.path.basename(m["_file"]) for m, _ in rules}
    cat = os.path.join(folder, CATALOG_FILE)
    if os.path.exists(os.path.join(folder, "index.md")):
        errors.append("index.md obsoleto: ejecuta 'build' para eliminarlo (el índice es CTLG-BR.md)")
    if not os.path.exists(cat):
        errors.append(f"No existe {CATALOG_FILE}: ejecuta 'build'")
    else:
        text = read(cat)
        links = [os.path.basename(x) for x in LINK.findall(text)]
        linked = set(links)
        if len(linked) != len(links):
            errors.append(f"{CATALOG_FILE}: filas duplicadas")
        if linked - files:
            errors.append(f"{CATALOG_FILE}: filas sin regla: {', '.join(sorted(linked - files))}")
        if files - linked:
            errors.append(f"{CATALOG_FILE}: reglas fuera del catálogo: {', '.join(sorted(files - linked))}")
        meta, _ = _split(text)
        if not meta or meta.get("type") != "CTLG" or meta.get("id") != CATALOG_ID:
            errors.append(f"{CATALOG_FILE}: el frontmatter debe tener type: CTLG e id: {CATALOG_ID}")
        if render_catalog(folder, rules) != text:
            errors.append(f"{CATALOG_FILE}: el catálogo no coincide con las reglas: ejecuta 'build'")
    for err in errors:
        print("ERROR", err)
    print(f"{len(rules)} reglas revisadas, {len(errors)} errores.")
    return 1 if errors else 0


def cmd_build(folder):
    rules = load_rules(folder)
    write(os.path.join(folder, CATALOG_FILE), render_catalog(folder, rules))
    legacy = os.path.join(folder, "index.md")
    if os.path.exists(legacy):
        os.remove(legacy)
        print("index.md obsoleto eliminado (sustituido por CTLG-BR.md).")
    print(f"{len(rules)} reglas indexadas en {CATALOG_FILE}.")


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("dir")
    n.add_argument("title")
    n.add_argument("--product", required=True)
    j = sub.add_parser("from-json")
    j.add_argument("dir")
    j.add_argument("json")
    j.add_argument("--product", required=True)
    j.add_argument("--update", action="store_true")
    sub.add_parser("build").add_argument("dir")  # elimina index.md obsoleto y regenera CTLG-BR.md
    sub.add_parser("check").add_argument("dir")
    a = ap.parse_args(argv)
    if a.cmd == "new":
        cmd_new(a.dir, a.title, a.product)
    elif a.cmd == "from-json":
        cmd_from_json(a.dir, a.json, a.product, a.update)
    elif a.cmd == "build":
        cmd_build(a.dir)
    else:
        return cmd_check(a.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
