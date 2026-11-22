#!/usr/bin/env python3
"""Checks deterministas del paquete UOW. Stdlib + PyYAML.

Salida: JSON {"checks":[{id,result,evidence_ref,detail}]} apto para `uow_orchestrator.py gate --checks`
(el orquestador añade los checks `independent-review`). No decide el gate.

Layout (--root, por defecto ./management/uows):
  UCX-NNN-<slug>.md                      contexto de la US (type UCX)
  UOW-NNN-<slug>.md                      la unidad de trabajo (type UOW)
  UOW-NNN/UCB-*.md UCM-*.md UAP-*.md UWR-*.md y uow-package.yaml
Perfiles: context, slice, binding, codebase, agent-plan, readiness, ready.
Los documentos se referencian por clave corta (`UOW-001`), el sufijo `TIPO-NNN` de su `id`.
"""
import argparse, hashlib, json, re, sys
from pathlib import Path

import yaml

MODES = {"GREENFIELD", "BROWNFIELD", "EVOLUTION"}
CLAIMS = ["Hechos", "Inferencias", "Supuestos", "Desconocidos y preguntas abiertas"]
UOW_SECTIONS = ["Objetivo y resultado esperado", "Alcance", "Criterios de aceptación cubiertos", "Contratos y datos", "Mapa de código",
                "Dependencias", "Plan para el agente", "Criterios de terminado", "Dimensión", "Riesgos y preguntas abiertas",
                "Handoff a QA", "Trazabilidad"]
SECRET = re.compile(
    r"(?i)(?:password|passwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*[\"']?(?!ref:|env:|vault:|secret:|<|\{|\$|\*|null)[^\s\"']{8,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|glpat-[A-Za-z0-9_-]{10,}|AKIA[0-9A-Z]{16}")
PLACEHOLDER = re.compile(r"<[^>]+>|\b(?:TODO|TBD|por definir|pendiente)\b|^\s*(?:latest|HEAD)\s*$", re.I)


def key(doc_id):
    m = re.search(r"([A-Z]+-\d+)$", str(doc_id))
    return m.group(1) if m else str(doc_id)


def load(path):
    raw = Path(path).read_text(encoding="utf8")
    if not raw.startswith("---"):
        raise ValueError(f"{Path(path).name}: sin frontmatter")
    return yaml.safe_load(raw.split("---", 2)[1]) or {}, raw


def section(raw, heading):
    m = re.search(r"^##\s+" + re.escape(heading) + r"[^\n]*\n(.*?)(?=^##\s|\Z)", raw, re.S | re.M)
    return m.group(1).strip() if m else None


def has(v):
    return bool(v) and not PLACEHOLDER.search(str(v))


class Pack:
    def __init__(self, root, uow=None):
        self.root = Path(root)
        if not self.root.is_dir():
            raise ValueError("--root debe ser un directorio existente")
        self.docs = {}   # (TYPE, key) -> (meta, raw, path)
        for f in sorted(self.root.rglob("*.md")):
            try:
                meta, raw = load(f)
            except ValueError:
                continue
            t = meta.get("type")
            if t in ("UCX", "UOW", "UCB", "UCM", "UAP", "UWR"):
                self.docs[(t, key(meta.get("id")))] = (meta, raw, f)
        self.uow = uow

    def of(self, t):
        return {k[1]: v for k, v in self.docs.items() if k[0] == t}

    def companion(self, t):
        return [v for k, v in self.docs.items() if k[0] == t and key(v[0].get("uow_ref", "")) == self.uow]


