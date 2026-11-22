#!/usr/bin/env python3
"""Asigna y verifica IDs globalmente únicos de User Stories (`RCP-NNN-US-NNN`) y de Épicas (`RCP-NNN-EPC-NNN`).

    python us_ids.py next  --workspace <raíz> --rcp RCP-002 [--count N] [--also <raíz>...] [--git-ref <ref>...]
    python us_ids.py check --workspace <raíz> [--also <raíz>...] [--git-ref <ref>...]

El ID es `RCP-NNN-US-NNN`, donde `RCP-NNN` es el Requirement Context Pack que origina la historia. El DSP se genera
después de identificar las historias y no forma parte del ID. Cada RCP tiene su propia numeración, y el archivo se
llama `<ID>.md` o `<ID>-<slug>.md`. El código de producto (`product`, MAYÚSCULAS, p. ej. `CL2`) es un metadato opcional
que no forma parte del ID. Un ID previo (`HU-NN-NN`, `US-001`, `CL2-US-014`) se conserva en `legacy_id`.

La Épica (`type: EPC`, ID `RCP-NNN-EPC-NNN`) agrupa historias mediante `related`. `check` verifica que cada US citada
exista en las KB revisadas y que ninguna US pertenezca a dos épicas. `next` solo numera US; las épicas no desplazan
su numeración.

Solo se recorre `requirements/` de cada raíz; `--exclude <glob>` (repetible, p. ej. `requirements/examples/*`) omite rutas.
`--also` suma otras KB (raíces de workspace) y `--git-ref` suma ramas o tags del repositorio del workspace
(`origin/develop`, `origin/feature/x`), para detectar colisiones entre quienes numeran en paralelo. La asignación es
local: dos personas pueden elegir el mismo número en ramas distintas; `check --git-ref` en la revisión de la rama
y en G3/G6 lo detecta antes de integrar. No hay un servidor central de numeración.
Requiere PyYAML. Código de salida 1 si `check` encuentra errores.
"""
import argparse
import collections
import fnmatch
import pathlib
import re
import subprocess
import sys

import yaml

CONTEXT = "requirements/context-packs/"
KINDS = {"US", "EPC"}
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
RCP_ID = re.compile(r"RCP-\d{3,}")
US_ID = re.compile(r"RCP-\d{3,}-US-\d{3,}")
EPC_ID = re.compile(r"RCP-\d{3,}-EPC-\d{3,}")
PRODUCT = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*")
SKIP = {".git", "node_modules", "__pycache__"}


def parse(text):
    m = FRONT.match(text)
    if not m:
        return None
    try:
        meta = yaml.safe_load(m.group(1))
    except yaml.YAMLError:
        return None
    return meta if isinstance(meta, dict) else None


def collect_dir(root, exclude=()):
    """US y EPC de una raíz de workspace: todo documento con `type` US o EPC bajo `requirements/`.

    Solo se recorre `requirements/`: copias de modelos o ejemplos en otras carpetas del workspace no cuentan.
    `exclude` son patrones glob (relativos a la raíz, p. ej. `requirements/examples/*`) para omitir más rutas.
    """
    out = []
    root = pathlib.Path(root).resolve()
    base = root / "requirements"
    if not base.is_dir():
        return out
    for p in sorted(base.rglob("*.md")):
        rel_posix = p.relative_to(root).as_posix()
        if SKIP & set(p.relative_to(root).parts) or any(fnmatch.fnmatch(rel_posix, g) for g in exclude):
            continue
        meta = parse(p.read_text(encoding="utf-8", errors="ignore"))
        if meta and str(meta.get("type")) in KINDS:
            rel = p.relative_to(root).as_posix()
            out.append({"where": f"{root.name}:{rel}", "key": (str(root), rel), "name": p.name, "meta": meta})
    return out


def collect_ref(workspace, ref):
    out = []
    ws = str(pathlib.Path(workspace).resolve())
    ls = subprocess.run(["git", "-C", ws, "ls-tree", "-r", "--name-only", ref], capture_output=True, text=True, encoding="utf-8")
    if ls.returncode != 0:
        raise SystemExit(f"ERROR: no se puede leer la referencia git '{ref}': {ls.stderr.strip()}")
    for path in ls.stdout.splitlines():
        if not path.endswith(".md") or CONTEXT not in path:
            continue
        show = subprocess.run(["git", "-C", ws, "show", f"{ref}:{path}"], capture_output=True, text=True, encoding="utf-8")
        meta = parse(show.stdout) if show.returncode == 0 else None
        if meta and str(meta.get("type")) in KINDS:
            out.append({"where": f"{ref}:{path}", "key": (ws, path), "name": pathlib.PurePosixPath(path).name, "meta": meta})
    return out


