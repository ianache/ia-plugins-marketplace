#!/usr/bin/env python3
"""Valida web-automation-report.yaml (estructura, campos obligatorios y ausencia de secretos).

Uso: python validar_reporte_web.py <reporte.yaml>
Salida: 0 sin hallazgos, 1 con hallazgos, 2 si el archivo no se puede leer.
No valida las aserciones ni el resultado real del pipeline: eso exige revisión humana.
"""
import re
import sys
from pathlib import Path

import yaml

FRAMEWORKS = {"PLAYWRIGHT", "SELENIUM"}
ESTADOS_CASO = {"AUTOMATED", "PARTIAL", "NOT_AUTOMATED"}
ESTADOS_EJECUCION = {"EXECUTED", "NOT_EXECUTED"}
TC_RE = re.compile(r"^TC-[A-Z0-9][A-Z0-9-]*$")
# Contraseñas, tokens o URLs con credenciales escritas literalmente (no variables).
SECRETO_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key)\s*[:=]\s*['\"]?(?![\"']?\$\{|\{\{|<)[^\s'\"#]{4,}",
    re.IGNORECASE,
)
URL_CREDENCIAL_RE = re.compile(r"https?://[^/\s:@]+:[^/\s@]+@")


def validar(texto, datos):
    hallazgos = []
    if not isinstance(datos, dict):
        return ["el reporte no es un mapa YAML"]

    for campo in ("aut", "framework", "casos", "ejecucion"):
        if campo not in datos:
            hallazgos.append(f"falta el campo obligatorio: {campo}")

    if datos.get("framework") not in FRAMEWORKS:
        hallazgos.append(f"framework inválido: {datos.get('framework')!r} (PLAYWRIGHT o SELENIUM)")

    casos = datos.get("casos")
    if not isinstance(casos, list) or not casos:
        hallazgos.append("casos debe ser una lista no vacía")
        casos = []
    vistos = set()
    for i, caso in enumerate(casos):
        if not isinstance(caso, dict):
            hallazgos.append(f"casos[{i}] no es un mapa")
            continue
        cid = caso.get("id")
        if not isinstance(cid, str) or not TC_RE.match(cid):
            hallazgos.append(f"casos[{i}].id no es un TC válido: {cid!r}")
        elif cid in vistos:
            hallazgos.append(f"casos[{i}].id duplicado: {cid}")
        else:
            vistos.add(cid)
        if caso.get("estado") not in ESTADOS_CASO:
            hallazgos.append(f"{cid or f'casos[{i}]'}: estado inválido {caso.get('estado')!r}")

    ejecucion = datos.get("ejecucion")
    if not isinstance(ejecucion, dict):
        hallazgos.append("ejecucion debe ser un mapa")
    else:
        estado = ejecucion.get("estado")
        if estado not in ESTADOS_EJECUCION:
            hallazgos.append(f"ejecucion.estado inválido: {estado!r}")
        elif estado == "EXECUTED":
            if not ejecucion.get("pipeline"):
                hallazgos.append("ejecucion EXECUTED exige pipeline (ID o URL real)")
            if not ejecucion.get("resultados"):
                hallazgos.append("ejecucion EXECUTED exige resultados")
        else:
            if not ejecucion.get("razon"):
                hallazgos.append("ejecucion NOT_EXECUTED exige razon")

    for m in SECRETO_RE.finditer(texto):
        hallazgos.append(f"posible secreto literal: {m.group(1)}=…")
    if URL_CREDENCIAL_RE.search(texto):
        hallazgos.append("URL con credenciales embebidas")
    return hallazgos


def main(argv):
    if len(argv) != 2:
        print("uso: validar_reporte_web.py <reporte.yaml>", file=sys.stderr)
        return 2
    try:
        texto = Path(argv[1]).read_text(encoding="utf8")
        datos = yaml.safe_load(texto)
    except (OSError, yaml.YAMLError) as e:
        print(f"no se puede leer el reporte: {e}", file=sys.stderr)
        return 2
    hallazgos = validar(texto, datos)
    for h in hallazgos:
        print(f"HALLAZGO: {h}")
    if not hallazgos:
        print("OK: reporte válido")
    return 1 if hallazgos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
