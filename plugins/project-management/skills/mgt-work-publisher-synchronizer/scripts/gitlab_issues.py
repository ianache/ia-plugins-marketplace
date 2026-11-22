#!/usr/bin/env python3
"""Registra o actualiza en GitLab los issues del alcance de un Sprint: uno por User Story (label «User Story») y uno
para el Development Scope Pack (label «Proyecto»), de forma idempotente y con aprobación humana.

    python gitlab_issues.py --project-id 587 --dsp <DSP.md> --story <US.md> [--story <US.md> ...]
        [--ssp <SSP.md>] [--milestone-title "<título>" | --milestone-id N] [--label <extra> ...]
        [--kb-base-url <URL-base-de-archivos> --kb-root <raíz-local>] [--estimates <estimaciones.json>]
        [--project-issue-iid N] [--mode dry-run|create|update|sync] [--approved-by human:<nombre>]

- Cada historia es un issue con el label «User Story» y el Milestone del Sprint. Título `US{iid}: <título>` (el iid lo asigna GitLab al
  crear, por eso se crea y luego se completa el título). Descripción: fuente única de la historia (enlace al repositorio y ruta local),
  estimación de esfuerzo de referencia y trazabilidad (DSP, SSP, US, Project ID, Issue ID e IID, Project Issue, Milestone). No copia
  la historia, sus criterios ni la Definition of Done: esos viven solo en el archivo de la historia.
- Cada User Story debe tener dos issues con el label «Task» (y «Dev» o «QA»), creados o ya existentes: `US{iid}: Coordinación del
  desarrollo con Superpowers` y `US{iid}: Coordinación del Aseguramiento de Calidad`. Cada uno se basa en una plantilla
  (`templates/task-issue-dev.md`, `templates/task-issue-qa.md`) con tabla de contenido y tres secciones: Scope, Acceptance Criteria y
  Condition of Done. Quedan asociados al mismo Milestone de la historia y enlazados a ella (`relates_to`).
- La estimación de esfuerzo la entrega una persona o el estimador (`--estimates`). Acepta la salida de `estimate.py` del skill
  `mgt-backlog-iteration-planner` (`{"stories": [...]}`) o un JSON `{"<US-id>": {"hours": 68, "size": "XL", "confidence": "Media",
  "basis": "...", "note": "...", "dev_hours": 40, "qa_hours": 28}}`. El estimate es horas de persona más horas del agente de IA (no
  incluye costo). Con la salida del estimador: el issue de la historia lleva `human_h + agent_h`, la tarea Dev `dev_human_h +
  dev_agent_h` y la tarea QA `qa.human_h + qa.agent_h`. Cada total se fija en el estimate nativo del issue (`time_estimate`) para
  contrastarlo luego con `/spend`. Sin dato queda «Por definir» y no se fija nada; no se inventa. La QA sin casos de prueba no se estima.
- El DSP es un solo issue con el label «Proyecto» (sin Milestone: abarca varios Sprints). Si ya existe un Project Issue gobernado aparte
  (por ejemplo por `management-context-and-governance`), indique `--project-issue-iid N`: se enlaza desde cada historia y no se crea
  ni se modifica.
- Una historia se reconoce de nuevo (no duplica) por la línea `- US: `<ruta local>`` de su descripción, o por el marcador
  `concept_id: <ID>` de versiones previas; el título puede cambiar.
- Reglas: las historias deben tener `type: US` e `id` `<PRODUCTO>-US-NNN` (globalmente único); el DSP, `type: DSP`; toda historia debe
  aparecer en el DSP (y en el SSP si se indica `--ssp`, cuyo `dsp_id` debe coincidir): una historia fuera del alcance es un cambio, no
  una adición.
- `update` y `sync` agregan labels (`add_labels`) sin quitar los que el equipo haya puesto (por ejemplo, de estado); nunca cierran,
  reabren ni eliminan issues.
- `dry-run` (por defecto) no escribe; con `GITLAB_PAT` consulta qué existe. Los modos que escriben exigen `--approved-by human:<nombre>`
  y `GITLAB_PAT`. La credencial solo viaja en la cabecera `PRIVATE-TOKEN` y se redacta en los errores. URL: `GITLAB_URL` o
  https://project.comsatel.com.pe; CA interna opcional en `GITLAB_CA_BUNDLE`.
Salida: JSON con una fila de linaje por documento (concepto, issue, URL, resultado, labels, milestone). Solo biblioteca estándar.
Código de salida 2 ante errores de validación o de GitLab.
"""
import argparse
import json
import os
import pathlib
import re
import sys
import urllib.parse

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from gitlab_milestone import DEFAULT_URL, GitLab, MilestoneError, redact  # noqa: E402

FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
US_ID = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-US-\d{3,}")
AC_HEADING = re.compile(r"(?m)^###\s+(AC-\d+.*?)\s*$")
LIVE = {"create", "update", "sync"}
LABEL_STORY, LABEL_PROJECT, LABEL_TASK = "User Story", "Proyecto", "Task"
# Cada User Story lleva dos issues «Task», uno por rol: (clave, label de rol, plantilla, tarea del título `US{iid}: <tarea>`).
TASKS = (("dev", "Dev", "task-issue-dev.md", "Coordinación del desarrollo con Superpowers"),
         ("qa", "QA", "task-issue-qa.md", "Coordinación del Aseguramiento de Calidad"))


def read_doc(path, expected_type):
    p = pathlib.Path(path)
    text = p.read_text(encoding="utf-8")
    m = FRONT.match(text)
    if not m:
        raise MilestoneError(f"{p.name}: no tiene frontmatter YAML")
    meta = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^(\w+):\s*(.*?)\s*$", line)
        if kv:
            meta[kv.group(1)] = kv.group(2).strip("'\"")
    if meta.get("type") != expected_type:
        raise MilestoneError(f"{p.name}: se esperaba type: {expected_type} y es {meta.get('type')!r}")
    if not meta.get("id"):
        raise MilestoneError(f"{p.name}: no tiene id")
    return {"path": p, "meta": meta, "body": text[m.end():], "text": text}


def doc_url(doc, a):
    if not a.kb_base_url:
        return None
    try:
        rel = doc["path"].resolve().relative_to(pathlib.Path(a.kb_root).resolve()).as_posix()
    except ValueError as ex:
        raise MilestoneError(f"{doc['path'].name} no está dentro de --kb-root") from ex
    return a.kb_base_url.rstrip("/") + "/" + rel


def short_title(meta):
    title = meta.get("title") or meta["id"]
    rest = title[len(meta["id"]):].lstrip(" —-:") if title.startswith(meta["id"]) else title
    return f"{meta['id']} — {rest or meta['id']}"


def marker(concept_id):
    return f"<!-- concept_id: {concept_id} -->"


TEMPLATES = pathlib.Path(__file__).resolve().parent.parent / "templates"
PLACEHOLDER = re.compile(r"\{\{(\w+)\}\}")


def render_template(name, values):
    """Rellena `templates/<name>`: quita los comentarios HTML (guía de la plantilla), exige todos los valores y descarta
    las líneas que quedan vacías por un valor opcional vacío."""
    text = re.sub(r"<!--.*?-->", "", (TEMPLATES / name).read_text(encoding="utf-8"), flags=re.S)
    missing = sorted(set(PLACEHOLDER.findall(text)) - set(values))
    if missing:
        raise MilestoneError(f"la plantilla {name} necesita valores para: {', '.join(missing)}")
    out = []
    for line in text.rstrip().splitlines():
        had = bool(PLACEHOLDER.search(line))
        line = PLACEHOLDER.sub(lambda m: str(values[m.group(1)]), line)
        if had and not line.strip():
            continue
        out.append(line)
    return chr(10).join(out)


def title_rest(meta):
    title = meta.get("title") or meta["id"]
    return title[len(meta["id"]):].lstrip(" —-:") or meta["id"] if title.startswith(meta["id"]) else title


def story_title(meta, iid):
    return f"US{iid}: {title_rest(meta)}" if iid else title_rest(meta)


def effort_lines(est):
    if not est:
        return ["- **Estimación de esfuerzo:** Por definir (la entrega una persona o el estimador; no se estima aquí).",
                "- **Base de la estimación:** Por definir."]
    head = f"- **Estimación de esfuerzo:** {est['hours']:g} h"
    split = f"{est['human_hours']:g} h de persona + {est['agent_hours']:g} h de agente de IA" if est.get("agent_hours") is not None else ""
    detail = ", ".join(x for x in (split, f"talla {est['size']}" if est.get("size") else "", f"confianza {est['confidence']}" if est.get("confidence") else "") if x)
    head += f" ({detail})" if detail else ""
    head += ". Propuesta; la confirma el equipo en el Sprint Planning."
    if est.get("note"):
        head += " " + est["note"].strip()
    return [head, f"- **Base de la estimación:** {est.get('basis') or 'Por definir.'}"]


def costing_table(est):
    """Tabla de costeo: horas de persona, horas del agente de IA, total y costo de la persona (horas × tarifa del estimador)."""
    if not est or est.get("dev_human_h") is None:
        return "Por definir (la entrega el estimador; no se calcula aquí)."
    rate = est.get("rate")

    def money(h):
        return f"{h * rate:,.2f}" if rate else "Por definir"
    rows = [("Desarrollo", est["dev_human_h"], est["dev_agent_h"]), ("QA", est["qa_human_h"], est["qa_agent_h"])]
    hh, aa = sum(r[1] for r in rows), sum(r[2] for r in rows)
    lines = ["| Concepto | Horas persona | Horas agente IA | Total horas | Costo persona (S/) |", "|---|---|---|---|---|"]
    lines += [f"| {n} | {h:g} | {g:g} | {h + g:g} | {money(h)} |" for n, h, g in rows if n != "QA" or est.get("qa_estimated", True)]
    if not est.get("qa_estimated", True):
        lines.append("| QA | Sin TC | Sin TC | Sin TC | Sin TC |")
    lines.append(f"| **Total** | **{hh:g}** | **{aa:g}** | **{hh + aa:g}** | **{money(hh)}** |")
    note = (f"Tarifa de persona: S/ {rate:,.2f} por hora. " if rate else "") + "El costo del agente de IA se calcula por Sprint (`/cost_agent` del Milestone), no por historia."
    return chr(10).join(lines + ["", note])


