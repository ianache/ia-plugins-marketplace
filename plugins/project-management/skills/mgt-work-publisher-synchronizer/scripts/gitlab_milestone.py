#!/usr/bin/env python3
"""Crea o actualiza en GitLab el Milestone de un Sprint Scope Pack (SSP), de forma idempotente y con aprobación humana.

    python gitlab_milestone.py <SSP.md> --project-id 605 [--mode dry-run|create|update|sync]
        [--start-date AAAA-MM-DD] [--due-date AAAA-MM-DD] [--approved-by human:<nombre>]
    (milestone de grupo: --group-id <id> en lugar de --project-id)

- Los valores salen de la sección «Descripción del Milestone» del SSP (si contiene un bloque de código, solo el primero), que trae la cabecera
  `/project`, `/subproject`, `/cost`, `/time`, `/client`, `/group`, `/cost_agent`, `/time_agent` (y `/project_end` opcional; `/cost` y `/time`
  son del humano, `/cost_agent` y `/time_agent` del agente de IA). La descripción publicada se renderiza con
  `templates/milestone-description.md` y contiene solo esos comandos: el texto que el SSP escriba después (Sprint Goal, historias, enlaces)
  no se envía. El título del Milestone es el valor de `/subproject`. Los valores que nadie informó se escriben `PENDIENTE` y se listan
  en `pending_header_values`; `/subproject` no puede estar pendiente. Los comandos son texto: GitLab no los ejecuta.
- Las fechas solo se envían si se pasan por argumento: nunca se infieren ni se inventan.
- `dry-run` (por defecto) no escribe y no exige credenciales; con `GITLAB_PAT` consulta si el Milestone ya existe.
- `create` crea si no existe (si existe, no lo duplica ni lo modifica); `update` modifica uno existente (falla si no existe);
  `sync` crea si falta o actualiza si difiere. Los modos que escriben exigen `--approved-by human:<nombre>` y `GITLAB_PAT`.
- Nunca cierra ni elimina un Milestone: cerrarlo es una decisión humana fuera de este script.
- La credencial solo se lee de `GITLAB_PAT` (cabecera `PRIVATE-TOKEN`); se redacta en cualquier error. URL base:
  `GITLAB_URL` o https://project.comsatel.com.pe; CA interna opcional en `GITLAB_CA_BUNDLE`.
Salida: JSON con la acción, el Milestone resultante y la fila para el «Sprint GitLab Control Pack» del SSP.
Solo biblioteca estándar. Código de salida 2 ante errores de validación o de GitLab.
"""
import argparse
import datetime
import json
import os
import pathlib
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_URL = "https://project.comsatel.com.pe"
PLACEHOLDER = re.compile(r"<[^<>\n]+>")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
SECTION = "Descripción del Milestone"
HEADER = ["project", "subproject", "cost", "time", "client", "group", "cost_agent", "time_agent"]
OPTIONAL_HEADER = ["project_end"]
CMD = re.compile(r"^/(\w+)(?:[ \t]+(.*?))?[ \t]*$")
LIVE = {"create", "update", "sync"}
TEMPLATE = pathlib.Path(__file__).resolve().parent.parent / "templates" / "milestone-description.md"
TEMPLATE_FIELD = re.compile(r"\{\{(\w+)\}\}")


def render_description(header):
    """Descripción del Milestone desde `templates/milestone-description.md`: solo los comandos, sin texto libre."""
    text = re.sub(r"<!--.*?-->", "", TEMPLATE.read_text(encoding="utf-8"), flags=re.S).strip()
    values = dict(header)
    values["project_end_line"] = f"/project_end {header['project_end']}" if header.get("project_end") else ""
    missing = sorted(set(TEMPLATE_FIELD.findall(text)) - set(values))
    if missing:
        raise MilestoneError("la plantilla del Milestone necesita valores para: " + ", ".join(missing))
    lines = [TEMPLATE_FIELD.sub(lambda m: values[m.group(1)], line).rstrip() for line in text.splitlines()]
    return chr(10).join(line for line in lines if line)


class MilestoneError(RuntimeError):
    pass


def redact(text, secret):
    if secret:
        text = text.replace(secret, "[REDACTED]")
    return text.replace("PRIVATE-TOKEN", "[REDACTED-HEADER]")


