#!/usr/bin/env python3
"""Verifica el contrato de contenido de un BSN (templates/scenario.md).

Comprueba: frontmatter OKF (vía validate_okf), las once secciones en orden, que cada
paso cite una BR existente, que los TRM citados existan y que no queden marcadores de
plantilla. Sin --workspace no verifica la existencia de BR/TRM y lo informa.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
import validate_okf  # noqa: E402

SECTIONS = [
    "## 1. Identificación", "## 2. Propósito y alcance", "## 3. Precondiciones",
    "## 4. Pasos del escenario", "## 5. Excepciones y alternativas", "## 6. Resultado y estados finales",
    "## 7. Términos TRM", "## 8. Trazabilidad", "## 9. Clasificación de afirmaciones",
    "## 10. Preguntas abiertas", "## 11. Readiness y aprobación",
]
READINESS = {"READY", "CONDITIONAL", "NOT_READY"}
PLACEHOLDER = re.compile(r"<[^>]+>|\bBSN-NNN\b|\bBR-NNN\b|\bTRM-NNN\b|\bSTK-NNN\b|\bBCAP-NNN\b|\bBO-NNN\b|\bEXC-NN\b")
ID_BR = re.compile(r"\bBR-\d{3,}\b")
ID_TRM = re.compile(r"\bTRM-\d{3,}\b")


def _section(body, title):
    start = body.find(title)
    if start < 0:
        return None
    nxt = body.find("\n## ", start + len(title))
    return body[start: nxt if nxt >= 0 else len(body)]


def check(path, workspace=None):
    issues, notes = [], []
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    issues += validate_okf.validate(str(p))
    body = text.split("\n---\n", 1)[1] if text.startswith("---") and "\n---\n" in text else text
    pos = -1
    for title in SECTIONS:
        i = body.find(title)
        if i < 0:
            issues.append(f"sección ausente: {title}")
        elif i < pos:
            issues.append(f"sección fuera de orden: {title}")
        else:
            pos = i
    steps = _section(body, "## 4. Pasos del escenario") or ""
    rows = [l for l in steps.splitlines() if l.startswith("| ") and not l.startswith("| Nº") and not l.startswith("|---")]
    if not rows:
        issues.append("la sección 4 no tiene pasos")
    for r in rows:
        if not ID_BR.search(r):
            issues.append(f"paso sin regla BR: {r[:60]}")
    cited_br = set(ID_BR.findall(body))
    cited_trm = set(ID_TRM.findall(body))
    if workspace:
        ws = Path(workspace)
        for b in sorted(cited_br):
            if not (ws / "business" / "rules" / f"{b}.md").exists():
                issues.append(f"BR citada no existe: {b}")
        for t in sorted(cited_trm):
            if not any((ws / "business" / "terms").glob(f"{t}-*.md")):
                issues.append(f"TRM citado no existe: {t}")
    else:
        notes.append("sin --workspace: no se verificó la existencia de BR ni TRM")
    readiness = _section(body, "## 11. Readiness y aprobación") or ""
    m = re.search(r"\*\*Readiness:\*\*\s*([A-Z_]+)", readiness)
    if not m or m.group(1) not in READINESS:
        issues.append("readiness ausente o no válido (READY, CONDITIONAL o NOT_READY)")
    for ph in sorted(set(PLACEHOLDER.findall(body))):
        issues.append(f"marcador de plantilla sin reemplazar: {ph}")
    return issues, notes


def main(argv=None):
    a = argparse.ArgumentParser()
    a.add_argument("file")
    a.add_argument("--workspace")
    args = a.parse_args(argv)
    issues, notes = check(args.file, args.workspace)
    print(f"{args.file}: " + ("OK" if not issues else "NO CONFORME"))
    for n in notes:
        print("  nota: " + n)
    for i in issues:
        print("  - " + i)
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
