#!/usr/bin/env python3
"""Mantiene el glosario de negocio: un documento OKF `type: TRM` por término en business/terms/ y su catálogo `type: CTLG` (CTLG-TRM.md).

Uso (<dir> es la carpeta del glosario, normalmente <workspace>/business/terms):
    python glossary.py new <dir> "<Nombre>" --product <PRODUCTO>   # crea TRM-NNN-<slug>.md desde la plantilla
    python glossary.py build <dir>   # copia la Definición a `description`, deriva `sources` y regenera CTLG-TRM.md; elimina index.md obsoleto
    python glossary.py check <dir>   # valida términos y catálogo; sale con código 1 si hay errores
Requiere PyYAML. No aprueba definiciones: solo comprueba estructura y consistencia.
El catálogo no repite definiciones: solo ID, término, sinónimos, estado y versión, con enlace a cada TRM.
"""
import argparse
import glob
import os
import re
import sys
import unicodedata
from datetime import datetime, timezone

import yaml

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "templates", "term.md")
CATALOG_ID = "CTLG-TRM"
CATALOG_FILE = CATALOG_ID + ".md"
CATALOG_BY = "biz-glossary-curator/2.0.0"
FILE_RE = re.compile(r"^(TRM-\d{3,})-[a-z0-9-]+\.md$")
FIELD = re.compile(r"^- \*\*(.+?):\*\*\s*(.*)$")
SOURCE = re.compile(r"^\s+- \[(N[123])\]\s+(.+)$")
CITATION = re.compile(r"\s*\[[^\]]*\]")
LINK = re.compile(r"\]\(([^)#]+\.md)(?:#[^)]*)?\)")
REQUIRED = ["Tipo", "Sinónimos", "Definición", "Ámbito", "Fuentes", "Clasificación", "Confianza", "Responsable"]
ALLOWED = {
    "Tipo": {"concepto", "término", "sigla", "abreviatura"},
    "Clasificación": {"fact", "decision", "assumption", "inference", "gap"},
    "Confianza": {"high", "medium", "low"},
}
NONE = {"", "—", "-"}
SLUG_MAX = 40
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)


def sort_key(text):
    """Orden alfabético del español: sin mayúsculas ni tildes, Ñ tras N, cifras primero."""
    text = text.lower().replace("ñ", "n\x7f")
    text = "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^0-9a-z\x7f ]", "", text).strip()


def slugify(text):
    text = "".join(c for c in unicodedata.normalize("NFD", text.lower()) if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text[:SLUG_MAX].rsplit("-", 1)[0] if len(text) > SLUG_MAX else text


def letter(name):
    key = sort_key(name)
    if not key:
        return "#"
    if key[0].isdigit():
        return "0–9"
    return "Ñ" if key.startswith("n\x7f") else key[0].upper()


def split_values(value):
    if value.strip() in NONE:
        return []
    return [v for v in (CITATION.sub("", p).strip() for p in value.split(";")) if v]


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)


class Term:
    def __init__(self, path):
        self.path, self.file = path, os.path.basename(path)
        m = FILE_RE.match(self.file)
        self.id = m.group(1) if m else None
        self.text = read(path)
        fm = FRONT.match(self.text)
        self.meta, self.error = {}, None
        if fm:
            try:
                self.meta = yaml.safe_load(fm.group(1)) or {}
            except yaml.YAMLError as ex:
                self.error = f"YAML inválido: {ex}"
        else:
            self.error = "frontmatter no encontrado"
        self.body = self.text[fm.end():] if fm else self.text
        self.title = str(self.meta.get("title", ""))
        self.fields, self.sources, current = {}, [], None
        for line in self.body.split("\n"):
            f = FIELD.match(line)
            if f:
                current = f.group(1)
                self.fields[current] = f.group(2).strip()
            elif current == "Fuentes" and SOURCE.match(line):
                level, rest = SOURCE.match(line).groups()
                pieces = rest.rsplit(" — ", 2)
                self.sources.append((level, pieces[1].strip() if len(pieces) == 3 else "", pieces[0].strip()))

    def aliases(self):
        names = split_values(self.fields.get("Sinónimos", ""))
        full = CITATION.sub("", self.fields.get("Forma completa", "")).strip()
        if full and full.lower() != "desconocida" and full not in NONE:
            names.append(full)
        return names

    def derived_sources(self):
        out, seen = [], set()
        for _, locator, title in self.sources:
            resource = re.sub(r":L\d+(?:-L?\d+)?$", "", locator)
            if resource and resource not in seen:
                seen.add(resource)
                out.append({"id": f"src-{len(out) + 1}", "resource": resource, "title": title})
        return out


