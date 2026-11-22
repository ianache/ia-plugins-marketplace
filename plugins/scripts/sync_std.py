#!/usr/bin/env python3
"""Sincroniza STD-OKF-001 desde el maestro `plugins/STD-OKF-001-v<ver>-stable.md`.

  --check   Informa y termina con 1 si alguna copia, lista de tipos o referencia de versión difiere del maestro.
  --apply   Copia el maestro a cada copia, regenera las listas de tipos de los validadores y actualiza
            las referencias a la versión anterior. No toca CHANGELOG.md ni AGENTS.md (historial y reglas).

Ver plugins/AGENTS.md: el informe de impacto y la aprobación humana van antes de --apply.
"""
import argparse
import re
import sys
from pathlib import Path

PLUGINS = Path(__file__).resolve().parents[1]
MASTER_RE = re.compile(r'STD-OKF-001-v(\d+\.\d+\.\d+)-stable\.md')
COPY_GLOBS = [
    '*/standards/STD-OKF-001*.md',
    '*/resources/STD-OKF-001*.md',
    '*/skills/*/resources/STD-OKF-001*.md',
]
SET_LINE_RE = re.compile(r'^(APPROVED|TYPES)\s*=.*$', re.M)
# Textos de referencia a la versión del estándar. Los históricos (CHANGELOG, AGENTS.md) no se tocan.
EXCLUDED_FROM_REFS = {'CHANGELOG.md', 'AGENTS.md', 'sync_std.py', 'test_sync_std.py'}


def master_path():
    found = list(PLUGINS.glob('STD-OKF-001-v*-stable.md'))
    if len(found) != 1:
        raise SystemExit(f'Se esperaba un único maestro en {PLUGINS}, hay {len(found)}')
    return found[0]


def version_of(master):
    return MASTER_RE.fullmatch(master.name).group(1)


def normalized(data):
    return data.replace(b'\r\n', b'\n')


def copies(master):
    found = set()
    for pattern in COPY_GLOBS:
        found.update(p for p in PLUGINS.glob(pattern) if p != master)
    return sorted(found)


def approved_codes(text):
    """Códigos de los tipos aprobados: filas de tablas bajo encabezados de nivel 2 que no son propuestas."""
    codes, section = set(), ''
    for line in text.split('\n'):
        if line.startswith('## '):
            section = line
            continue
        if re.search(r'propuest|pendiente', section, re.I):
            continue
        match = re.match(r'^\|\s*`?([A-Z][A-Z0-9]{1,5})`?\s*\|', line)
        if match and match.group(1) not in {'TIPO', 'SIGLA'}:
            codes.add(match.group(1))
    return codes


def validators():
    result = []
    for path in sorted(PLUGINS.glob('*/scripts/*.py')):
        matches = SET_LINE_RE.findall(path.read_text(encoding='utf-8'))
        if matches:
            if len(matches) != 1:
                raise SystemExit(f'{path}: se esperaba una lista de tipos, hay {len(matches)}')
            result.append(path)
    return result


def render_set(codes):
    return "APPROVED=set('" + ' '.join(sorted(codes)) + "'.split())"


def current_codes(text):
    match = SET_LINE_RE.search(text)
    return set(re.findall(r'[A-Z][A-Z0-9]{1,5}', match.group(0).split('=', 1)[1]))


# Referencias a una versión del estándar: "STD-OKF-001-vX.Y.Z-stable", "STD-OKF-001 vX.Y.Z-stable" o "vX.Y.Z-stable" suelto.
# Cualquier versión distinta de la maestra es obsoleta: se reescribe a la vigente. No se fija a ninguna versión concreta.
VERSION_REF = re.compile(r'(?<![\w.-])(STD-OKF-001[ -])?v(\d+\.\d+\.\d+)-stable')


def stale_versions(text, ver):
    """Versiones del estándar distintas de `ver` que aparecen en `text`."""
    return sorted({m.group(2) for m in VERSION_REF.finditer(text) if m.group(2) != ver})


def refresh_versions(text, ver):
    """Reescribe a `ver` toda referencia a otra versión del estándar; conserva el prefijo STD-OKF-001 que tuviera."""
    return VERSION_REF.sub(lambda m: f'{m.group(1) or ""}v{ver}-stable', text)


def text_files():
    for path in PLUGINS.rglob('*'):
        if path.is_file() and path.suffix in {'.md', '.py', '.json', '.yaml', '.yml', '.html'} and '.git' not in path.parts:
            if path.name in EXCLUDED_FROM_REFS or path.name.startswith('STD-OKF-001'):
                continue
            yield path


def check(master, ver):
    problems = []
    master_norm = normalized(master.read_bytes())
    master_text = master.read_text(encoding='utf-8')
    expected = approved_codes(master_text)
    for copy in copies(master):
        if copy.name != master.name and MASTER_RE.fullmatch(copy.name):
            problems.append(f'nombre de copia distinto del maestro: {copy.relative_to(PLUGINS)}')
        if normalized(copy.read_bytes()) != master_norm:
            problems.append(f'copia distinta: {copy.relative_to(PLUGINS)}')
    for path in validators():
        codes = current_codes(path.read_text(encoding='utf-8'))
        if codes != expected:
            problems.append(f'lista de tipos distinta: {path.relative_to(PLUGINS)} (faltan {sorted(expected - codes)}, sobran {sorted(codes - expected)})')
    for path in text_files():
        text = path.read_text(encoding='utf-8', errors='replace')
        old = stale_versions(text, ver)
        if old:
            problems.append(f'referencia a versión anterior {", ".join(old)}: {path.relative_to(PLUGINS)}')
    return problems


def apply(master, ver):
    master_bytes = master.read_bytes()
    for copy in copies(master):
        target = copy.with_name(master.name) if MASTER_RE.fullmatch(copy.name) else copy
        if target != copy:
            copy.rename(target)
        target.write_bytes(master_bytes)
    expected = approved_codes(master.read_text(encoding='utf-8'))
    for path in validators():
        text = path.read_text(encoding='utf-8')
        path.write_text(SET_LINE_RE.sub(lambda _: render_set(expected), text, count=1), encoding='utf-8')
    changed = []
    for path in text_files():
        text = path.read_text(encoding='utf-8')
        new = refresh_versions(text, ver)
        if new != text:
            path.write_text(new, encoding='utf-8')
            changed.append(path.relative_to(PLUGINS))
    return changed


def main(argv=None):
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check', action='store_true')
    mode.add_argument('--apply', action='store_true')
    args = parser.parse_args(argv)
    master = master_path()
    ver = version_of(master)
    if args.check:
        problems = check(master, ver)
        for problem in problems:
            print(problem)
        print(f'maestro {master.name}: {len(problems)} discrepancia(s)')
        return 1 if problems else 0
    changed = apply(master, ver)
    print(f'maestro {master.name}: {len(changed)} archivo(s) con referencias actualizadas')
    return 0


if __name__ == '__main__':
    sys.exit(main())
