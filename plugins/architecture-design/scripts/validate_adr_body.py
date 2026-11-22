#!/usr/bin/env python3
"""Structural validator for the body of ADR documents (visual section, element catalog, variation points, lightweight ATAM).

Does not assert semantic truth, quality measures, sources or human approval. Mermaid rendering is optional
(--render, local only) and needs mmdc on PATH or in the MMDC environment variable.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

SECTIONS = [
    'Contexto y drivers',
    'Escenarios de calidad afectados',
    'Opciones consideradas',
    'Decisión',
    'Representación visual',
    'Evaluación ATAM',
    'Consecuencias',
    'Riesgos, dependencias y preguntas abiertas',
    'Evidencia y procedencia',
]
ATAM_TYPES = ['Sensibilidad', 'Compromiso', 'Riesgo', 'No-riesgo']
BINDING_TIMES = ('diseño', 'construcción', 'despliegue', 'ejecución')


def headings(body):
    """Return (level, title, content) for every markdown heading outside fenced code blocks."""
    items, current, buffer, in_code = [], None, [], False
    for line in body.splitlines():
        if line.lstrip().startswith('```'):
            in_code = not in_code
        match = None if in_code else re.match(r'^(#{1,6}) (.+?)\s*$', line)
        if match:
            if current:
                items.append((current[0], current[1], '\n'.join(buffer)))
            current, buffer = (len(match.group(1)), match.group(2)), []
        else:
            buffer.append(line)
    if current:
        items.append((current[0], current[1], '\n'.join(buffer)))
    return items


def scope(items, title, level):
    """Text of a heading and all of its sub-headings, up to the next heading of the same or higher level."""
    out, inside = [], False
    for lvl, name, content in items:
        if lvl == level and name == title:
            inside = True
            out.append(content)
        elif inside and lvl <= level:
            break
        elif inside:
            out.append(f'{"#" * lvl} {name}\n{content}')
    return '\n'.join(out)


def table_rows(text):
    """Cells of every table row in text, without separator lines."""
    rows = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped.startswith('|') or re.match(r'^\|\s*:?-{2,}', stripped):
            continue
        rows.append([cell.strip() for cell in stripped.strip('|').split('|')])
    return rows


def mermaid_blocks(text):
    return re.findall(r'```mermaid\n(.*?)```', text, re.S)


def render_error(block, mmdc):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / 'diagram.mmd'
        src.write_text(block, encoding='utf-8')
        cmd = [mmdc, '-i', str(src), '-o', str(Path(tmp) / 'diagram.svg')]
        config = os.environ.get('MMDC_PUPPETEER_CONFIG')
        if config:
            cmd += ['-p', config]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        if result.returncode == 0:
            return None
        lines = (result.stderr or result.stdout).strip().splitlines()
        return lines[-1] if lines else 'mmdc failed'


def check(path, render=False):
    """Return None when the file is not an ADR, otherwise a list of errors (empty when valid)."""
    text = Path(path).read_text(encoding='utf-8')
    match = re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)', text, re.S)
    if not match:
        return ['missing YAML frontmatter']
    frontmatter = yaml.safe_load(match.group(1))
    if not isinstance(frontmatter, dict) or frontmatter.get('type') != 'ADR':
        return None

    items = headings(text[match.end():])
    errors = []
    if re.search(r'^> TEMPLATE:', text, re.M):
        errors.append('plantilla sin completar (quitar el bloque "> TEMPLATE:")')
    level2 = {name for lvl, name, _ in items if lvl == 2}
    for section in SECTIONS:
        if section not in level2:
            errors.append(f'falta la sección "## {section}"')

    visual = scope(items, 'Representación visual', 2)
    blocks = mermaid_blocks(visual)
    if not blocks and not re.search(r'^Visual: no aplica — \S', visual, re.M):
        errors.append('sin diagrama Mermaid ni "Visual: no aplica — <motivo>"')
    if render:
        mmdc = os.environ.get('MMDC') or shutil.which('mmdc')
        if not mmdc:
            errors.append('--render solicitado pero mmdc no está disponible (PATH o variable MMDC)')
        else:
            for block in blocks:
                problem = render_error(block, mmdc)
                if problem:
                    errors.append(f'Mermaid no renderiza: {problem}')

    diagram = '\n'.join(blocks)
    diagram_elements = set(re.findall(r'\bE\d{2}\b', diagram))
    diagram_vps = set(re.findall(r'\bVP-\d{2}\b', diagram))

    catalog = [r for r in table_rows(scope(items, 'Catálogo de elementos', 3)) if re.fullmatch(r'E\d{2}', r[0])]
    catalog_ids = {r[0] for r in catalog}
    for element in sorted(diagram_elements - catalog_ids):
        errors.append(f'{element} aparece en el diagrama sin fila en el catálogo')
    for element in sorted(catalog_ids - diagram_elements):
        errors.append(f'{element} está en el catálogo sin nodo en el diagrama')

    vp_rows = [r for r in table_rows(scope(items, 'Puntos de variación', 3)) if re.fullmatch(r'VP-\d{2}', r[0])]
    vp_ids = {r[0] for r in vp_rows}
    catalog_vps = set()
    for row in catalog:
        if len(row) < 6 or row[3] not in ('Sí', 'No'):
            errors.append(f'{row[0]}: el catálogo necesita "¿Punto de variación?" = Sí o No y la trazabilidad')
        elif row[3] == 'Sí':
            if not re.fullmatch(r'VP-\d{2}', row[4]):
                errors.append(f'{row[0]} es punto de variación sin VP-nn en la columna VP')
            else:
                catalog_vps.add(row[4])
    for vp in sorted(diagram_vps - vp_ids):
        errors.append(f'{vp} aparece en el diagrama sin fila en "Puntos de variación"')
    for vp in sorted(catalog_vps - vp_ids):
        errors.append(f'{vp} referenciado en el catálogo sin fila en "Puntos de variación"')
    for vp in sorted(vp_ids - catalog_vps):
        errors.append(f'{vp} no está referenciado por ningún elemento del catálogo')
    for row in vp_rows:
        if len(row) < 7:
            errors.append(f'{row[0]}: faltan columnas en "Puntos de variación"')
            continue
        if not row[1] or not row[2]:
            errors.append(f'{row[0]}: falta dimensión o variantes')
        if not any(time in row[3] for time in BINDING_TIMES):
            errors.append(f'{row[0]}: momento de vinculación no reconocido')
        if not row[5]:
            errors.append(f'{row[0]}: falta responsable')

    scenarios = [r for r in table_rows(scope(items, 'Escenarios de calidad afectados', 2)) if re.fullmatch(r'QA-\d{2}', r[0])]
    scenario_ids = {r[0] for r in scenarios}
    if not scenarios:
        errors.append('no hay escenarios de calidad QA-nn')
    for row in scenarios:
        if len(row) < 9 or not row[7]:
            errors.append(f'{row[0]}: falta la medida de respuesta (usar [PENDIENTE: arquitecto] si no hay fuente)')

    atam_text = scope(items, 'Evaluación ATAM', 2)
    atam = [r for r in table_rows(atam_text) if r and r[0] in ATAM_TYPES]
    for kind in ATAM_TYPES:
        has_rows = any(r[0] == kind for r in atam)
        has_justification = re.search(rf'Sin registros de tipo {re.escape(kind)}: \S', atam_text)
        if not has_rows and not has_justification:
            errors.append(f'ATAM sin registros de tipo {kind} ni justificación "Sin registros de tipo {kind}: <motivo>"')
    for row in atam:
        if len(row) < 6:
            errors.append(f'{row[0]} {row[1] if len(row) > 1 else ""}: faltan columnas en la evaluación ATAM')
            continue
        referenced = re.findall(r'QA-\d{2}', row[3])
        if not referenced or any(ref not in scenario_ids for ref in referenced):
            errors.append(f'{row[1]}: el escenario debe referenciar un QA-nn existente')
    return errors


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    render = '--render' in args
    paths = [arg for arg in args if not arg.startswith('-')]
    failures = 0
    for path in paths:
        errors = check(path, render)
        if errors is None:
            print(f'{path}: SKIP (no es ADR)')
        elif errors:
            print(f'{path}: FAIL (cuerpo ADR): ' + '; '.join(errors))
            failures += 1
        else:
            print(f'{path}: PASS (cuerpo ADR)')
    return int(failures > 0)


if __name__ == '__main__':
    raise SystemExit(main())
