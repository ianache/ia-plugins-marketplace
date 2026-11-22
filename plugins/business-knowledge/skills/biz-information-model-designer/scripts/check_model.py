"""Valida la consistencia de un modelo de información conceptual (IMD-NNN).

Uso:
    python check_model.py <modelo.md> [--skip-links] [--extract <carpeta>]

Comprueba:
- que cada concepto de los diagramas Mermaid esté en la tabla de conceptos (columna "Nombre en diagrama") y viceversa;
- que cada relación R-NN tenga cardinalidad, una clasificación válida y fuente;
- que las relaciones INFERENCE del diagrama estén marcadas con "(inf.)" (aviso si ninguna lo está);
- que no queden textos de plantilla "<...>";
- que la sección "Diagrama de Estados" sea coherente (diagrama, tabla de estados y transiciones ECA);
- que los enlaces relativos a archivos .md existan (salvo --skip-links).
Con --extract escribe cada diagrama Mermaid como d1.mmd, d2.mmd… en <carpeta> para validarlo con mermaid-cli.
Sale con código 1 si hay errores.
"""
import os
import re
import sys

CLASSES = ("FACT", "INFERENCE", "UNKNOWN", "RETIRADA")
EDGE = re.compile(r"^\s*([A-Z0-9_]+)\s+[|}o][|o]?--[|o][|{o]?\s+([A-Z0-9_]+)\s*:\s*\"([^\"]*)\"")
ENTITY_ONLY = re.compile(r"^\s*([A-Z0-9_]+)\s*\{")