def parse_header(description):
    """Valida la cabecera de comandos y el cuerpo; devuelve ({comando: valor}, [comandos pendientes])."""
    lines = description.splitlines()
    header, i = {}, 0
    while i < len(lines) and lines[i].strip():  # la cabecera termina en la primera línea en blanco; lo que siga no se publica
        m = CMD.match(lines[i].strip())
        if not m:
            raise MilestoneError(f"la línea {i + 1} de la cabecera no tiene la forma '/comando valor': {lines[i]!r}")
        header[m.group(1)] = (m.group(2) or "").strip()
        i += 1
    names = list(header)
    expected = HEADER + [n for n in OPTIONAL_HEADER if n in header]
    if names != expected:
        raise MilestoneError("la cabecera debe tener, en este orden, " + ", ".join("/" + n for n in HEADER)
                             + " (y /project_end opcional al final); se encontró: " + (", ".join("/" + n for n in names) or "ninguna"))
    end = header.get("project_end", "")
    if end and end.upper() != "PENDIENTE" and not DATE.fullmatch(end):
        raise MilestoneError("/project_end debe ser AAAA-MM-DD o PENDIENTE")
    if not header["subproject"] or header["subproject"].upper() == "PENDIENTE":
        raise MilestoneError("/subproject es el título del Milestone y no puede estar vacío ni PENDIENTE")
    pending = [n for n, v in header.items() if not v or "PENDIENTE" in v.upper()]
    return header, pending


def read_ssp(path):
    text = pathlib.Path(path).read_text(encoding="utf-8")
    front = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    if not front or not re.search(r"(?m)^type:\s*['\"]?SSP['\"]?\s*$", front.group(1)):
        raise MilestoneError("el documento no es un SSP (frontmatter con type: SSP)")
    body = text[front.end():]
    sec = re.search(r"(?ms)^## " + re.escape(SECTION) + r"\s*\n(.*?)(?=^#{1,2} |\Z)", body)
    if not sec or not sec.group(1).strip():
        raise MilestoneError(f"el SSP no tiene la sección '## {SECTION}' con contenido")
    description = sec.group(1).strip()
    fenced = re.search(r"(?ms)^```[\w-]*[ \t]*\n(.*?)^```[ \t]*$", description)
    if fenced:  # la sección puede explicar el formato en prosa; lo publicado es el primer bloque de código
        description = fenced.group(1).strip()
    found = PLACEHOLDER.search(description)
    if found:
        raise MilestoneError(f"la descripción del Milestone conserva texto de plantilla ({found.group(0)}); complétela o escriba PENDIENTE")
    header, pending = parse_header(description)
    return header["subproject"], render_description(header), header, pending