def check_context(p):
    out, ucx = {}, p.of("UCX")
    bad = [] if ucx else ["falta el UCX"]
    for k, (m, raw, f) in ucx.items():
        src = m.get("sources") or []
        if not src:
            bad.append(f"{k}: sin fuentes")
        bad += [f"{k}: fuente sin id, resource o version ({s.get('id')})" for s in src
                if not (has(s.get("id")) and has(s.get("resource")) and has(s.get("version")))]
    out["sources-versioned"] = bad
    bad = []
    for k, (m, raw, f) in ucx.items():
        bad += [f"{k}: falta la sección {c}" for c in CLAIMS if section(raw, c) is None]
    out["claims-separated"] = bad
    out["unknowns-listed"] = [f"{k}: la sección de desconocidos está vacía (declarar 'Ninguno' si no hay)"
                              for k, (m, raw, f) in ucx.items() if not (section(raw, "Desconocidos y preguntas abiertas") or "").strip()]
    bad = []
    for k, (m, raw, f) in ucx.items():
        if m.get("mode") not in MODES:
            bad.append(f"{k}: mode inválido")
        elif m["mode"] in ("BROWNFIELD", "EVOLUTION") and not (has((m.get("baseline") or {}).get("ref")) and has((m.get("baseline") or {}).get("commit"))):
            bad.append(f"{k}: {m['mode']} exige baseline.ref y baseline.commit")
    out["mode-baseline-consistent"] = bad
    return out


def check_slice(p):
    out, ucx, uows = {}, p.of("UCX"), p.of("UOW")
    crit = {c for m, _, _ in ucx.values() for c in (m.get("acceptance_criteria") or [])}
    covered = {c for m, _, _ in uows.values() for c in (m.get("acceptance_criteria") or [])}
    bad = [f"criterio sin UOW: {c}" for c in sorted(crit - covered)] + [f"UOW cubre un criterio fuera de la US: {c}" for c in sorted(covered - crit)]
    if not uows:
        bad.append("no hay UOW")
    out["criteria-assigned-to-uow"] = bad
    bad = []
    for k, (m, raw, f) in uows.items():
        sc = section(raw, "Alcance") or ""
        if not (re.search(r"incluye", sc, re.I) and re.search(r"excluye", sc, re.I)):
            bad.append(f"{k}: el alcance debe declarar qué incluye y qué excluye")
    out["uow-boundaries-defined"] = bad
    graph = {k: list(m.get("depends_on_uow") or []) for k, (m, _, _) in uows.items()}
    bad, state = [], {}

    def visit(n):
        if state.get(n) == 1:
            bad.append(f"ciclo entre UOW en {n}"); return
        if state.get(n) == 2 or n not in graph:
            if n not in graph: bad.append(f"dependencia desconocida {n}")
            return
        state[n] = 1
        for d in graph[n]:
            visit(d)
        state[n] = 2
    for n in graph:
        visit(n)
    out["dependencies-acyclic"] = sorted(set(bad))
    us = {m.get("us_ref") for m, _, _ in ucx.values()}
    out["uow-traces-to-us"] = [f"{k}: us_ref {m.get('us_ref')} no está en el UCX" for k, (m, _, _) in uows.items() if m.get("us_ref") not in us]
    return out


def check_binding(p):
    out = {}
    cb = p.companion("UCB")
    bad = [] if cb else [f"{p.uow}: falta el UCB"]
    ops, objs, versions = [], [], []
    for m, raw, f in cb:
        ops += m.get("api_operations") or []
        objs += m.get("data_objects") or []
        if not (m.get("api_operations") or m.get("api_not_applicable")):
            bad.append("api_operations vacío (declarar api_not_applicable con motivo si no hay API)")
        bad += [f"operación sin operation_id o contract_ref: {o}" for o in ops if not (has(o.get("operation_id")) and has(o.get("contract_ref")))]
    out["api-operations-resolved"] = bad
    bad = [] if cb else [f"{p.uow}: falta el UCB"]
    for m, raw, f in cb:
        if not (m.get("data_objects") or m.get("data_not_applicable")):
            bad.append("data_objects vacío (declarar data_not_applicable con motivo si no hay datos)")
        bad += [f"objeto de datos sin name o version: {o}" for o in objs if not (has(o.get("name")) and has(o.get("version")))]
    out["db-objects-resolved"] = bad
    bad = []
    for m, raw, f in cb:
        mapped = {e.get("api_field"): e for e in (m.get("mapping") or [])}
        for fld in m.get("api_fields") or []:
            e = mapped.get(fld)
            if e is None:
                bad.append(f"campo API sin mapeo: {fld}")
            elif not (has(e.get("column")) or has(e.get("na_reason"))):
                bad.append(f"campo API sin columna ni motivo: {fld}")
    out["api-db-consistent"] = bad
    bad = [f"versión no fijada: {x.get('operation_id') or x.get('name')}" for x in ops + objs
           if not has(x.get("contract_version") or x.get("version"))]
    out["contract-versions-pinned"] = bad
    return out


