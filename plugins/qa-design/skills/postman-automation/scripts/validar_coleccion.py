#!/usr/bin/env python3
"""Valida la estructura y la documentación de una colección Postman v2.1.

Comprueba (ver references/estructura-coleccion.md):
  E2  Estructura: RF##-<nombre> en el primer nivel; <ID> - <Nombre> en el segundo;
      sin AC- en títulos de caso; sin carpetas de tercer nivel.
  E3  Documentación: cada request con **Caso:**, **Objetivo:** y **Criterios de aceptación:**.
  E4  Sin secretos: ningún JWT ni Bearer literal.
  Extra: variable baseUrl declarada; URLs de request basadas en {{baseUrl}}.

No verifica que los criterios coincidan con la historia ni que las aserciones sean correctas.

Uso:  python validar_coleccion.py <postman.json>
Salida: 0 sin hallazgos, 1 con hallazgos, 2 archivo ilegible o JSON inválido.
"""
import json
import re
import sys

RE_FUNCIONALIDAD = re.compile(r"^RF\d{2}-.+$")
RE_CASO = re.compile(r"^TC-[A-Z0-9-]+ - .+$")
RE_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")
RE_BEARER_LITERAL = re.compile(r"Bearer\s+(?!\{\{)[A-Za-z0-9._~+/=-]{12,}")
DOC_OBLIGATORIA = ["**Caso:**", "**Objetivo:**", "**Criterios de aceptación:**"]


def _es_carpeta(item):
    return isinstance(item, dict) and isinstance(item.get("item"), list)


def _es_request(item):
    return isinstance(item, dict) and "request" in item and not _es_carpeta(item)


def _url_texto(request):
    url = request.get("url")
    if isinstance(url, str):
        return url
    if isinstance(url, dict):
        return url.get("raw", "")
    return ""


def validar(coleccion):
    """Devuelve una lista de hallazgos (regla, ruta, mensaje)."""
    hallazgos = []

    def add(regla, ruta, mensaje):
        hallazgos.append((regla, ruta, mensaje))

    variables = {v.get("key") for v in coleccion.get("variable", []) if isinstance(v, dict)}
    if "baseUrl" not in variables:
        add("E2", "variable", "falta la variable de colección baseUrl")

    for i, f in enumerate(coleccion.get("item", [])):
        ruta_f = f"item[{i}]"
        nombre_f = f.get("name", "") if isinstance(f, dict) else ""
        if not _es_carpeta(f):
            add("E2", ruta_f, f"el primer nivel debe ser una funcionalidad (carpeta), no un request: '{nombre_f}'")
            continue
        if not RE_FUNCIONALIDAD.match(nombre_f):
            add("E2", ruta_f, f"la funcionalidad debe llamarse RF##-<nombre>: '{nombre_f}'")
        if not (f.get("description") or "").strip():
            add("E2", ruta_f, f"la funcionalidad '{nombre_f}' no tiene descripción (método, ruta y rol)")

        for j, c in enumerate(f["item"]):
            ruta_c = f"{ruta_f}.item[{j}]"
            nombre_c = c.get("name", "") if isinstance(c, dict) else ""
            if not _es_carpeta(c):
                add("E2", ruta_c, f"el segundo nivel debe ser un caso de prueba (carpeta): '{nombre_c}'")
                continue
            if not RE_CASO.match(nombre_c):
                add("E2", ruta_c, f"el caso debe llamarse '<ID> - <Nombre>': '{nombre_c}'")
            if "AC-" in nombre_c:
                add("E2", ruta_c, f"el título del caso no debe contener AC-; va en la descripción: '{nombre_c}'")
            desc_c = (c.get("description") or "").strip()
            if not desc_c:
                add("E2", ruta_c, f"el caso '{nombre_c}' no tiene descripción de trazabilidad")
            elif "Cubre" not in desc_c and "Sin criterio" not in desc_c:
                add("E2", ruta_c, f"la descripción del caso '{nombre_c}' no declara Cubre ni Sin criterio")

            for k, r in enumerate(c["item"]):
                ruta_r = f"{ruta_c}.item[{k}]"
                nombre_r = r.get("name", "") if isinstance(r, dict) else ""
                if _es_carpeta(r):
                    add("E2", ruta_r, f"no se permiten carpetas de tercer nivel: '{nombre_r}'")
                    continue
                if not _es_request(r):
                    add("E2", ruta_r, f"elemento sin request: '{nombre_r}'")
                    continue
                req = r["request"]
                doc = req.get("description") or ""
                for etiqueta in DOC_OBLIGATORIA:
                    if etiqueta not in doc:
                        add("E3", ruta_r, f"el request '{nombre_r}' no tiene {etiqueta} en su documentación")
                url = _url_texto(req)
                if url and "{{baseUrl}}" not in url:
                    add("E2", ruta_r, f"la URL de '{nombre_r}' no usa {{{{baseUrl}}}}")

    texto = json.dumps(coleccion, ensure_ascii=False)
    if RE_JWT.search(texto):
        add("E4", "*", "se encontró un JWT literal; use una variable de entorno")
    for m in RE_BEARER_LITERAL.finditer(texto):
        add("E4", "*", f"se encontró un 'Bearer' con valor literal: '{m.group(0)[:20]}...'")
    return hallazgos


def main(argv):
    if len(argv) != 2:
        print("uso: validar_coleccion.py <postman.json>", file=sys.stderr)
        return 2
    try:
        with open(argv[1], encoding="utf-8") as fh:
            coleccion = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: no se puede leer la colección: {exc}", file=sys.stderr)
        return 2
    hallazgos = validar(coleccion)
    for regla, ruta, mensaje in hallazgos:
        print(f"[{regla}] {ruta}: {mensaje}")
    print(f"{len(hallazgos)} hallazgo(s)")
    return 1 if hallazgos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