class GitLab:
    def __init__(self, base_url, pat, ca_bundle=None, timeout=30, opener=None):
        self.base, self.pat, self.timeout = base_url.rstrip("/"), pat, timeout
        self.ctx = ssl.create_default_context(cafile=ca_bundle) if ca_bundle else None
        self.opener = opener  # inyectable en pruebas: opener(method, url, payload) -> (status, json)

    def call(self, method, path, payload=None):
        url = f"{self.base}/api/v4{path}"
        if self.opener:
            status, data = self.opener(method, url, payload)
            if status >= 400:
                raise MilestoneError(redact(f"GitLab HTTP {status}: {data}", self.pat))
            return data
        req = urllib.request.Request(url, method=method, data=json.dumps(payload).encode() if payload is not None else None,
                                     headers={"PRIVATE-TOKEN": self.pat or "", "Content-Type": "application/json", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout, context=self.ctx) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as ex:
            raise MilestoneError(redact(f"GitLab HTTP {ex.code}: {ex.read().decode('utf-8', 'replace')[:400]}", self.pat)) from ex
        except urllib.error.URLError as ex:
            raise MilestoneError(redact(f"error de red: {ex.reason}", self.pat)) from ex


def base_path(a):
    return f"/projects/{a.project_id}/milestones" if a.project_id else f"/groups/{a.group_id}/milestones"


def find(client, a, title):
    q = urllib.parse.urlencode({"title": title, "include_parent_milestones": "false", "per_page": 100})
    hits = client.call("GET", f"{base_path(a)}?{q}")
    exact = [m for m in hits if m.get("title") == title]
    if len(exact) > 1:
        raise MilestoneError(f"hay {len(exact)} Milestones con el título exacto '{title}'; resolver a mano antes de continuar")
    return exact[0] if exact else None


def desired_fields(title, description, a):
    fields = {"title": title, "description": description}
    if a.start_date:
        fields["start_date"] = a.start_date
    if a.due_date:
        fields["due_date"] = a.due_date
    return fields


def norm(value):
    return (value or "").replace("\r\n", "\n").strip() or None


def diff(existing, wanted):
    return {k: {"actual": existing.get(k), "nuevo": v} for k, v in wanted.items() if norm(existing.get(k)) != norm(v)}


def brief(m):
    return {k: m.get(k) for k in ("id", "iid", "title", "state", "start_date", "due_date", "web_url")}


def control_row(action, where, milestone, approved_by, executed):
    ref = f"{milestone.get('title')} (id {milestone.get('id')}, iid {milestone.get('iid')}) {milestone.get('web_url', '')}".strip()
    return f"| M-1 | {action} Milestone en {where}: {ref} | {approved_by or 'sin aprobar (dry-run)'} | {'ejecutada' if executed else 'no ejecutada'} |"


def run(a, opener=None):
    for name in ("start_date", "due_date"):
        v = getattr(a, name)
        if v:
            if not DATE.fullmatch(v):
                raise MilestoneError(f"--{name.replace('_', '-')} debe ser AAAA-MM-DD")
            datetime.date.fromisoformat(v)
    if a.start_date and a.due_date and a.start_date > a.due_date:
        raise MilestoneError("--start-date no puede ser posterior a --due-date")
    if bool(a.project_id) == bool(a.group_id):
        raise MilestoneError("indique exactamente uno de --project-id o --group-id")
    title, description, header, pending = read_ssp(a.ssp)
    wanted = desired_fields(title, description, a)
    where = f"proyecto {a.project_id}" if a.project_id else f"grupo {a.group_id}"
    result = {"mode": a.mode, "scope": where, "title": title, "header": header, "pending_header_values": pending}
    pat = os.environ.get("GITLAB_PAT")
    if a.mode in LIVE:
        if not (a.approved_by or "").startswith("human:") or len(a.approved_by) <= len("human:"):
            raise MilestoneError("los modos que escriben exigen --approved-by human:<nombre>; sin aprobación humana solo se permite dry-run")
        if not pat:
            raise MilestoneError("GITLAB_PAT no está definida en el entorno")
    elif a.mode != "dry-run":
        raise MilestoneError(f"modo desconocido: {a.mode}")
    client = GitLab(os.environ.get("GITLAB_URL", DEFAULT_URL), pat, os.environ.get("GITLAB_CA_BUNDLE"), opener=opener)
    if a.mode == "dry-run" and not pat and opener is None:
        result.update(action="dry-run (sin consulta a GitLab: GITLAB_PAT no definida)", fields_to_send=wanted)
        return result
    existing = find(client, a, title)
    if a.mode == "dry-run":
        if existing is None:
            result.update(action="crearía", fields_to_send=wanted)
        else:
            d = diff(existing, wanted)
            result.update(action="actualizaría" if d else "sin cambios", milestone=brief(existing), changes=d)
        return result
    if existing is None:
        if a.mode == "update":
            raise MilestoneError(f"no existe un Milestone con el título '{title}' en {where}; use create o sync")
        created = client.call("POST", base_path(a), wanted)
        result.update(action="creado", milestone=brief(created), control_pack_row=control_row("crear", where, created, a.approved_by, True))
        return result
    if a.mode == "create":
        result.update(action="ya existía: no se modificó", milestone=brief(existing), changes=diff(existing, wanted),
                      control_pack_row=control_row("sin mutación;", where, existing, a.approved_by, False))
        return result
    d = diff(existing, wanted)
    if not d:
        result.update(action="sin cambios", milestone=brief(existing), control_pack_row=control_row("sin mutación;", where, existing, a.approved_by, False))
        return result
    updated = client.call("PUT", f"{base_path(a)}/{existing['id']}", {k: v["nuevo"] for k, v in d.items()})
    result.update(action="actualizado", milestone=brief(updated), changes=d, control_pack_row=control_row("actualizar", where, updated, a.approved_by, True))
    return result


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ssp")
    ap.add_argument("--project-id", type=int)
    ap.add_argument("--group-id", type=int)
    ap.add_argument("--mode", default="dry-run", choices=["dry-run", "create", "update", "sync"])
    ap.add_argument("--start-date")
    ap.add_argument("--due-date")
    ap.add_argument("--approved-by")
    a = ap.parse_args(argv)
    try:
        print(json.dumps(run(a), ensure_ascii=False, indent=2))
        return 0
    except (MilestoneError, OSError, ValueError) as ex:
        print("ERROR:", redact(str(ex), os.environ.get("GITLAB_PAT")), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
