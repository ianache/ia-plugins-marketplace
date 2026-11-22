#!/usr/bin/env python3
"""Valida una suite Grafana k6 (carpeta test/load) según references/estructura-k6.md.

Checks:
  L1 Estructura: k6.js, scenarios/TC-*.js, lib/config.js.
  L2 Imports: solo k6, k6/*, rutas relativas existentes o https://jslib.k6.io/.
  L3 Cableado: cada escenario de options tiene exec exportado por k6.js, y cada módulo
     de scenarios/ está re-exportado desde k6.js.
  L4 Criterio: primera línea '// criterio: BASELINE' o 'APROBADO <DATA-xx|NFR-xx>';
     BASELINE sin umbrales; APROBADO con '// umbral-fuente:' antes de cada umbral.
  L5 Sin secretos: sin URLs, Bearer, JWT ni contraseñas literales en el código.
  L6 Datos: cada open('...') apunta a un archivo existente.
  Extra: si k6 está en PATH, 'k6 inspect' (no ejecuta carga). Si no, se informa L7 NOT_EXECUTED.

No verifica que el perfil de carga sea el aprobado ni que la carga sea representativa.

Uso:  python validar_k6.py <ruta/a/test/load>
Salida: 0 sin hallazgos, 1 con hallazgos, 2 directorio ilegible.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

RE_TC_FILE = re.compile(r"^TC-[A-Z0-9-]+\.js$")
RE_TC_KEY = re.compile(r"^TC-[A-Z0-9-]+$")
RE_CRITERIO = re.compile(r"^// criterio: (BASELINE|APROBADO (DATA-\d+|NFR-[\w-]+)(\s.*)?)$")
RE_IMPORT = re.compile(r"""(?:import|export)\s+[^'";]*?\s+from\s+['"]([^'"]+)['"]|import\s+['"]([^'"]+)['"]""")
RE_OPEN = re.compile(r"""open\(\s*['"]([^'"]+)['"]""")
RE_URL = re.compile(r"https?://")
RE_BEARER = re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]{8,}")
RE_JWT = re.compile(r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")
RE_SECRET = re.compile(r"""(password|passwd|secret|token|apikey)\s*[:=]\s*['"][^'"]+['"]""", re.I)


def sin_comentarios(texto):
    texto = re.sub(r"/\*.*?\*/", "", texto, flags=re.S)
    return "\n".join(re.sub(r"(?<![:'\"])//.*$", "", linea) for linea in texto.splitlines())


def js_files(base):
    return sorted(p for p in base.rglob("*.js") if "node_modules" not in p.parts)


def exports_de(texto):
    nombres = set(re.findall(r"export\s+(?:async\s+)?function\s+(\w+)", texto))
    nombres |= set(re.findall(r"export\s+const\s+(\w+)", texto))
    for bloque in re.findall(r"export\s*\{([^}]*)\}\s*from", texto):
        for parte in bloque.split(","):
            parte = parte.strip()
            if not parte:
                continue
            nombres.add(parte.split(" as ")[-1].strip())
    return nombres


def bloque_thresholds(lineas):
    """Devuelve índices de líneas de umbrales (no comentadas) dentro de 'thresholds: {'."""
    idx, dentro, prof = [], False, 0
    for i, linea in enumerate(lineas):
        if linea.lstrip().startswith("//"):
            continue
        if not dentro:
            m = re.search(r"\bthresholds\s*:\s*\{", linea)
            if not m:
                continue
            resto = linea[m.start():]
            prof = resto.count("{") - resto.count("}")
            dentro = prof > 0
            if re.search(r":\s*\[", linea[m.end():]):  # forma de una sola línea
                idx.append(i)
            continue
        prof += linea.count("{") - linea.count("}")
        if re.search(r":\s*\[", linea):
            idx.append(i)
        if prof <= 0:
            dentro = False
    return idx


def validar(base):
    hallazgos = []

    def add(regla, ruta, mensaje):
        hallazgos.append((regla, ruta, mensaje))

    k6 = base / "k6.js"
    if not k6.is_file():
        add("L1", "k6.js", "falta el archivo principal k6.js")
        return hallazgos
    if not (base / "lib" / "config.js").is_file():
        add("L1", "lib/config.js", "falta lib/config.js (variables de entorno)")
    escenarios = base / "scenarios"
    modulos = sorted(escenarios.glob("*.js")) if escenarios.is_dir() else []
    if not modulos:
        add("L1", "scenarios/", "no hay módulos de escenario (scenarios/TC-*.js)")
    for m in modulos:
        if not RE_TC_FILE.match(m.name):
            add("L1", f"scenarios/{m.name}", "el módulo debe llamarse TC-<ID>.js")

    texto_k6 = k6.read_text(encoding="utf8")
    lineas = texto_k6.splitlines()

    # L4 criterio
    primera = next((l for l in lineas if l.strip()), "")
    if not RE_CRITERIO.match(primera.strip()):
        add("L4", "k6.js", "la primera línea debe ser '// criterio: BASELINE' o '// criterio: APROBADO <DATA-xx|NFR-xx>'")
    criterio_baseline = primera.strip().startswith("// criterio: BASELINE")
    umbrales = bloque_thresholds(lineas)
    if criterio_baseline and umbrales:
        add("L4", "k6.js", "criterio BASELINE con umbrales: quitar los umbrales o cambiar a APROBADO con fuente")
    if not criterio_baseline:
        for i in umbrales:
            previa = next((lineas[j] for j in range(i - 1, -1, -1) if lineas[j].strip()), "")
            if "umbral-fuente:" not in previa:
                add("L4", f"k6.js:{i + 1}", "umbral sin '// umbral-fuente: <DATA-xx|NFR-xx>' en la línea anterior")

    # L2 imports, L5 secretos, L6 datos (todos los .js del directorio)
    for f in js_files(base):
        rel = f.relative_to(base).as_posix()
        codigo = sin_comentarios(f.read_text(encoding="utf8"))
        for m in RE_IMPORT.finditer(codigo):
            spec = m.group(1) or m.group(2)
            if spec.startswith("k6") or spec.startswith("https://jslib.k6.io/"):
                continue
            if spec.startswith("./") or spec.startswith("../"):
                if not (f.parent / spec).resolve().is_file():
                    add("L2", rel, f"import relativo inexistente: {spec}")
                continue
            add("L2", rel, f"import no permitido en k6: {spec}")
        for m in RE_OPEN.finditer(codigo):
            if not (f.parent / m.group(1)).resolve().is_file():
                add("L6", rel, f"open() apunta a un archivo inexistente: {m.group(1)}")
        if RE_URL.search(codigo.replace("https://jslib.k6.io/", "")):
            add("L5", rel, "URL literal en el código: construirla con lib/config.js")
        if RE_BEARER.search(codigo) or RE_JWT.search(codigo):
            add("L5", rel, "token literal en el código: usar variable de entorno")
        for m in RE_SECRET.finditer(codigo):
            if "__ENV" not in m.group(0):
                add("L5", rel, f"valor literal para '{m.group(1)}': usar variable de entorno")

    # L3 cableado
    exportados = exports_de(texto_k6)
    for m in re.finditer(r"exec\s*:\s*['\"](\w+)['\"]", sin_comentarios(texto_k6)):
        if m.group(1) not in exportados:
            add("L3", "k6.js", f"exec '{m.group(1)}' no está exportado por k6.js")
    claves = re.findall(r"^\s*['\"]?(TC-[A-Z0-9-]+)['\"]?\s*:\s*\{", sin_comentarios(texto_k6), re.M)
    for clave in claves:
        if not RE_TC_KEY.match(clave):
            add("L3", "k6.js", f"escenario '{clave}' no sigue TC-<ID>")
    for m in modulos:
        if f"scenarios/{m.name}" not in texto_k6:
            add("L3", f"scenarios/{m.name}", "módulo no re-exportado desde k6.js")
    return hallazgos


def inspeccionar(base):
    """L7 informativo: 'k6 inspect' solo si k6 está en PATH; nunca ejecuta carga."""
    if not shutil.which("k6"):
        return "L7 NOT_EXECUTED: k6 no está en PATH; sin 'k6 inspect'"
    r = subprocess.run(["k6", "inspect", str(base / "k6.js")], capture_output=True, text=True, timeout=60)
    return "L7 inspect OK" if r.returncode == 0 else f"L7 inspect FALLÓ: {r.stderr.strip()[:200]}"


def main(argv):
    # Salida UTF-8 fija: los mensajes llevan acentos y la consola de Windows usa cp1252 por defecto.
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    if len(argv) != 2:
        print("uso: validar_k6.py <ruta/a/test/load>", file=sys.stderr)
        return 2
    base = Path(argv[1])
    if not base.is_dir():
        print(f"ERROR: no existe el directorio {base}", file=sys.stderr)
        return 2
    hallazgos = validar(base)
    for regla, ruta, mensaje in hallazgos:
        print(f"[{regla}] {ruta}: {mensaje}")
    print(f"{len(hallazgos)} hallazgo(s)")
    print(inspeccionar(base))
    return 1 if hallazgos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