def check_compat_rollback(cm, ucx_mode):
    """D-25: en EVOLUTION el UCM registra compatibilidad hacia atrás y rollback (campo con resumen + sección con contenido)."""
    if ucx_mode != "EVOLUTION":
        return []
    bad = []
    for m, raw, f in cm:
        for field, flag, heading in (("backward_compatibility", "assessed", "Compatibilidad hacia atrás"), ("rollback", "defined", "Rollback")):
            v = m.get(field) or {}
            if not (v.get(flag) is True and has(v.get("summary"))):
                bad.append(f"{f.name}: EVOLUTION exige {field}.{flag}: true y {field}.summary")
            sec = re.search(r"(?ms)^##\s+" + re.escape(heading) + r"\s*\n(.*?)(?=^##\s|\Z)", raw)
            if not (sec and sec.group(1).strip()):
                bad.append(f"{f.name}: EVOLUTION exige la sección '## {heading}' con contenido")
    return bad


def check_codebase(p):
    out, cm = {}, p.companion("UCM")
    bad = [] if cm else [f"{p.uow}: falta el UCM"]
    ucx_mode = next((m.get("mode") for m, _, _ in p.of("UCX").values()), None)
    ra, ap, fz, bl = [], [], [], []
    for m, raw, f in cm:
        r = m.get("repository") or {}
        ra += [f"repository.{k} no fijado" for k in ("project", "target_branch", "source_ref", "source_commit") if not has(r.get(k))]
        if not m.get("allowed_paths"):
            ap.append("allowed_paths vacío")
        if not m.get("forbidden_paths"):
            fz.append("forbidden_paths vacío")
        if ucx_mode in ("BROWNFIELD", "EVOLUTION") and not (m.get("existing_code_analysis") or {}).get("performed"):
            bl.append(f"{ucx_mode} exige existing_code_analysis.performed")
    out["repo-ref-pinned"], out["allowed-paths-defined"] = bad + ra, ap
    out["forbidden-zones-defined"], out["baseline-analysis-present"] = fz, bl
    out["compat-and-rollback-present"] = check_compat_rollback(cm, ucx_mode)
    return out


def check_agent_plan(p):
    out, ap = {}, p.companion("UAP")
    steps = [s for m, _, _ in ap for s in (m.get("steps") or [])]
    bad = [] if ap and steps else [f"{p.uow}: UAP sin pasos"]
    bad += [f"{s.get('id')}: sin verify, expected o files" for s in steps if not (has(s.get("verify")) and has(s.get("expected")) and s.get("files"))]
    out["steps-verifiable"] = bad
    out["tests-before-code"] = [f"{s.get('id')}: un paso de implementación debe declarar test_first" for s in steps
                                if s.get("kind") == "impl" and s.get("test_first") is not True]
    out["stop-conditions-defined"] = [] if all(m.get("stop_conditions") for m, _, _ in ap) and ap else ["stop_conditions vacío"]
    out["deviation-protocol-present"] = [] if all(has((m.get("deviation_protocol") or {}).get("escalate_to")) for m, _, _ in ap) and ap else ["deviation_protocol.escalate_to ausente"]
    out["no-secrets"] = [f"{f.name}: posible secreto" for m, raw, f in ap if SECRET.search(raw)]
    out["dod-measurable"] = [f"{d.get('id')}: criterio sin verify" for m, _, _ in ap for d in (m.get("definition_of_done") or []) if not has(d.get("verify"))] \
        + ([] if any(m.get("definition_of_done") for m, _, _ in ap) else ["definition_of_done vacío"])
    return out