def tasks_table(a, tasks, est):
    """Los dos issues Task de la historia con su enlace y su estimate; `tasks` = {rol: iid}."""
    lines = ["| Rol | Issue | Estimate |", "|---|---|---|"]
    for role, label, _tpl, title in TASKS:
        iid = (tasks or {}).get(role)
        hours = (est or {}).get(f"{role}_hours")
        lines.append(f"| {label} | {('#' + str(iid)) if iid else '(por crear)'} — {title} | {f'{hours:g} h' if hours else 'Por definir'} |")
    return chr(10).join(lines)


def doc_ref(doc, a):
    local = _local(doc, a)
    url = doc_url(doc, a) if _inside(doc, a) else None
    return f"[{local}]({url}) · Local: `{local}`" if url else f"Local: `{local}`"


def story_description(doc, a, milestone_title, dsp, ssp=None, est=None, issue=None, project_issue_iid=None, tasks=None):
    meta = doc["meta"]
    local = _local(doc, a)
    url = doc_url(doc, a) if _inside(doc, a) else None
    effort = effort_lines(est)
    return render_template("user-story-issue.md", {
        "hu_id": meta["id"], "title": title_rest(meta), "hu_repo": f"[{local}]({url})" if url else f"`{local}`", "hu_local": local,
        "effort_estimate": effort[0].split(":** ", 1)[1], "effort_basis": effort[1].split(":** ", 1)[1],
        "costing_table": costing_table(est), "tasks_table": tasks_table(a, tasks, est),
        "dsp_id": dsp["meta"]["id"], "dsp_ref": doc_ref(dsp, a),
        "ssp_line": f"- SSP: `{ssp['meta']['id']}` ({doc_ref(ssp, a)})" if ssp else "",
        "project_id": a.project_id,
        "issue_id": issue["id"] if issue else "(se asigna al crear)", "issue_iid": issue["iid"] if issue else "(se asigna al crear)",
        "project_issue": f"#{project_issue_iid}" if project_issue_iid else "(por crear)",
        "milestone_title": milestone_title or "(sin asignar)"})


def _local(doc, a):
    return doc["path"].resolve().relative_to(pathlib.Path(a.kb_root).resolve()).as_posix() if _inside(doc, a) else doc["path"].name


def trace_line(local):
    return f"- US: `{local}`"


def _inside(doc, a):
    try:
        doc["path"].resolve().relative_to(pathlib.Path(a.kb_root).resolve())
        return True
    except ValueError:
        return False


def section(doc, *names):
    """Cuerpo de la primera sección `## <nombre>` del documento, o '' si no existe."""
    for name in names:
        m = re.search(rf"(?ms)^##\s+{re.escape(name)}\s*$\n(.*?)(?=^##\s|\Z)", doc["body"])
        if m:
            return m.group(1).strip()
    return ""


RISK_KEYS = ("id", "risk", "classification", "impact", "probability", "incidence", "affects", "response", "owner")


def risk_row(r):
    return "| " + " | ".join(str(r.get(k, "")) for k in RISK_KEYS) + " |"


