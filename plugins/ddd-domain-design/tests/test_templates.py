"""Verifica que cada plantilla vive en la carpeta templates/ del skill que la produce y cumple STD-OKF-001 v1.9.0."""
import pathlib
import re

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REQUIRED = {"type", "id", "title", "description", "version", "status", "owner",
            "classification", "tags", "generated", "sources"}
FORBIDDEN_ALIASES = {"artifact_type", "source_refs", "reviewed_by", "lifecycle_status"}

# Plantillas OKF tipadas por skill productor: nombre -> (type, indexes)
OKF_TEMPLATES = {
    "ddd-domain-discovery": {"domain-discovery-acp.md": ("ACP", None)},
    "ddd-bounded-context-designer": {"bounded-context-okf.md": ("BC", None),
                                     "ctlg-bc-okf.md": ("CTLG", "BC")},
    "ddd-context-map-designer": {"context-map-okf.md": ("CTX", None)},
    "ddd-tactical-model-designer": {"ctlg-agg-okf.md": ("CTLG", "AGG"),
                                    "agg-okf.md": ("AGG", None),
                                    "vo-okf.md": ("VO", None)},
    "ddd-domain-event-designer": {"ctlg-evt-okf.md": ("CTLG", "EVT"),
                                  "evt-okf.md": ("EVT", None)},
    "ddd-domain-contract-validator": {"cfr-okf.md": ("CFR", None)},
}
# Plantillas YAML operativas (no OKF) por skill productor
YAML_TEMPLATES = {
    "ddd-domain-contract-validator": ["domain-design-contract.yaml"],
    "ddd-design-orchestrator": ["execution-plan.yaml", "gate-register.yaml", "task-ledger.yaml", "task-result.yaml"],
}
TASK_RESULT = "task-result.yaml"


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path.name}: sin frontmatter YAML"
    return yaml.safe_load(match.group(1)), text


def _template(skill, name):
    return SKILLS / skill / "templates" / name


ORCHESTRATOR = "ddd-design-orchestrator"


def test_okf_templates_have_expected_type_and_profile():
    for skill, templates in OKF_TEMPLATES.items():
        for name, (doc_type, indexes) in templates.items():
            path = _template(skill, name)
            assert path.is_file(), f"{skill}: falta templates/{name}"
            data, _ = _frontmatter(path)
            assert data["type"] == doc_type, f"{skill}/{name}"
            assert data.get("indexes") == indexes, f"{skill}/{name}"
            assert data["skill"] == skill, f"{skill}/{name}"
            assert data["pack"] == "ddd-domain-design", f"{skill}/{name}"
            assert REQUIRED <= set(data), f"{skill}/{name}: faltan campos {REQUIRED - set(data)}"
            assert not (FORBIDDEN_ALIASES & set(data)), f"{skill}/{name}"
            assert data["generated"]["by"].startswith(f"{skill}/"), f"{skill}/{name}"


def test_yaml_templates_live_in_producing_skill():
    for skill, names in YAML_TEMPLATES.items():
        for name in names:
            assert _template(skill, name).is_file(), f"{skill}: falta templates/{name}"


def test_no_plugin_root_templates():
    assert not (ROOT / "templates").exists(), "los registros operativos viven en la carpeta del orquestador; la raíz no tiene templates/"


def test_operational_records_live_in_orchestrator_folder():
    for name in YAML_TEMPLATES[ORCHESTRATOR]:
        assert _template(ORCHESTRATOR, name).is_file(), f"falta {ORCHESTRATOR}/templates/{name}"
        for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir() and p.name != ORCHESTRATOR):
            assert not (skill_dir / "templates" / name).exists(), f"{skill_dir.name}: {name} es registro operativo del orquestador"


def test_skills_reference_their_templates_in_own_folder():
    for skill, templates in {**{k: list(v) for k, v in OKF_TEMPLATES.items()}, **YAML_TEMPLATES}.items():
        text = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
        assert f"skills/{skill}/templates/" in text, f"{skill}: no indica su carpeta de plantillas"
        for name in templates:
            assert f"templates/{name}" in text, f"{skill}: no referencia templates/{name}"
        assert "auxiliar sin tipo" not in text, f"{skill}: queda referencia a plantilla auxiliar"
        assert "copia idéntica" not in text, f"{skill}: queda referencia a copia en la raíz"


def test_event_template_covers_skill_objectives():
    _, text = _frontmatter(_template("ddd-domain-event-designer", "evt-okf.md"))
    for section in ["## Clasificación del evento", "## Ownership", "## Semántica y versionado",
                    "## Payload", "## Consumidores conocidos", "## Preguntas abiertas", "## Trazabilidad"]:
        assert section in text, f"evt-okf.md: falta sección {section}"