def dump_scalar(value):
    return yaml.safe_dump(value, allow_unicode=True, width=10 ** 6, default_style='"').strip().removesuffix("...").strip()


def synced(t):
    """Texto del término con `description` y `sources` derivados del cuerpo (edición textual: conserva el resto del frontmatter)."""
    lines = FRONT.match(t.text).group(1).split("\n")
    out, skipping = [], False
    for line in lines:
        if re.match(r"^(description|sources):", line):
            skipping = True
            continue
        if skipping and re.match(r"^([ \t]+|- )", line):
            continue
        skipping = False
        out.append(line)
    out.append("description: " + dump_scalar(t.fields.get("Definición", "")))
    srcs = t.derived_sources()
    if srcs:
        out.append(yaml.safe_dump({"sources": srcs}, allow_unicode=True, sort_keys=False, width=10 ** 6).rstrip())
    else:
        out.append("sources: []")
    return "---\n" + "\n".join(out) + "\n---\n" + t.body


def load_terms(folder):
    return [Term(p) for p in sorted(glob.glob(os.path.join(folder, "TRM-*.md")))]


def _cell(text):
    return str(text).replace("|", "/").replace("\n", " ").strip()


def render_catalog_body(terms):
    """Cuerpo del CTLG-TRM: índice alfabético (sin definiciones). Cada término se define en su propio TRM."""
    rows = sorted(terms, key=lambda t: sort_key(t.title))
    out = ["# Catálogo de términos", "",
           "> **Definición:** índice de los términos (TRM) del glosario, ordenado alfabéticamente (A a Z, sin distinguir mayúsculas ni tildes). Un término se define únicamente en su documento `TRM-NNN`.",
           "> **Regla:** este documento no repite definiciones. Generado con `glossary.py build`; no editar a mano.", ""]
    group = None
    for t in rows:
        if letter(t.title) != group:
            group = letter(t.title)
            out += [f"## {group}", "", "| ID | Término | Sinónimos | Estado | Versión |", "|---|---|---|---|---|"]
        syn = "; ".join(t.aliases())
        out.append(f"| {t.id} | [{_cell(t.title)}]({t.file}) | {_cell(syn)} | {_cell(t.meta.get('status', ''))} | {_cell(t.meta.get('version', ''))} |")
    return "\n".join(out).strip() + "\n"


def _split_frontmatter(text):
    m = FRONT.match(text)
    return (yaml.safe_load(m.group(1)) or {}, text[m.end():]) if m else ({}, text)