def gather(workspace, also, refs, exclude=()):
    items = collect_dir(workspace, exclude)
    for other in also or []:
        items += collect_dir(other, exclude)
    for ref in refs or []:
        items += collect_ref(workspace, ref)
    return items


def problems(items):
    errors, warnings = [], []
    by_id = collections.defaultdict(list)
    legacy = collections.defaultdict(list)
    us_ids = set()
    membership = collections.defaultdict(list)  # US -> [(clave del documento, dónde)] de las épicas que la citan
    for it in items:
        meta, where = it["meta"], it["where"]
        kind, ident, prod = str(meta.get("type")), str(meta.get("id", "")), meta.get("product")
        pattern, label = (US_ID, "RCP-NNN-US-NNN (p. ej. RCP-002-US-001)") if kind == "US" else (EPC_ID, "RCP-NNN-EPC-NNN (p. ej. RCP-002-EPC-001)")
        if not pattern.fullmatch(ident):
            errors.append(f"{where}: id '{ident}' no cumple {label}")
        elif not re.fullmatch(re.escape(ident) + r"(-[^/]+)?\.md", it["name"]):
            errors.append(f"{where}: el archivo debe llamarse '{ident}.md' o '{ident}-<slug>.md'")
        if prod is not None and not (isinstance(prod, str) and PRODUCT.fullmatch(prod)):
            errors.append(f"{where}: product ({prod!r}) debe ser un código en MAYÚSCULAS, p. ej. CL2, o omitirse")
        by_id[ident].append((it["key"], where))
        if meta.get("legacy_id"):
            legacy[str(meta["legacy_id"])].append((it["key"], where))
        if kind == "US":
            us_ids.add(ident)
        else:
            for us in meta.get("related") or []:
                if isinstance(us, str) and US_ID.fullmatch(us):
                    membership[us].append((it["key"], where))
    # El mismo archivo visto en el workspace y en una rama es un solo documento; una colisión es otro archivo con el mismo ID.
    for ident, pairs in by_id.items():
        if len({k for k, _ in pairs}) > 1:
            errors.append(f"ID duplicado {ident}: " + "; ".join(sorted({w for _, w in pairs})))
    for lid, pairs in legacy.items():
        if len({k for k, _ in pairs}) > 1:
            warnings.append(f"legacy_id repetido: {lid}: " + "; ".join(sorted({w for _, w in pairs})))
    # Épicas: cada US citada debe existir y pertenecer a una sola épica.
    for us, pairs in membership.items():
        if us not in us_ids:
            wheres = "; ".join(sorted({w for _, w in pairs}))
            errors.append(f"épica cita la US {us}, que no existe en las KB revisadas: {wheres}")
        if len({k for k, _ in pairs}) > 1:
            errors.append(f"US {us} pertenece a más de una épica: " + "; ".join(sorted({w for _, w in pairs})))
    return errors, warnings


def number(ident, rcp):
    m = re.fullmatch(re.escape(rcp) + r"-US-(\d+)", ident)
    return int(m.group(1)) if m else None


def cmd_next(a):
    if not RCP_ID.fullmatch(a.rcp):
        raise SystemExit("ERROR: --rcp debe ser el ID del RCP de origen en MAYÚSCULAS (p. ej. RCP-002)")
    items = gather(a.workspace, a.also, a.git_ref, a.exclude)
    used = [n for n in (number(str(i["meta"].get("id", "")), a.rcp) for i in items) if n is not None]
    start = (max(used) if used else 0) + 1
    for n in range(start, start + a.count):
        print(f"{a.rcp}-US-{n:03d}")
    return 0


def cmd_check(a):
    items = gather(a.workspace, a.also, a.git_ref, a.exclude)
    errors, warnings = problems(items)
    for e in errors:
        print("ERROR", e)
    for w in warnings:
        print("AVISO", w)
    us = sum(1 for i in items if str(i["meta"].get("type")) == "US")
    print(f"{us} User Stories y {len(items) - us} Épicas revisadas, {len(errors)} errores, {len(warnings)} avisos.")
    return 1 if errors else 0


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("next", "check"):
        s = sub.add_parser(name)
        s.add_argument("--workspace", default=".")
        s.add_argument("--also", action="append", default=[], help="otra raíz de KB a incluir (repetible)")
        s.add_argument("--exclude", action="append", default=[], help="patrón glob relativo a la raíz para omitir rutas dentro de requirements/ (repetible)")
        s.add_argument("--git-ref", action="append", default=[], help="rama o tag del repositorio del workspace (repetible)")
        if name == "next":
            s.add_argument("--rcp", required=True, help="ID del RCP (RCP-NNN) que origina las historias")
            s.add_argument("--count", type=int, default=1)
    a = ap.parse_args(argv)
    return cmd_next(a) if a.cmd == "next" else cmd_check(a)


if __name__ == "__main__":
    sys.exit(main())
