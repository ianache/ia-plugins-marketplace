import copy
import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validar", ROOT / "scripts" / "validar_coleccion.py")
validar_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validar_mod)
validar = validar_mod.validar

DOC_OK = (
    "**Objetivo:** verificar X.\n\n**Caso:** TC-PE-01 - Caso\n\n"
    "**Criterios de aceptación:**\n\n#### HU-05-04 AC-1 — Título\n\n```gherkin\nDado X\n```"
)


def request(nombre="Consulta válida", doc=DOC_OK, url="{{baseUrl}}/svc/x"):
    return {"name": nombre, "request": {"method": "GET", "url": url, "description": doc}}


def coleccion_valida():
    return {
        "info": {"name": "svc", "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
        "variable": [{"key": "baseUrl", "value": "http://localhost:8080"}, {"key": "tokenAuditQuery", "value": ""}],
        "item": [
            {
                "name": "RF01-Consultar eventos",
                "description": "GET /svc/x. Rol AUDIT_QUERY.",
                "item": [
                    {
                        "name": "TC-PE-01 - Consulta válida devuelve una página",
                        "description": "Cubre HU-05-04 AC-1.",
                        "item": [request()],
                    }
                ],
            }
        ],
    }


def reglas(col):
    return {r for r, _, _ in validar(col)}


def test_coleccion_valida_sin_hallazgos():
    assert validar(coleccion_valida()) == []


def test_funcionalidad_sin_prefijo_rf_se_rechaza():
    col = coleccion_valida()
    col["item"][0]["name"] = "Consultar eventos"
    assert "E2" in reglas(col)


def test_caso_con_ac_en_el_titulo_se_rechaza():
    col = coleccion_valida()
    col["item"][0]["item"][0]["name"] = "HU-05-04 AC-1 - Consulta válida"
    msgs = [m for _, _, m in validar(col)]
    assert any("AC-" in m for m in msgs)


def test_caso_sin_descripcion_de_trazabilidad_se_rechaza():
    col = coleccion_valida()
    col["item"][0]["item"][0]["description"] = ""
    assert "E2" in reglas(col)


def test_request_sin_objetivo_se_rechaza():
    col = coleccion_valida()
    col["item"][0]["item"][0]["item"][0]["request"]["description"] = "**Caso:** x\n**Criterios de aceptación:** y"
    msgs = [m for r, _, m in validar(col) if r == "E3"]
    assert any("**Objetivo:**" in m for m in msgs)


def test_documentacion_en_item_y_no_en_request_se_rechaza():
    col = coleccion_valida()
    req = col["item"][0]["item"][0]["item"][0]
    req["description"] = req["request"].pop("description")
    assert "E3" in reglas(col)


def test_jwt_literal_se_rechaza():
    col = coleccion_valida()
    col["item"][0]["item"][0]["item"][0]["request"]["header"] = [
        {"key": "Authorization", "value": "Bearer eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abcdefghijklmnop"}
    ]
    assert "E4" in reglas(col)


def test_bearer_con_variable_es_valido():
    col = coleccion_valida()
    col["item"][0]["item"][0]["item"][0]["request"]["header"] = [
        {"key": "Authorization", "value": "Bearer {{tokenAuditQuery}}"}
    ]
    assert "E4" not in reglas(col)


def test_falta_basurl_se_rechaza():
    col = coleccion_valida()
    col["variable"] = [v for v in col["variable"] if v["key"] != "baseUrl"]
    assert "E2" in reglas(col)


def test_url_sin_basurl_se_rechaza():
    col = coleccion_valida()
    col["item"][0]["item"][0]["item"][0]["request"]["url"] = "http://localhost:8080/svc/x"
    assert "E2" in reglas(col)


def test_carpeta_de_tercer_nivel_se_rechaza():
    col = copy.deepcopy(coleccion_valida())
    col["item"][0]["item"][0]["item"].append({"name": "sub", "item": [request()]})
    assert "E2" in reglas(col)


def _ejecutar(ruta):
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "validar_coleccion.py"), str(ruta)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


def test_cli_devuelve_0_sin_hallazgos():
    with tempfile.TemporaryDirectory() as d:
        ruta = pathlib.Path(d) / "postman.json"
        ruta.write_text(json.dumps(coleccion_valida(), ensure_ascii=False), encoding="utf-8")
        assert _ejecutar(ruta).returncode == 0


def test_cli_devuelve_1_con_hallazgos():
    col = coleccion_valida()
    col["item"][0]["name"] = "sin prefijo"
    with tempfile.TemporaryDirectory() as d:
        ruta = pathlib.Path(d) / "postman.json"
        ruta.write_text(json.dumps(col, ensure_ascii=False), encoding="utf-8")
        assert _ejecutar(ruta).returncode == 1


def test_cli_devuelve_2_si_el_json_no_es_valido():
    with tempfile.TemporaryDirectory() as d:
        ruta = pathlib.Path(d) / "postman.json"
        ruta.write_text("{no es json", encoding="utf-8")
        assert _ejecutar(ruta).returncode == 2
