#!/usr/bin/env python3
"""Validación estructural de salidas y payloads de ssp-closure.

No verifica semántica, autenticación humana, acceso GitLab ni aprobación de release.
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

PATHMAP = json.loads((Path(__file__).resolve().parents[1] / "assets" / "pathmap.json").read_text(encoding="utf-8-sig"))
APPROVED_DOC_TYPES = set(PATHMAP["approved_types"])
REQUIRED_OKF = {"type", "id", "title", "description", "version", "status", "owner", "classification", "tags", "product", "pack", "skill", "related", "generated", "sources"}
HOURS_PATTERNS = [
    r"\b\d+(?:[.,]\d+)?\s*(?:h|hrs?|hours?|horas?)\b",
    r"\b(?:time_stats|total_time_spent|time_estimate|spend|estimate)\s*[:=]\s*\S+",
]


def frontmatter(text: str) -> tuple[dict, str, list[str]]:
    m = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not m:
        return {}, text, ["Falta frontmatter YAML delimitado por ---."]
    block = m.group(1)
    fields = {}
    for line in block.splitlines():
        match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$", line)
        if match:
            fields[match.group(1)] = match.group(2).strip().strip('"\'')
    errors = []
    return fields, text[m.end():], errors


def check_okf(text: str, expected_type: str) -> list[str]:
    fields, body, errors = frontmatter(text)
    if errors:
        return errors
    missing = sorted(REQUIRED_OKF - fields.keys())
    if missing:
        errors.append("Faltan metadatos requeridos: " + ", ".join(missing))
    actual = fields.get("type", "")
    if actual not in APPROVED_DOC_TYPES or actual != expected_type:
        errors.append(f"type debe ser el tipo aprobado {expected_type}; encontrado '{actual}'.")
    doc_id = fields.get("id", "")
    if not doc_id.startswith(expected_type + "-") or re.search(r"<[^>]+>", doc_id):
        errors.append(f"id debe iniciar con {expected_type}- y no contener placeholders.")
    if not re.fullmatch(r"\d+\.\d+\.\d+", fields.get("version", "")):
        errors.append("version debe ser SemVer.")
    if fields.get("status") not in {"draft", "stable", "deprecated"}:
        errors.append("status debe ser draft, stable o deprecated.")
    if fields.get("classification") not in {"public", "internal", "confidential", "restricted"}:
        errors.append("classification no pertenece al enum STD-OKF.")
    for field in ("title", "description", "owner", "product", "pack", "skill"):
        if not fields.get(field):
            errors.append(f"{field} no puede estar vacío.")
    if fields.get("pack") != "ssp-closure":
        errors.append("pack debe ser ssp-closure.")
    if not re.search(r"(?m)^\s+by:\s*\S+", text.split("---", 2)[1]):
        errors.append("generated.by es obligatorio.")
    at_match = re.search(r"(?m)^\s+at:\s*['\"]?([^'\"\n]+)", text.split("---", 2)[1])
    if not at_match or "<" in at_match.group(1):
        errors.append("generated.at debe ser una fecha ISO-8601 real con zona.")
    else:
        try:
            parsed = datetime.fromisoformat(at_match.group(1).replace("Z", "+00:00"))
            if parsed.tzinfo is None:
                errors.append("generated.at debe incluir zona horaria.")
        except ValueError:
            errors.append("generated.at no es ISO-8601 válido.")
    if re.search(r"(?m)^sources:\s*\[\s*\]\s*$", text.split("---", 2)[1]):
        errors.append("sources vacío requiere justificación; este plugin debe citar las fuentes del SSP.")
    if not re.search(r"(?m)^\s+-\s+resource:\s*\S+", text.split("---", 2)[1]):
        errors.append("sources debe incluir al menos un resource.")
    tags_match = re.search(r"(?m)^tags:\s*\[([^]]*)\]", text.split("---", 2)[1])
    if tags_match:
        tags = [tag.strip().strip("\"'") for tag in tags_match.group(1).split(",") if tag.strip()]
        if len(tags) != len(set(tags)) or any(tag.lower() != tag for tag in tags):
            errors.append("tags debe usar valores minúsculos y no duplicados.")
    if re.search(r"<[^>]+>", text):
        errors.append("El documento contiene placeholders sin completar.")
    if not body.strip():
        errors.append("El cuerpo del documento está vacío.")
    return errors


def check_status_report(text: str) -> list[str]:
    errors = check_okf(text, "STR")
    for pat in HOURS_PATTERNS:
        if re.search(pat, text, flags=re.IGNORECASE):
            errors.append("C6: el informe contiene horas/estimaciones/esfuerzo registrados.")
            break
    if not re.search(r"#\d+", text):
        errors.append("El informe no cita ningún issue de origen (formato '#<iid>').")
    return errors


def check_closure_report(text: str) -> list[str]:
    errors = check_okf(text, "CLS")
    for section in ("Resultado frente al objetivo", "Aceptación y desviaciones", "Lecciones aprendidas", "Transferencia"):
        if section.lower() not in text.lower():
            errors.append(f"CLS: falta la sección '{section}'.")
    return errors


def check_document_path(file_path: str, doc_type: str) -> list[str]:
    expected = tuple(part.lower() for part in Path(PATHMAP["document_types"][doc_type]).parts)
    path = Path(file_path)
    actual_parent = tuple(part.lower() for part in path.parent.parts)
    if len(actual_parent) < len(expected) or actual_parent[-len(expected):] != expected:
        return [f"{doc_type} debe ubicarse bajo {'/'.join(expected)}."]
    doc_id_match = re.search(r"(?m)^id:\s*['\"]?([^'\"\n]+)", path.read_text(encoding="utf-8-sig"))
    if doc_id_match and not path.name.startswith(doc_id_match.group(1) + "."):
        return ["El nombre del archivo debe comenzar con el id OKF."]
    return []


def check_review_agenda(text: str) -> list[str]:
    errors = []
    if not re.search(r"Product Owner", text):
        errors.append("C9: el payload debe indicar que Product Owner registra la aceptación.")
    if re.search(r"(?i)decisi[oó]n\s*:\s*(aceptad[ao]|rechazad[ao])", text):
        errors.append("C9: la decisión de aceptación aparece prellenada.")
    if re.search(r"\b\d+(?:[.,]\d+)?\s*(?:h|hrs?|hours?|horas?)\b", text, re.I):
        errors.append("C6: la agenda contiene una métrica de horas.")
    return errors


def check_retro_agenda(text: str) -> list[str]:
    if not re.search(r"(?i)hip[oó]tesis", text):
        return ["La agenda de retro no separa hipótesis de hechos."]
    return []


def check_experiment(text: str) -> list[str]:
    errors = []
    try:
        data = json.loads(text)
        checks = {"owner_person": data.get("owner_person"), "success_metric": data.get("success_metric"), "due_date": data.get("due_date")}
        for key, value in checks.items():
            if not value or re.search(r"<[^>]+>", str(value)):
                errors.append(f"C5: falta {key} o conserva placeholder.")
        if checks["due_date"]:
            try:
                date.fromisoformat(checks["due_date"])
            except ValueError:
                errors.append("C5: due_date no es una fecha válida (AAAA-MM-DD).")
        return errors
    except json.JSONDecodeError:
        fields = ["Dueño", "Métrica", "Fecha de cierre"]
        for field in fields:
            m = re.search(rf"{field}[ \t]*:[ \t]*([^\n]*)", text, re.I)
            if not m or not m.group(1).strip() or re.search(r"<[^>]+>", m.group(1)):
                errors.append(f"C5: falta el campo obligatorio '{field}'.")
        return errors


CHECKS = {
    "status-report": (check_status_report, "STR"),
    "closure-report": (check_closure_report, "CLS"),
    "review-agenda": (check_review_agenda, None),
    "retro-agenda": (check_retro_agenda, None),
    "experiment": (check_experiment, None),
}


def main(argv: list[str]) -> int:
    if len(argv) != 3 or argv[1] not in CHECKS:
        print("Uso: check_closure.py <status-report|closure-report|review-agenda|retro-agenda|experiment> <archivo>")
        return 2
    try:
        text = Path(argv[2]).read_text(encoding="utf-8-sig")
    except OSError as exc:
        print(f"FAIL\n - No se pudo leer el archivo: {exc}")
        return 1
    errors = CHECKS[argv[1]][0](text)
    doc_type = CHECKS[argv[1]][1]
    if doc_type:
        errors.extend(check_document_path(argv[2], doc_type))
    if errors:
        print("FAIL")
        for error in errors:
            print(" -", error)
        return 1
    print("PASS (checks estructurales; no es aprobación humana)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
