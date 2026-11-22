import json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
PM = json.loads((ROOT / "assets" / "pathmap.json").read_text(encoding="utf-8"))
TEMPLATES = PM["templates"]

# Secciones obligatorias por tipo markdown (contrato de cada plantilla).
SECTIONS = {
    "templates/service-architecture.md": ["## 1. Núcleo", "## 2. Adaptadores", "## 3. Dependencias externas", "## 4. Vista C4", "## 5. NFR", "## 6. Trazabilidad"],
    "ASIS": ["## 1. Alcance", "## 2. Evidencia", "## 3. Componentes", "## 4. Dependencias", "## 5. Hechos", "## 6. Inferencias", "## 7. Incertidumbres"],
    "templates/service-boundaries.md": ["## 1. Responsabilidades", "## 2. Límites", "## 3. Ownership", "## 4. Dependencias", "## 5. Trazabilidad", "## 6. NFR"],
    "API": ["## 1. Propósito", "## 2. Operaciones", "## 3. Modelo de errores", "## 4. Seguridad", "## 5. Versionado", "## 6. Consumidores", "## 7. Contrato OpenAPI", "## 8. Trazabilidad", "## 9. Preguntas"],
    "EVT": ["## 1. Propósito", "## 2. Eventos", "## 3. Esquema", "## 4. Entrega", "## 5. Versionado", "## 6. Errores", "## 7. Trazabilidad", "## 8. Preguntas"],
    "IMP": ["## 1. Cambios", "## 2. Compatibilidad", "## 3. Consumidores", "## 4. Migración", "## 5. Rollout", "## 6. Rollback", "## 7. Riesgos"],
    "C4": ["## 1. Contexto", "## 2. Contenedores", "## 3. Componentes", "## 4. Código", "## 5. Escenarios", "## 6. Fuentes"],
}


def _declared_type(path):
    text = path.read_text(encoding="utf-8")
    m = re.search(r"(?m)^(?:# )?type:\s*([A-Z0-9]+)\s*$", text)
    return m.group(1) if m else None


def test_every_output_type_has_a_contract_template():
    for doc_type in PM["document_types"]:
        assert doc_type in TEMPLATES, f"sin plantilla para {doc_type}"
        for rel in TEMPLATES[doc_type]:
            assert (ROOT / rel).is_file(), rel


def test_template_declares_the_same_type_it_serves():
    for doc_type, files in TEMPLATES.items():
        for rel in files:
            declared = _declared_type(ROOT / rel)
            if declared is None and rel.endswith("manifest.yaml"):
                continue  # manifiestos operativos de FDT: no llevan campo type
            assert declared == doc_type, (rel, declared, doc_type)


def test_markdown_templates_define_required_sections_and_placeholders():
    for key, required in SECTIONS.items():
        rels = [key] if key.startswith("templates/") else TEMPLATES[key]
        for rel in rels:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for sec in required:
                assert sec in text, (rel, sec)
            assert "<<" in text and "Reglas de validación" in text, rel


def test_new_templates_contain_no_real_service_data():
    for doc_type, files in TEMPLATES.items():
        for rel in files:
            if rel.endswith("fdt-functionality.md") or rel.endswith("fdt-manifest.yaml"):
                continue
            text = (ROOT / rel).read_text(encoding="utf-8")
            assert "ms-distribuidores" not in text and "REPLACE_WITH" not in text, rel


def test_api_skill_uses_the_pathmap_location_for_the_design():
    skill = (ROOT / "skills" / "api-integration-contract-designer" / "SKILL.md").read_text(encoding="utf-8")
    assert "to-be/api-integration-design.md" in skill
    assert "design/microservices/<servicio>/api-integration-design.md" not in skill


def test_no_comsatel_folder_reference_without_dot():
    bad = []
    for f in ROOT.rglob("*"):
        if f.is_file() and f.suffix in (".md", ".py", ".json", ".yaml", ".html") and "__pycache__" not in f.parts and "tests" not in f.parts:
            for line in f.read_text(encoding="utf-8").splitlines():
                if re.search(r"(?<![\w./\-])comsatel/", line):
                    bad.append(f"{f.name}: {line[:80]}")
    assert not bad, bad