def render_catalog(folder, terms, now=None):
    """Texto completo de CTLG-TRM.md. Conserva `version` y `status` editados por humanos y `generated.at` si nada cambió."""
    path = os.path.join(folder, CATALOG_FILE)
    old_meta, old_body = {}, None
    if os.path.exists(path):
        old_meta, old_body = _split_frontmatter(read(path))
    body = render_catalog_body(terms)
    products = sorted({str(t.meta.get("product")) for t in terms if t.meta.get("product")})
    owners = sorted({str(t.meta.get("owner")) for t in terms if t.meta.get("owner")})
    meta = {
        "type": "CTLG",
        "id": CATALOG_ID,
        "title": f"Catálogo de términos — {', '.join(products) if products else 'sin producto'}",
        "description": f"Índice ordenado de los {len(terms)} términos del glosario de negocio; cada término se define en su propio documento TRM.",
        "version": old_meta.get("version", "1.0.0"),
        "status": old_meta.get("status", "draft"),
        "owner": ", ".join(owners) if owners else "Por definir",
        "classification": "internal",
        "tags": ["business", "glossary", "catalogo"],
        "product": ", ".join(products) if products else "Por definir",
        "pack": "business-knowledge",
        "skill": "biz-glossary-curator",
        "generated": {"by": CATALOG_BY, "at": old_meta.get("generated", {}).get("at", "")},
        "sources": [{"id": f"src-{i + 1}", "resource": t.file, "title": t.title} for i, t in enumerate(terms)],
        "related": [t.id for t in terms],
    }
    unchanged = old_body is not None and old_body == body and {k: v for k, v in old_meta.items() if k != "generated"} == {k: v for k, v in meta.items() if k != "generated"}
    if unchanged:
        return read(path)
    meta["generated"]["at"] = (now or datetime.now(timezone.utc).astimezone()).isoformat(timespec="seconds")
    head = yaml.safe_dump(meta, allow_unicode=True, sort_keys=False, width=10 ** 6).rstrip()
    return f"---\n{head}\n---\n\n{body}"


def cmd_build(folder):
    for t in load_terms(folder):
        if t.error:
            continue
        new = synced(t)
        if new != t.text:
            write(t.path, new)
    terms = load_terms(folder)
    catalog = render_catalog(folder, terms)
    write(os.path.join(folder, CATALOG_FILE), catalog)
    legacy = os.path.join(folder, "index.md")
    if os.path.exists(legacy):
        os.remove(legacy)
        print("index.md obsoleto eliminado (sustituido por CTLG-TRM.md).")
    print(f"{len(terms)} términos sincronizados; {CATALOG_FILE} regenerado.")


def cmd_new(folder, name, product):
    terms = load_terms(folder)
    used = [int(t.id[4:]) for t in terms if t.id]
    tid = f"TRM-{(max(used) if used else 0) + 1:03d}"
    path = os.path.join(folder, f"{tid}-{slugify(name)}.md")
    os.makedirs(folder, exist_ok=True)
    write(path, read(TEMPLATE).replace("<Nombre del término>", name).replace("TRM-NNN", tid).replace("<PRODUCTO>", product))
    print(path)


def check_term(t, files):
    errors = [t.error] if t.error else []
    if not t.id:
        errors.append("el nombre debe ser TRM-NNN-<slug>.md")
    if t.meta.get("type") != "TRM":
        errors.append("el frontmatter debe tener type: TRM")
    if t.meta.get("id") != t.id:
        errors.append(f"el id '{t.meta.get('id')}' no coincide con el archivo")
    for key in ("title", "description", "owner", "product", "pack", "skill"):
        v = t.meta.get(key)
        if not v or str(v).startswith("<"):
            errors.append(f"frontmatter sin '{key}'")
    if t.title and not re.search(r"^# " + re.escape(t.title) + r"\s*$", t.body, flags=re.M):
        errors.append(f"falta el encabezado '# {t.title}' igual al title")
    for field in REQUIRED:
        v = t.fields.get(field)
        if v is None or (v in NONE and field not in ("Sinónimos", "Fuentes")) or v.startswith("<"):
            errors.append(f"campo obligatorio vacío o sin completar: {field}")
    for field, v in t.fields.items():
        if field not in REQUIRED and v.startswith("<"):
            errors.append(f"campo opcional con texto de plantilla: {field} (complétalo o borra la línea)")
    for field, allowed in ALLOWED.items():
        v = t.fields.get(field)
        if v and v not in allowed:
            errors.append(f"{field} = '{v}' no es uno de {sorted(allowed)}")
    definition = t.fields.get("Definición", "")
    if "…" in definition or definition.rstrip().endswith("..."):
        errors.append("Definición truncada (…): completar con el texto íntegro de la fuente; no se admite elipsis")
    if t.fields.get("Tipo") in ("sigla", "abreviatura") and t.fields.get("Forma completa", "") in NONE:
        errors.append("una sigla o abreviatura necesita 'Forma completa' (o 'Desconocida')")
    if not t.sources:
        errors.append("sin fuentes con formato '  - [N1|N2|N3] título — localizador — consultada AAAA-MM-DD'")
    elif not {"N1", "N2"} & {lvl for lvl, _, _ in t.sources} and t.fields.get("Clasificación") != "gap":
        errors.append("sin fuente N1/N2; la clasificación debe ser 'gap'")
    for lvl, locator, _ in t.sources:
        if not locator or locator.startswith("<"):
            errors.append(f"fuente [{lvl}] sin localizador")
    for target in LINK.findall(t.fields.get("Relacionados", "")):
        if os.path.basename(target) not in files:
            errors.append(f"Relacionados apunta a un término que no existe: {target}")
    if not t.error and synced(t) != t.text:
        errors.append("description o sources no coinciden con el cuerpo: ejecuta 'build'")
    return errors