def estimation_table(stories):
    """Tabla del alcance: una fila por User Story con talla, # CA y las horas de persona, agente de IA y total de QA y Dev."""
    head = ["Código", "Título", "Talla", "# CA", "Horas persona QA", "Horas agente QA", "Horas persona Dev", "Horas agente Dev", "Horas total QA", "Horas total Dev", "Horas total"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    sums, counted = [0.0] * 7, 0

    def h(v):
        return f"{v:g}"
    for s in stories:
        e = s.get("est") or {}
        if e.get("dev_human_h") is None:
            lines.append(f"| {s['id']} | {s.get('title', '')} | " + " | ".join(["Por definir"] * 9) + " |")
            continue
        qh, qa_, dh, da = e["qa_human_h"], e["qa_agent_h"], e["dev_human_h"], e["dev_agent_h"]
        vals = [qh, qa_, dh, da, qh + qa_, dh + da, qh + qa_ + dh + da]
        sums = [x + y for x, y in zip(sums, vals)]
        counted += 1
        shown = [h(v) for v in vals]
        if not e.get("qa_estimated", True):  # sin casos de prueba la QA no se estima: no es cero horas
            shown[0] = shown[1] = shown[4] = "Sin TC"
        lines.append(f"| {s['id']} | {s.get('title', '')} | {e.get('size') or '—'} | {e.get('criteria') if e.get('criteria') is not None else '—'} | " + " | ".join(shown) + " |")
    if counted:
        lines.append("| **Total** | | | | " + " | ".join(f"**{h(v)}**" for v in sums) + " |")
    return chr(10).join(lines)


def sprint_costing(sprint):
    """Totales del Sprint que calcula el estimador (/time, /cost, /time_agent, /cost_agent); vacío si no se entregaron."""
    if not sprint:
        return ""
    rows = [("Horas persona (`/time`)", sprint.get("time")), ("Costo persona (`/cost`)", sprint.get("cost")),
            ("Horas agente IA (`/time_agent`)", sprint.get("time_agent")), ("Costo agente IA (`/cost_agent`)", sprint.get("cost_agent"))]
    return chr(10).join(["| Total del Sprint | Valor |", "|---|---|"] + [f"| {k} | {v} |" for k, v in rows if v])


def project_description(dsp, a, stories, ssp=None, milestone=None, issue=None, data=None, sprint=None):
    """Project Issue (label «Proyecto») desde `templates/project-issue.md`; riesgos y textos propios llegan en `--project-data`."""
    data = data or {}
    meta = dsp["meta"]
    rows = [f"| {s['id']} | {s.get('title', '')} | {('#' + str(s['iid'])) if s.get('iid') else '(issue por crear)'} |" for s in stories]
    scope = chr(10).join(["| Historia | Título | Issue |", "|---|---|---|"] + rows) if rows else "Por definir."
    milestone_rows = f"| 1 | {ssp['meta']['id']} — {title_rest(ssp['meta'])} | {milestone} |" if ssp and milestone else ""
    text = render_template("project-issue.md", {
        "dsp_id": meta["id"], "project_name": data.get("project_name") or title_rest(meta),
        "objective": data.get("objective") or section(dsp, "Objetivo") or meta.get("description", "").strip() or "Por definir.",
        "scope": data.get("scope") or scope,
        "exclusions": data.get("exclusions") or section(dsp, "Trabajo excluido", "Exclusiones") or "Por definir.",
        "risks_intro": data.get("risks_intro") or "Riesgos identificados para el alcance de " + meta["id"] + ".",
        "risk_rows": chr(10).join(risk_row(r) for r in data.get("risks", [])),
        "estimation_table": estimation_table(stories) if stories else "Por definir.",
        "sprint_costing": sprint_costing(sprint),
        "milestones_intro": data.get("milestones_intro") or ("" if milestone_rows else "Aún no hay Milestones."),
        "milestone_rows": milestone_rows,
        "dsp_ref": doc_ref(dsp, a), "project_id": a.project_id,
        "issue_id": issue["id"] if issue else "(se asigna al crear)", "issue_iid": issue["iid"] if issue else "(se asigna al crear)"})
    return text + chr(10) * 2 + marker(meta["id"])


def issues_path(a):
    return f"/projects/{a.project_id}/issues"


def find_issue(client, a, concept_id, local=None):
    """Busca por el marcador `concept_id` y, para historias, también por la línea `- US: <ruta local>`."""
    def matches(i):
        d = i.get("description") or ""
        return marker(concept_id) in d or bool(local and trace_line(local) in d)
    hits, seen = [], set()
    for term in [concept_id] + ([local] if local else []):
        q = urllib.parse.urlencode({"search": term, "in": "description", "state": "all", "per_page": 100})
        for i in client.call("GET", f"{issues_path(a)}?{q}"):
            if matches(i) and i["iid"] not in seen:
                seen.add(i["iid"])
                hits.append(i)
    if len(hits) > 1:
        raise MilestoneError(f"hay {len(hits)} issues para {concept_id}; resolver a mano antes de continuar")
    return hits[0] if hits else None


def resolve_milestone(client, a):
    """Devuelve (id, título) o (None, título pendiente) si es un dry-run sin consulta."""
    if a.milestone_id:
        return a.milestone_id, a.milestone_title
    if not a.milestone_title:
        return None, None
    if client is None:
        return None, a.milestone_title
    q = urllib.parse.urlencode({"title": a.milestone_title, "include_parent_milestones": "false", "per_page": 100})
    exact = [m for m in client.call("GET", f"/projects/{a.project_id}/milestones?{q}") if m.get("title") == a.milestone_title]
    if len(exact) != 1:
        raise MilestoneError(f"se esperaba exactamente un Milestone titulado '{a.milestone_title}' y hay {len(exact)}; créelo antes con gitlab_milestone.py")
    return exact[0]["id"], a.milestone_title


def labels_of(issue):
    return sorted(issue.get("labels") or [])


def upsert(client, a, concept_id, title, description, label, milestone_id, kind, local=None, render=None, est=None):
    """`render(issue)` devuelve (título, descripción) con el id e iid reales; solo las historias lo usan."""
    wanted_labels = [label] + [l for l in a.label if l != label]
    row = {"kind": kind, "concept_id": concept_id, "title": title, "labels": wanted_labels}
    if est:
        row["estimate_hours"] = est["hours"]
    if client is None:
        row.update(action="crearía o actualizaría (sin consulta a GitLab: GITLAB_PAT no definida)")
        return row
    existing = find_issue(client, a, concept_id, local)
    if render and existing:
        title, description = render(existing)
        row["title"] = title
    if a.mode == "dry-run":
        if existing is None:
            row.update(action="crearía")
        else:
            changes = changes_for(existing, title, description, wanted_labels, milestone_id, est)
            row.update(action="actualizaría" if changes else "sin cambios", issue=brief(existing), changes=sorted(changes))
        return row
    if existing is None:
        if a.mode == "update":
            raise MilestoneError(f"no existe un issue para {concept_id}; use create o sync")
        payload = {"title": title, "description": description, "labels": ",".join(wanted_labels)}
        if milestone_id:
            payload["milestone_id"] = milestone_id
        created = client.call("POST", issues_path(a), payload)
        if render:  # el iid y el id solo existen ahora: completar título y trazabilidad
            ftitle, fdesc = render(created)
            created = client.call("PUT", f"{issues_path(a)}/{created['iid']}", {"title": ftitle, "description": fdesc})
            row["title"] = ftitle
        if est:
            created = set_estimate(client, a, created, est)
        row.update(action="creado", issue=brief(created))
        return row
    if a.mode == "create":
        row.update(action="ya existía: no se modificó", issue=brief(existing), changes=sorted(changes_for(existing, title, description, wanted_labels, milestone_id, est)))
        return row
    changes = changes_for(existing, title, description, wanted_labels, milestone_id, est)
    if not changes:
        row.update(action="sin cambios", issue=brief(existing))
        return row
    estimate = changes.pop("time_estimate", None)
    updated = client.call("PUT", f"{issues_path(a)}/{existing['iid']}", changes) if changes else existing
    if estimate:
        updated = set_estimate(client, a, updated, est)
    row.update(action="actualizado", issue=brief(updated), changes=sorted(list(changes) + (["time_estimate"] if estimate else [])))
    return row


def duration(hours):
    """Horas (posiblemente fraccionarias) como duración de GitLab: 68 -> `68h`, 2.5 -> `2h30m`."""
    h, m = divmod(int(round(hours * 60)), 60)
    return (f"{h}h" if h else "") + (f"{m}m" if m else "") or "0h"


def set_estimate(client, a, issue, est):
    """Estimate nativo de GitLab (equivale a `/estimate <duración>`)."""
    stats = client.call("POST", f"{issues_path(a)}/{issue['iid']}/time_estimate", {"duration": duration(est["hours"])})
    issue = dict(issue)
    issue["time_stats"] = stats if isinstance(stats, dict) else {"time_estimate": int(est["hours"] * 3600)}
    return issue


def norm(v):
    return (v or "").replace("\r\n", "\n").strip()


def changes_for(existing, title, description, wanted_labels, milestone_id, est=None):
    out = {}
    if est and int((existing.get("time_stats") or {}).get("time_estimate") or 0) != int(round(est["hours"] * 3600)):
        out["time_estimate"] = duration(est["hours"])
    if norm(existing.get("title")) != norm(title):
        out["title"] = title
    if norm(existing.get("description")) != norm(description):
        out["description"] = description
    missing = [l for l in wanted_labels if l not in labels_of(existing)]
    if missing:
        out["add_labels"] = ",".join(missing)
    if milestone_id and (existing.get("milestone") or {}).get("id") != milestone_id:
        out["milestone_id"] = milestone_id
    return out


def brief(i):
    return {"iid": i.get("iid"), "id": i.get("id"), "web_url": i.get("web_url"), "state": i.get("state"), "labels": labels_of(i),
            "milestone": (i.get("milestone") or {}).get("title"),
            "time_estimate_h": round(int((i.get("time_stats") or {}).get("time_estimate") or 0) / 3600, 2)}


STORY_ID_ERR = "el id de la User Story debe ser <PRODUCTO>-US-NNN (globalmente único); migre el ID previo a legacy_id"


def validate_scope(dsp, stories, ssp):
    dsp_id = dsp["meta"]["id"]
    for st in stories:
        sid = st["meta"]["id"]
        if not US_ID.fullmatch(sid):
            raise MilestoneError(f"{st['path'].name}: {STORY_ID_ERR} (actual: {sid!r})")
        if not re.search(r"(?<![\w-])" + re.escape(sid) + r"(?![\w-])", dsp["text"]):
            raise MilestoneError(f"{sid} no aparece en el DSP {dsp_id}: una historia fuera del alcance es un cambio (CHG), no una adición")
    ids = [s["meta"]["id"] for s in stories]
    if len(ids) != len(set(ids)):
        raise MilestoneError("hay historias repetidas en --story")
    if ssp:
        if ssp["meta"].get("dsp_id") != dsp_id:
            raise MilestoneError(f"el SSP referencia el DSP {ssp['meta'].get('dsp_id')!r} y se publica el {dsp_id!r}")
        for sid in ids:
            if not re.search(r"(?<![\w-])" + re.escape(sid) + r"(?![\w-])", ssp["text"]):
                raise MilestoneError(f"{sid} no aparece en el SSP {ssp['meta']['id']}")


def run(a, opener=None):
    if a.mode not in LIVE and a.mode != "dry-run":
        raise MilestoneError(f"modo desconocido: {a.mode}")
    if not a.story:
        raise MilestoneError("indique al menos una --story")
    dsp = read_doc(a.dsp, "DSP")
    stories = [read_doc(p, "US") for p in a.story]
    ssp = read_doc(a.ssp, "SSP") if a.ssp else None
    validate_scope(dsp, stories, ssp)
    pat = os.environ.get("GITLAB_PAT")
    if a.mode in LIVE:
        if not (a.approved_by or "").startswith("human:") or len(a.approved_by) <= len("human:"):
            raise MilestoneError("los modos que escriben exigen --approved-by human:<nombre>; sin aprobación humana solo se permite dry-run")
        if not pat:
            raise MilestoneError("GITLAB_PAT no está definida en el entorno")
    client = GitLab(os.environ.get("GITLAB_URL", DEFAULT_URL), pat, os.environ.get("GITLAB_CA_BUNDLE"), opener=opener)
    online = bool(pat) or opener is not None
    live_client = client if online else None
    milestone_id, milestone_title = resolve_milestone(live_client, a)
    estimates = load_estimates(a, stories)
    dsp_id = dsp["meta"]["id"]
    pi_iid, pre_created = getattr(a, "project_issue_iid", None), None
    pdata = load_project_data(a)
    sprint = load_sprint_totals(a)

    def prender(refs):
        return lambda issue: (short_title(dsp["meta"]), project_description(dsp, a, refs, ssp, milestone_title, issue, pdata, sprint))
    if not pi_iid and live_client is not None:
        found = find_issue(live_client, a, dsp_id)
        if found:
            pi_iid = found["iid"]
        elif a.mode in LIVE:  # las historias enlazan al Project Issue: crearlo antes (se completa al final con sus iid)
            pre_created = upsert(live_client, a, dsp_id, short_title(dsp["meta"]), project_description(dsp, a, [], ssp, milestone_title, None, pdata, sprint),
                                 LABEL_PROJECT, None, "project", render=prender([]))
            pi_iid = pre_created["issue"]["iid"]
    rows = []
    for st in stories:
        meta = st["meta"]
        est = estimates.get(meta["id"])

        def render(issue, st=st, meta=meta, est=est, tasks=None):
            if tasks is None and live_client is not None:  # tareas ya existentes de esta historia
                tasks = {r_: (t_ or {}).get("iid") for r_, _l, _t, _x in TASKS for t_ in [find_task(live_client, a, issue["iid"], dict((x[0], x[1]) for x in TASKS)[r_])]}
            return story_title(meta, issue["iid"]), story_description(st, a, milestone_title, dsp, ssp, est, issue, pi_iid, tasks)
        row = upsert(live_client, a, meta["id"], story_title(meta, None), story_description(st, a, milestone_title, dsp, ssp, est, None, pi_iid),
                     LABEL_STORY, milestone_id, "story", local=_local(st, a), render=render, est=est)
        row["milestone"] = milestone_title
        rows.append(row)
        task_rows = ensure_tasks(live_client, a, st, dsp, row.get("issue"), milestone_id, milestone_title, est)
        rows.extend(task_rows)
        if live_client is not None and a.mode in LIVE and row.get("issue") and any(x["action"] == "creado" for x in task_rows):
            # las tareas se crearon después de la historia: completar en su descripción la tabla de tareas con los iid reales
            refs = {x["role"]: x["issue"]["iid"] for x in task_rows if x.get("issue")}
            _, desc = render(row["issue"], tasks=refs)
            live_client.call("PUT", f"{issues_path(a)}/{row['issue']['iid']}", {"description": desc})
            if row["action"] == "sin cambios":
                row["action"] = "actualizado"
    if getattr(a, "project_issue_iid", None):
        prow = {"kind": "project", "concept_id": dsp_id, "labels": [LABEL_PROJECT], "action": "gobernado aparte: no se modificó",
                "issue": {"iid": a.project_issue_iid}}
    else:
        refs = [{"id": r["concept_id"], "iid": (r.get("issue") or {}).get("iid"), "title": title_rest(s["meta"]), "est": estimates.get(s["meta"]["id"])} for r, s in zip([r for r in rows if r["kind"] == "story"], stories)]
        prow = upsert(live_client, a, dsp_id, short_title(dsp["meta"]), project_description(dsp, a, refs, ssp, milestone_title, None, pdata, sprint),
                      LABEL_PROJECT, None, "project", render=prender(refs))
        if pre_created:
            prow["action"] = "creado"
    rows.append(prow)
    return {"mode": a.mode, "project_id": a.project_id, "milestone": milestone_title, "rows": rows,
            "lineage": [f"| {r['concept_id']} | {(r.get('issue') or {}).get('iid', '')} | {(r.get('issue') or {}).get('web_url', '')} | {r['action']} | {','.join(r['labels'])} |" for r in rows]}


def task_description(role, doc, a, dsp, story_iid):
    key, _label, template, _title = next(x for x in TASKS if x[0] == role)
    meta = doc["meta"]
    return render_template(template, {"story_ref": f"#{story_iid}" if story_iid else "(por crear)", "hu_id": meta["id"],
                                      "hu_local": _local(doc, a), "dsp_id": dsp["meta"]["id"]})


def task_title(role, story_iid):
    title = next(x[3] for x in TASKS if x[0] == role)
    return f"US{story_iid}: {title}" if story_iid else title


def find_task(client, a, story_iid, role_label):
    q = urllib.parse.urlencode({"labels": f"{LABEL_TASK},{role_label}", "search": f"US{story_iid}:", "in": "title", "state": "all", "per_page": 100})
    hits = [i for i in client.call("GET", f"{issues_path(a)}?{q}")
            if (i.get("title") or "").startswith(f"US{story_iid}:") and {LABEL_TASK, role_label} <= set(i.get("labels") or [])]
    if len(hits) > 1:
        raise MilestoneError(f"hay {len(hits)} issues {LABEL_TASK}/{role_label} para US{story_iid}; resolver a mano antes de continuar")
    return hits[0] if hits else None


def ensure_link(client, a, task, story_iid):
    """Enlaza la tarea con la historia (`relates_to`) si aún no lo está; devuelve True si creó el enlace."""
    links = client.call("GET", f"{issues_path(a)}/{story_iid}/links") or []
    if any(l.get("iid") == task["iid"] and l.get("project_id", a.project_id) == a.project_id for l in links):
        return False
    client.call("POST", f"{issues_path(a)}/{task['iid']}/links", {"target_project_id": a.project_id, "target_issue_iid": story_iid, "link_type": "relates_to"})
    return True


def ensure_tasks(client, a, doc, dsp, story, milestone_id, milestone_title, est=None):
    """Asegura los issues Dev y QA de una historia; `story` es el issue de la historia (None en un dry-run sin historia)."""
    rows = []
    story_iid = (story or {}).get("iid")
    for role, label, _template, _t in TASKS:
        title, description = task_title(role, story_iid), task_description(role, doc, a, dsp, story_iid)
        hours = (est or {}).get(f"{role}_hours")
        test = {"hours": hours} if hours else None  # estimate de la tarea: persona + agente de IA; sin dato no se fija
        row = {"kind": "task", "role": role, "concept_id": f"{doc['meta']['id']}:{role}", "title": title, "labels": [LABEL_TASK, label], "milestone": milestone_title}
        if test:
            row["estimate_hours"] = hours
        if client is None:
            row.update(action="crearía o actualizaría (sin consulta a GitLab: GITLAB_PAT no definida)")
        elif story_iid is None:
            row.update(action="crearía (la historia aún no existe)")
        else:
            existing = find_task(client, a, story_iid, label)
            wanted = [LABEL_TASK, label]
            if a.mode == "dry-run":
                if existing is None:
                    row.update(action="crearía")
                else:
                    changes = changes_for(existing, title, description, wanted, milestone_id, test)
                    linked = any(l.get("iid") == existing["iid"] for l in (client.call("GET", f"{issues_path(a)}/{story_iid}/links") or []))
                    row.update(action="actualizaría" if (changes or not linked) else "sin cambios", issue=brief(existing), changes=sorted(changes) + ([] if linked else ["link"]))
            elif existing is None:
                if a.mode == "update":
                    raise MilestoneError(f"no existe el issue {LABEL_TASK}/{label} de US{story_iid}; use create o sync")
                payload = {"title": title, "description": description, "labels": ",".join(wanted)}
                if milestone_id:
                    payload["milestone_id"] = milestone_id
                created = client.call("POST", issues_path(a), payload)
                ensure_link(client, a, created, story_iid)
                if test:
                    created = set_estimate(client, a, created, test)
                row.update(action="creado", issue=brief(created))
            elif a.mode == "create":
                row.update(action="ya existía: no se modificó", issue=brief(existing), changes=sorted(changes_for(existing, title, description, wanted, milestone_id, test)))
            else:
                changes = changes_for(existing, title, description, wanted, milestone_id, test)
                pending_estimate = changes.pop("time_estimate", None)
                updated = client.call("PUT", f"{issues_path(a)}/{existing['iid']}", changes) if changes else existing
                if pending_estimate:
                    updated = set_estimate(client, a, updated, test)
                linked_now = ensure_link(client, a, existing, story_iid)
                done = sorted(list(changes) + (["time_estimate"] if pending_estimate else [])) + (["link"] if linked_now else [])
                row.update(action="actualizado" if done else "sin cambios", issue=brief(updated), changes=done)
        rows.append(row)
    return rows


def load_project_data(a):
    """`--project-data`: JSON opcional con textos y riesgos propios del Project Issue (ver `templates/project-issue.md`)."""
    path = getattr(a, "project_data", None)
    if not path:
        return {}
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    for r in data.get("risks", []):
        if not isinstance(r, dict) or not r.get("id") or not r.get("risk"):
            raise MilestoneError("--project-data: cada riesgo necesita al menos 'id' y 'risk'")
    return data


def from_estimator(s):
    """Convierte una historia de la salida de `estimate.py` (horas de persona + agente) a lo que publica el issue."""
    qa = s.get("qa") or {}
    qa_hours = (qa.get("human_h", 0) + qa.get("agent_h", 0)) if qa.get("estimated", True) else 0
    human, agent = s["human_h"], s["agent_h"]
    codes = ", ".join(s.get("factors") or []) or "ninguno"
    return {"hours": human + agent, "human_hours": human, "agent_hours": agent, "size": s.get("size"), "confidence": s.get("confidence"),
            "dev_hours": s["dev_human_h"] + s.get("dev_agent_h", 0), "qa_hours": qa_hours or None,
            "criteria": s.get("criteria"), "qa_estimated": bool(qa.get("estimated", True)), "dev_human_h": s["dev_human_h"], "dev_agent_h": s.get("dev_agent_h", 0),
            "qa_human_h": qa.get("human_h", 0) if qa.get("estimated", True) else 0, "qa_agent_h": qa.get("agent_h", 0) if qa.get("estimated", True) else 0,
            "basis": f"{s['criteria']} criterios; factores: {codes}; preguntas abiertas no bloqueantes: {s.get('open_questions', 0)}"}


def load_sprint_totals(a):
    """Totales del Sprint de la salida de `estimate.py` (`header`: cost, time, cost_agent, time_agent); {} si no se entregaron."""
    path = getattr(a, "estimates", None)
    if not path:
        return {}
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    return data.get("header") or {} if isinstance(data, dict) and isinstance(data.get("stories"), list) else {}


def load_estimates(a, stories):
    """Lee `--estimates` (salida de `estimate.py` o JSON por historia); valida ids y horas positivas."""
    path = getattr(a, "estimates", None)
    if not path:
        return {}
    data = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and isinstance(data.get("stories"), list):
        rate = (data.get("totals") or {}).get("rate_pen_per_h")
        data = {s["id"]: dict(from_estimator(s), **({"rate": rate} if rate else {})) for s in data["stories"]}
    ids = {s["meta"]["id"] for s in stories}
    for sid, est in data.items():
        if sid not in ids:
            if len(data) > len(ids):
                continue  # la salida del estimador puede traer historias de otros Sprints
            raise MilestoneError(f"--estimates trae {sid!r}, que no es una de las --story")
        for key in ("hours", "dev_hours", "qa_hours"):
            v = est.get(key)
            if key == "hours" and (not isinstance(v, (int, float)) or isinstance(v, bool) or v <= 0):
                raise MilestoneError(f"--estimates: {sid} necesita 'hours' numérico mayor que 0")
            if v is not None and key != "hours" and (not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0):
                raise MilestoneError(f"--estimates: {sid}.{key} debe ser numérico y no negativo")
    return {k: v for k, v in data.items() if k in ids}


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--project-id", type=int, required=True)
    ap.add_argument("--dsp", required=True)
    ap.add_argument("--story", action="append", default=[])
    ap.add_argument("--ssp")
    ap.add_argument("--milestone-title")
    ap.add_argument("--milestone-id", type=int)
    ap.add_argument("--label", action="append", default=[], help="label adicional (repetible), p. ej. Producto::CL2")
    ap.add_argument("--kb-base-url")
    ap.add_argument("--kb-root", default=".")
    ap.add_argument("--mode", default="dry-run", choices=["dry-run", "create", "update", "sync"])
    ap.add_argument("--estimates", help="JSON con la estimación de esfuerzo por historia (hours, size, confidence, basis, note)")
    ap.add_argument("--project-data", help="JSON con objetivo, alcance, exclusiones, riesgos y textos del Project Issue (opcional)")
    ap.add_argument("--project-issue-iid", type=int, help="iid de un Project Issue gobernado aparte: se enlaza y no se crea ni modifica")
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