def table_rows(text, heading):
    """Filas de la primera tabla bajo un encabezado '## N. <heading>'."""
    m = re.search(r"^## \d+\. " + re.escape(heading) + r".*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        return None
    rows = [l for l in m.group(1).splitlines() if l.startswith("|")]
    if len(rows) < 2:
        return []
    header = [c.strip() for c in rows[0].strip("|").split("|")]
    out = []
    for line in rows[2:]:
        cells = [c.strip() for c in line.strip("|").split("|")]
        out.append(dict(zip(header, cells)))
    return out


def all_tables(chunk):
    """Todas las tablas markdown de un texto, como listas de dicts."""
    tables, rows = [], []
    for line in chunk.splitlines() + [""]:
        if line.startswith("|"):
            rows.append(line)
        elif rows:
            if len(rows) >= 2:
                header = [c.strip() for c in rows[0].strip("|").split("|")]
                tables.append([dict(zip(header, [c.strip() for c in r.strip("|").split("|")]))
                               for r in rows[2:]])
                tables[-1].insert(0, {"__header__": header})
            rows = []
    return tables


def check_states(text, errors, warnings):
    """Valida la sección 'Diagrama de Estados'. Devuelve cuántos conceptos tienen diagrama."""
    m = re.search(r"^## \d+\. Diagrama de Estados.*?$(.*?)(?=^## |\Z)", text, re.M | re.S)
    if not m:
        warnings.append("Falta la sección 'Diagrama de Estados' (escribe 'No aplica' si ningún concepto tiene estados relevantes).")
        return 0
    body = m.group(1)
    parts = re.split(r"^### (.+)$", body, flags=re.M)
    subs = list(zip(parts[1::2], parts[2::2]))
    if not subs:
        if not re.search(r"No aplica", body, re.I):
            errors.append("Diagrama de Estados: sin subsecciones '### <Concepto>' ni 'No aplica'.")
        return 0
    seen_ids = set()
    for title, chunk in subs:
        title = title.strip()
        blocks = [b for b in re.findall(r"```mermaid\n(.*?)```", chunk, re.S) if "stateDiagram" in b]
        if not blocks:
            errors.append(f"Estados de '{title}': falta el diagrama stateDiagram.")
            continue
        edge = re.compile(r"^\s*(\[\*\]|[A-Z0-9_]+)\s*-->\s*(\[\*\]|[A-Z0-9_]+)\s*(?::\s*(.*))?$")
        diag_states, diag_edges = set(), set()
        for line in blocks[0].splitlines():
            e = edge.match(line)
            if e:
                diag_edges.add((e.group(1), e.group(2)))
                diag_states.update(s for s in e.groups()[:2] if s != "[*]")
                if not (e.group(3) or "").strip():
                    errors.append(f"Estados de '{title}': transición {e.group(1)} --> {e.group(2)} sin evento en la etiqueta.")
        if not diag_edges:
            errors.append(f"Estados de '{title}': el diagrama no tiene transiciones.")
        if not any(a == "[*]" for a, _ in diag_edges):
            errors.append(f"Estados de '{title}': falta el estado inicial ([*] --> ...).")
        tables = all_tables(chunk)
        states_t = next((t for t in tables if "Nombre en diagrama" in t[0]["__header__"]), None)
        trans_t = next((t for t in tables if "Evento" in t[0]["__header__"]), None)
        if states_t is None:
            errors.append(f"Estados de '{title}': falta la tabla de estados.")
        else:
            names = set()
            for row in states_t[1:]:
                n = row.get("Nombre en diagrama", "").strip("`")
                names.add(n)
                if not row.get("Descripción"):
                    errors.append(f"Estados de '{title}': el estado {n or '?'} no tiene descripción.")
            for s in sorted(diag_states - names):
                errors.append(f"Estados de '{title}': '{s}' está en el diagrama pero no en la tabla de estados.")
            for s in sorted(names - diag_states):
                errors.append(f"Estados de '{title}': '{s}' está en la tabla pero no en el diagrama.")
        if trans_t is None:
            errors.append(f"Estados de '{title}': falta la tabla de transiciones ECA.")
        else:
            table_edges = set()
            for row in trans_t[1:]:
                tid = row.get("ID", "")
                if not re.fullmatch(r"T-[A-Z0-9_]+-\d{2,}", tid):
                    errors.append(f"Estados de '{title}': ID de transición inválido '{tid}'.")
                if tid in seen_ids:
                    errors.append(f"ID de transición duplicado: {tid}.")
                seen_ids.add(tid)
                table_edges.add((row.get("Origen", "").strip("`"), row.get("Destino", "").strip("`")))
                for col in ("Origen", "Destino", "Evento", "Condición (constraints)", "Acción", "Fuente"):
                    if not row.get(col):
                        errors.append(f"{tid}: falta '{col}'.")
                if not any(c in row.get("Clasificación", "") for c in CLASSES):
                    errors.append(f"{tid}: la clasificación debe incluir {', '.join(CLASSES)}.")
            for a, b in sorted(diag_edges - table_edges):
                if b == "[*]":
                    continue  # el cierre del ciclo no requiere regla ECA propia
                warnings.append(f"Estados de '{title}': {a} --> {b} está en el diagrama pero sin fila ECA.")
            for a, b in sorted(table_edges - diag_edges):
                warnings.append(f"Estados de '{title}': {a} --> {b} tiene fila ECA pero no está en el diagrama.")
    return len(subs)


def main(path, skip_links, extract_dir=None):
    text = open(path, encoding="utf-8").read()
    errors, warnings = [], []
    if extract_dir:
        os.makedirs(extract_dir, exist_ok=True)
        for i, block in enumerate(re.findall(r"```mermaid\n(.*?)```", text, re.S), 1):
            with open(os.path.join(extract_dir, f"d{i}.mmd"), "w", encoding="utf-8") as fh:
                fh.write(block)
            print(f"Diagrama extraído: {os.path.join(extract_dir, f'd{i}.mmd')}")

    diagram_entities, inf_edges = set(), 0
    for block in re.findall(r"```mermaid\n(.*?)```", text, re.S):
        if "erDiagram" not in block:
            continue
        for line in block.splitlines():
            m = EDGE.match(line)
            if m:
                diagram_entities.update([m.group(1), m.group(2)])
                inf_edges += "(inf.)" in m.group(3)
            elif ENTITY_ONLY.match(line):
                diagram_entities.add(ENTITY_ONLY.match(line).group(1))
    if not diagram_entities:
        errors.append("No hay diagramas erDiagram con relaciones.")

    concepts = table_rows(text, "Conceptos")
    if concepts is None:
        errors.append("Falta la sección '## 4. Conceptos'.")
        concepts = []
    table_names = set()
    for row in concepts:
        name = row.get("Nombre en diagrama", "")
        if not name:
            errors.append(f"Concepto '{row.get('Concepto', '?')}' sin 'Nombre en diagrama'.")
            continue
        if name.startswith(("—", "-")):
            continue  # concepto derivado: no aparece en diagramas
        for n in re.split(r"[,/ ]+", name):
            if n:
                table_names.add(n.strip("`"))
        if not row.get("Glosario"):
            errors.append(f"Concepto '{row.get('Concepto')}' sin columna Glosario.")
        if not row.get("Fuente"):
            errors.append(f"Concepto '{row.get('Concepto')}' sin fuente.")
    for e in sorted(diagram_entities - table_names):
        errors.append(f"'{e}' aparece en un diagrama pero no en la tabla de conceptos.")
    for e in sorted(table_names - diagram_entities):
        warnings.append(f"'{e}' está en la tabla de conceptos pero en ningún diagrama.")

    relations = table_rows(text, "Relaciones")
    if relations is None:
        errors.append("Falta la sección '## 5. Relaciones'.")
        relations = []
    seen, n_inf = set(), 0
    for row in relations:
        rid = row.get("ID", "")
        if not re.fullmatch(r"R-\d{2,}", rid):
            errors.append(f"Relación con ID inválido: '{rid}'.")
        if rid in seen:
            errors.append(f"ID de relación duplicado: {rid}.")
        seen.add(rid)
        cls = row.get("Clasificación", "")
        if not any(c in cls for c in CLASSES):
            errors.append(f"{rid}: la clasificación debe incluir {', '.join(CLASSES)}.")
        n_inf += "INFERENCE" in cls
        for col in ("Relación", "Cardinalidad", "Fuente"):
            if not row.get(col):
                errors.append(f"{rid}: falta '{col}'.")
    if n_inf and not inf_edges:
        warnings.append("Hay relaciones INFERENCE en la tabla, pero ninguna arista del diagrama lleva '(inf.)'.")

    n_states = check_states(text, errors, warnings)

    for placeholder in re.findall(r"<[A-Za-zÁÉÍÓÚáéíóúñ][^<>\n]{2,}>", text):
        if not placeholder.startswith("<a ") and not placeholder.startswith("</"):
            errors.append(f"Texto de plantilla sin completar: {placeholder}")

    if not skip_links:
        base = os.path.dirname(os.path.abspath(path))
        for target in sorted(set(re.findall(r"\]\(([^)#:]+\.md)(?:#[^)]*)?\)", text))):
            if not os.path.exists(os.path.normpath(os.path.join(base, target))):
                errors.append(f"Enlace roto: {target}")

    for w in warnings:
        print("AVISO", w)
    for e in errors:
        print("ERROR", e)
    print(f"{len(diagram_entities)} conceptos en diagramas, {len(relations)} relaciones, "
          f"{n_states} conceptos con diagrama de estados, "
          f"{len(errors)} errores, {len(warnings)} avisos.")
    return 1 if errors else 0


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    argv = sys.argv[1:]
    extract = None
    if "--extract" in argv:
        i = argv.index("--extract")
        if i + 1 >= len(argv):
            sys.exit(__doc__)
        extract = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    args = [a for a in argv if a != "--skip-links"]
    if len(args) != 1:
        sys.exit(__doc__)
    sys.exit(main(args[0], "--skip-links" in argv, extract))