def cmd_check(folder):
    terms, errors, ids, names = load_terms(folder), [], {}, {}
    files = {t.file for t in terms}
    for t in terms:
        errors += [f"{t.file}: {e}" for e in check_term(t, files)]
        if t.id in ids:
            errors.append(f"{t.file}: ID duplicado (también en {ids[t.id]})")
        ids[t.id] = t.file
        for name in [t.title] + t.aliases():
            key = sort_key(name)
            if key in names and names[key] != t.file:
                errors.append(f"{t.file}: '{name}' ya existe como término o alias en {names[key]}")
            names.setdefault(key, t.file)
    if os.path.exists(os.path.join(folder, "index.md")):
        errors.append("index.md obsoleto: ejecuta 'build' para eliminarlo (el índice es CTLG-TRM.md)")
    # Solo se admiten TRM-*.md y el catálogo CTLG-TRM.md; un glosario con otro type (p. ej. "Business Glossary") es un error.
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".md") or name == CATALOG_FILE or name.startswith("TRM-"):
            continue
        if name == "index.md":
            continue
        meta, _ = _split_frontmatter(read(os.path.join(folder, name)))
        errors.append(f"{name}: documento no permitido en business/terms/ (type: {meta.get('type', 'sin type')}); el glosario solo admite TRM-*.md y CTLG-TRM.md")
    cat = os.path.join(folder, CATALOG_FILE)
    if not os.path.exists(cat):
        errors.append(f"No existe {CATALOG_FILE}: ejecuta 'build'")
    else:
        text = read(cat)
        linked = {os.path.basename(x) for x in LINK.findall(text)}
        if linked - files:
            errors.append(f"{CATALOG_FILE}: filas sin término: {', '.join(sorted(linked - files))}")
        if files - linked:
            errors.append(f"{CATALOG_FILE}: términos fuera del catálogo: {', '.join(sorted(files - linked))}")
        meta, _ = _split_frontmatter(text)
        if meta.get("type") != "CTLG" or meta.get("id") != CATALOG_ID:
            errors.append(f"{CATALOG_FILE}: el frontmatter debe tener type: CTLG e id: {CATALOG_ID}")
        if render_catalog(folder, terms) != text:
            errors.append(f"{CATALOG_FILE}: el catálogo no coincide con los términos: ejecuta 'build'")
    for err in errors:
        print("ERROR", err)
    print(f"{len(terms)} términos revisados, {len(errors)} errores.")
    return 1 if errors else 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    n = sub.add_parser("new")
    n.add_argument("dir")
    n.add_argument("name")
    n.add_argument("--product", required=True)
    sub.add_parser("build").add_argument("dir")
    sub.add_parser("check").add_argument("dir")
    a = ap.parse_args(argv)
    if a.cmd == "new":
        cmd_new(a.dir, a.name, a.product)
    elif a.cmd == "build":
        cmd_build(a.dir)
    else:
        return cmd_check(a.dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