def package_digest(root, docs):
    lines = sorted(f"{d['id']}:{hashlib.sha256((Path(root) / d['path']).read_bytes()).hexdigest()}" for d in docs)
    return hashlib.sha256("\n".join(lines).encode()).hexdigest()


def check_readiness(p):
    out = {}
    uow = p.of("UOW").get(p.uow)
    bad = [] if uow else [f"{p.uow}: falta la UOW"]
    if uow:
        bad += [f"UOW: falta la sección {s}" for s in UOW_SECTIONS if section(uow[1], s) is None]
        bad += [f"falta el {t}" for t in ("UCB", "UCM", "UAP") if not p.companion(t)]
    out["package-complete"] = bad
    bad = []
    if uow:
        m = uow[0]
        if m.get("us_ref") not in {x.get("us_ref") for x, _, _ in p.of("UCX").values()}:
            bad.append("la UOW no traza a un UCX de su US")
        for t in ("UCB", "UCM", "UAP", "UWR"):
            if not p.companion(t):
                bad.append(f"{t} sin uow_ref a {p.uow}")
    out["traceability-complete"] = bad
    wr = p.companion("UWR")
    authors = {a for t in ("UOW", "UCB", "UCM", "UAP") for m, _, _ in ([uow] if t == "UOW" and uow else p.companion(t)) for a in (m.get("authored_by") or [])}
    bad = [] if wr else [f"{p.uow}: falta el UWR"]
    for m, _, _ in wr:
        if not has(m.get("reviewer")) or m["reviewer"] in authors:
            bad.append(f"el revisor {m.get('reviewer')} no es independiente de los autores")
    out["reviewer-independent-of-author"] = bad
    out["open-questions-handled"] = [f"pregunta bloqueante abierta: {q.get('id')}" for q in ((uow[0].get("open_questions") or []) if uow else [])
                                     if q.get("status") == "OPEN" and q.get("blocking", True)]
    return out


def check_ready(p):
    out = {}
    man = p.root / p.uow / "uow-package.yaml"
    bad = []
    if not man.exists():
        bad.append("falta uow-package.yaml")
    else:
        m = yaml.safe_load(man.read_text(encoding="utf8")) or {}
        try:
            if package_digest(man.parent, m.get("documents") or []) != m.get("digest"):
                bad.append("el digest del manifiesto no coincide con los documentos")
        except OSError as e:
            bad.append(f"documento del manifiesto ilegible: {e}")
        if not (m.get("documents")):
            bad.append("el manifiesto no lista documentos")
    out["package-digest-matches"] = bad
    wr = p.companion("UWR")
    out["review-recommendation-ready"] = [] if wr and all(m.get("recommendation") == "READY_FOR_APPROVAL" for m, _, _ in wr) else ["el UWR no recomienda READY_FOR_APPROVAL"]
    return out


PROFILES = {"context": check_context, "slice": check_slice, "binding": check_binding, "codebase": check_codebase,
            "agent-plan": check_agent_plan, "readiness": check_readiness, "ready": check_ready}
NEEDS_UOW = {"binding", "codebase", "agent-plan", "readiness", "ready"}


def checks(root, profile, uow=None):
    if profile in NEEDS_UOW and not uow:
        raise ValueError(f"el perfil {profile} exige --uow")
    res = PROFILES[profile](Pack(root, uow))
    return [{"id": k, "result": "FAIL" if v else "PASS", "evidence_ref": f"{Path(root).name}/{uow or 'pack'}/{k}", "detail": v}
            for k, v in res.items()]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="./management/uows")
    ap.add_argument("--profile", required=True, choices=sorted(PROFILES))
    ap.add_argument("--uow", help="clave de la UOW, p. ej. UOW-001")
    a = ap.parse_args(argv)
    try:
        c = checks(a.root, a.profile, a.uow)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        print(json.dumps({"checks": [], "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"checks": c}, ensure_ascii=False, indent=2))
    return 0 if all(x["result"] == "PASS" for x in c) else 1


if __name__ == "__main__":
    sys.exit(main())
