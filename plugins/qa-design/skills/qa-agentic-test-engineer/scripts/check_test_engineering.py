#!/usr/bin/env python3
"""Checks deterministas del QA Test Engineering Pack. Stdlib + PyYAML.

Salida: JSON {"checks":[{id,result,evidence_ref,detail}]} apto para `qa_orchestrator.py gate --checks`
(el gate acepta esta salida tal cual). Solo cubre los checks `script`: el orquestador NO añade los
checks `independent-review`; quien revisa debe incluirlos en el JSON. No decide el gate.

Layout del Engineering Pack (--pack):
  test-data-manifest.yaml, automated-tests/AT-*.md, executions/EXEC-*.md, evidence/EVD-*.md,
  cicd/ci-test-execution.yaml (condicional a AUTOMATED_CICD)
Insumos aprobados del Design Pack (--design-pack): coverage-matrix.yaml, TC/*.md, TDR/*.md
Perfil `engineering` = TEST_ENGINEERING_GATE; `review` = TEST_ENGINEERING_REVIEW_GATE.
"""
import argparse, json, re, sys
from pathlib import Path

import yaml

MODES = {"MANUAL", "AUTOMATED_STANDALONE", "AUTOMATED_CICD"}
EXEC_RESULT = {"PASSED", "FAILED", "ERROR", "BLOCKED"}
FAILURE_CLASS = {"FUNCTIONAL", "PIPELINE", "ENVIRONMENT", "TEST_DATA", "TOOLING", "UNCLASSIFIED"}
PROD = {"PROD", "PRODUCTION", "PRD"}
SECRET = re.compile(
    r"(?i)(?:password|passwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*[\"']?(?!ref:|env:|vault:|secret:|<|\{|\$|\*|null)[^\s\"']{8,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|glpat-[A-Za-z0-9_-]{10,}|AKIA[0-9A-Z]{16}")
CI_REQUIRED = ("pipeline_id", "job_id", "commit_sha")


def front(path):
    raw = Path(path).read_text(encoding="utf8")
    if not raw.startswith("---"):
        raise ValueError(f"{Path(path).name}: sin frontmatter")
    return yaml.safe_load(raw.split("---", 2)[1]) or {}


def _docs(folder, pattern):
    return {m["id"]: m for m in (front(f) for f in sorted(folder.glob(pattern)))} if folder.exists() else {}


def data_blockers(tc_meta, tdrs, tdas, exceptions):
    """Razones por las que los datos de un TC no están listos (vacío = listos)."""
    if tc_meta.get("data_required") is False:
        return []
    refs = tc_meta.get("tdr_refs") or []
    out = [] if refs else ["sin tdr_refs"]
    for r in refs:
        if r not in tdrs:
            out.append(f"{r}: TDR inexistente")
        elif not any(a.get("tdr_ref") == r and a.get("readiness") == "READY" for a in tdas) and r not in exceptions:
            out.append(f"{r}: sin TDA READY ni excepción con decision_ref")
    return out


def exec_readiness(ex, tcs, tdrs, tdas, exceptions, ats):
    """('READY'|'BLOCKED', razones). Una EXEC dependiente de datos no es READY sin TDR/TDA o excepción aprobada."""
    why = []
    mode = ex.get("execution_mode")
    tc = tcs.get(ex.get("testcase_ref"))
    if mode not in MODES:
        why.append("execution_mode inválido o ausente")
    if tc is None:
        why.append("TC inexistente o fuera del alcance aprobado")
    else:
        why += data_blockers(tc, tdrs, tdas, exceptions)
    if mode in ("AUTOMATED_STANDALONE", "AUTOMATED_CICD"):
        at = ats.get(ex.get("at_ref"))
        if at is None or at.get("testcase_ref") != ex.get("testcase_ref"):
            why.append("modo automatizado sin AT que referencie al TC")
    return ("BLOCKED" if why else "READY"), why


def _es_carga(meta, tcs):
    """TC de rendimiento (test_type): su AT lo implementa loadtest-automation, no postman-automation."""
    return (tcs.get(meta.get("testcase_ref")) or {}).get("test_type") == "rendimiento"


def _reportes(pack, carpeta, nombre):
    """Reportes de subordinado en automated-tests/<carpeta>/<microservicio>/<nombre>: [(microservicio, dict)]."""
    base = pack / "automated-tests" / carpeta
    if not base.is_dir():
        return []
    return [(p.parent.name, yaml.safe_load(p.read_text(encoding="utf8")) or {}) for p in sorted(base.glob(f"*/{nombre}"))]


def analyze(pack, design):
    pack, design = Path(pack), Path(design)
    if not pack.is_dir() or not design.is_dir():
        raise ValueError("--pack y --design-pack deben ser directorios existentes")
    cm = yaml.safe_load((design / "coverage-matrix.yaml").read_text(encoding="utf8")) if (design / "coverage-matrix.yaml").exists() else {}
    ready = {t["id"] for t in cm.get("test_cases", []) if t.get("readiness") == "READY"} if cm else None
    tcs = {k: v for k, v in _docs(design / "TC", "*.md").items() if ready is None or k in ready}
    tdrs = _docs(design / "TDR", "*.md")
    ats = _docs(pack / "automated-tests", "AT-*.md")
    execs = _docs(pack / "executions", "EXEC-*.md")
    evds = _docs(pack / "evidence", "EVD-*.md")
    mf = pack / "test-data-manifest.yaml"
    man = yaml.safe_load(mf.read_text(encoding="utf8")) if mf.exists() else {}
    tdas = man.get("test_data") or []
    exceptions = {e["tdr_ref"] for e in (man.get("exceptions") or []) if e.get("tdr_ref") and e.get("decision_ref")}
    out = {}

    bad = []
    for aid, a in ats.items():
        if str(a.get("testcase_ref", "")).startswith("TSN") or str(a.get("tsn_ref", "")):
            bad.append(f"{aid}: un AT no se genera desde un TSN")
        elif a.get("testcase_ref") not in tcs:
            bad.append(f"{aid}: testcase_ref {a.get('testcase_ref')} no es un TC aprobado del alcance")
    out["at-references-approved-tc"] = (not bad, bad)

    bad = []
    for a in tdas:
        t = tdrs.get(a.get("tdr_ref"))
        if t is None:
            bad.append(f"{a.get('id')}: TDR inexistente {a.get('tdr_ref')}")
            continue
        if not a.get("testcase_refs") or any(c not in (t.get("test_cases") or []) for c in a["testcase_refs"]):
            bad.append(f"{a.get('id')}: testcase_refs no coinciden con el TDR")
    out["tda-traces-to-tdr-and-tc"] = (not bad, bad)

    bad = []
    for eid, e in execs.items():
        tc = tcs.get(e.get("testcase_ref"))
        if tc is not None and e.get("result") != "BLOCKED":
            bad += [f"{eid}: {r}" for r in data_blockers(tc, tdrs, tdas, exceptions)]
    out["test-data-ready"] = (not bad, bad)

    bad = []
    for eid, e in execs.items():
        if e.get("testcase_ref") not in tcs:
            bad.append(f"{eid}: TC fuera del alcance")
        if e.get("result") not in EXEC_RESULT:
            bad.append(f"{eid}: result inválido")
        elif e["result"] in ("PASSED", "FAILED") and e.get("oracle_evaluated") is not True:
            bad.append(f"{eid}: no evalúa el oracle del TC")
        if e.get("result") in ("FAILED", "ERROR") and e.get("failure_class") not in FAILURE_CLASS:
            bad.append(f"{eid}: falla sin failure_class")
        if e.get("result") in ("PASSED", "FAILED", "ERROR") and not any(r in evds for r in e.get("evidence_refs") or []):
            bad.append(f"{eid}: sin EVD existente")
    out["exec-evaluates-tc-oracle"] = (not bad, bad)

    explicit = [f"{eid}: execution_mode inválido o ausente" for eid, e in execs.items() if e.get("execution_mode") not in MODES]
    out["execution-mode-explicit"] = (not explicit, explicit)

    def of(mode):
        return {k: v for k, v in execs.items() if v.get("execution_mode") == mode}

    bad = []
    for eid, e in of("MANUAL").items():
        bad += [f"{eid}: falta {k}" for k in ("executor", "environment", "started_at", "finished_at") if not e.get(k)]
        if e.get("result") != "BLOCKED" and not any(r in evds for r in e.get("evidence_refs") or []):
            bad.append(f"{eid}: sin evidencia")
    out["manual-execution-evidence-complete"] = (not bad, bad)

    bad = []
    for eid, e in of("AUTOMATED_STANDALONE").items():
        st, why = exec_readiness(e, tcs, tdrs, tdas, exceptions, ats)
        bad += [f"{eid}: {w}" for w in why]
        rt = e.get("runtime") or {}
        bad += [f"{eid}: falta runtime.{k}" for k in ("name", "version") if not rt.get(k)]
        bad += [f"{eid}: falta {k}" for k in ("environment", "executor") if not e.get(k)]
        if e.get("result") in ("PASSED", "FAILED") and not any(r in evds for r in e.get("evidence_refs") or []):
            bad.append(f"{eid}: sin reporte o evidencia")
    out["standalone-execution-reproducible"] = (not bad, bad)

    bad = []
    cicd = of("AUTOMATED_CICD")
    if cicd and not (pack / "cicd" / "ci-test-execution.yaml").exists():
        bad.append("falta cicd/ci-test-execution.yaml")
    for eid, e in cicd.items():
        st, why = exec_readiness(e, tcs, tdrs, tdas, exceptions, ats)
        bad += [f"{eid}: {w}" for w in why]
        ci = e.get("ci") or {}
        if ci.get("provider") != "GITLAB":
            bad.append(f"{eid}: ci.provider debe ser GITLAB")
        if e.get("result") != "BLOCKED":
            bad += [f"{eid}: falta ci.{k}" for k in CI_REQUIRED if not ci.get(k)]
            if not any(r in evds for r in e.get("evidence_refs") or []):
                bad.append(f"{eid}: sin artifacts, reportes o logs")
    out["cicd-provenance-complete"] = (not bad, bad)

    bad = [f"{eid}: rerun_of inválido ({e['rerun_of']})" for eid, e in execs.items()
           if e.get("rerun_of") and (e["rerun_of"] not in execs or e["rerun_of"] == eid
                                     or execs[e["rerun_of"]].get("testcase_ref") != e.get("testcase_ref"))]
    ids = [f.stem for f in sorted((pack / "executions").glob("EXEC-*.md"))] if (pack / "executions").exists() else []
    bad += [f"{i}: EXEC duplicada" for i in {x for x in ids if ids.count(x) > 1}]
    out["exec-rerun-history"] = (not bad, bad)

    bad = []
    for f in sorted(p for p in pack.rglob("*") if p.is_file() and p.suffix.lower() in (".md", ".yaml", ".yml", ".json", ".csv", ".py", ".txt", ".tmpl")):
        if SECRET.search(f.read_text(encoding="utf8", errors="ignore")):
            bad.append(f"{f.relative_to(pack)}: posible secreto persistido")
    bad += [f"{eid}: AT/EXEC fuera del alcance aprobado" for eid, e in execs.items() if e.get("testcase_ref") not in tcs and e.get("testcase_ref")]
    out["no-secrets-or-scope-drift"] = (not bad, bad)

    bad = [f"{a.get('id')}: PII real sin decision_ref" for a in tdas if a.get("contains_pii") and not a.get("pii_decision_ref")]
    bad += [f"{a.get('id')}: contiene secretos" for a in tdas if a.get("contains_secrets")]
    bad += [f"{r}: PII real no autorizada" for r, t in tdrs.items() if t.get("pii") not in (None, "NONE", "SYNTHETIC", "MASKED", "REAL_AUTHORIZED")]
    out["no-unauthorized-pii"] = (not bad, bad)

    bad = [f"{eid}: ejecución en PROD sin authorization_ref" for eid, e in execs.items()
           if str(e.get("environment", "")).upper() in PROD and not e.get("authorization_ref")]
    out["no-destructive-or-unauthorized-prod"] = (not bad, bad)

    # Automatización funcional subordinada: un reporte de postman-automation por microservicio
    # (automated-tests/postman/<microservicio>/). Cada AT API funcional debe figurar AUTOMATED o PARTIAL.
    bad = []
    api_ats = [a for a in ats.values() if str(a.get("surface", "")).upper() == "API" and not _es_carga(a, tcs)]
    if api_ats:
        reps = _reportes(pack, "postman", "postman-automation-report.yaml")
        if not reps:
            bad.append("falta automated-tests/postman/<microservicio>/postman-automation-report.yaml para AT funcionales de superficie API")
        casos = {}
        for ms, rep in reps:
            for c in rep.get("casos", []) or []:
                if isinstance(c, dict):
                    casos[c.get("id")] = c
            newman = (rep.get("newman") or {}).get("estado")
            if newman != "EXECUTED":
                bad.append(f"{ms}: ejecución newman {newman or 'ausente'}: sin EXEC para los AT de superficie API")
        for a in api_ats if reps else []:
            tc = a.get("testcase_ref")
            caso = casos.get(tc)
            if caso is None:
                bad.append(f"{a.get('id')}: {tc} no aparece en ningún reporte de postman-automation")
            elif caso.get("estado") not in ("AUTOMATED", "PARTIAL"):
                bad.append(f"{a.get('id')}: {tc} con estado {caso.get('estado')} en el reporte")
    out["api-automation-subordinate-traceable"] = (not bad, bad)

    # Carga subordinada: un reporte de loadtest-automation por microservicio (automated-tests/k6/<microservicio>/).
    bad = []
    load_ats = [a for a in ats.values() if str(a.get("surface", "")).upper() == "API" and _es_carga(a, tcs)]
    if load_ats:
        reps = _reportes(pack, "k6", "loadtest-automation-report.yaml")
        if not reps:
            bad.append("falta automated-tests/k6/<microservicio>/loadtest-automation-report.yaml para AT de TC rendimiento")
        casos = {}
        for ms, rep in reps:
            for c in rep.get("casos", []) or []:
                if isinstance(c, dict):
                    casos[c.get("id")] = c
            criterio = str(rep.get("criterio", ""))
            if not (criterio == "BASELINE" or criterio.startswith("APROBADO ")):
                bad.append(f"{ms}: criterio de umbrales ausente o inválido (BASELINE o APROBADO <fuente>)")
            k6 = (rep.get("k6") or {}).get("estado")
            if k6 != "EXECUTED":
                bad.append(f"{ms}: ejecución k6 {k6 or 'ausente'}: sin EXEC para los AT de carga")
        for a in load_ats if reps else []:
            tc = a.get("testcase_ref")
            caso = casos.get(tc)
            if caso is None:
                bad.append(f"{a.get('id')}: {tc} no aparece en ningún reporte de loadtest-automation")
            elif caso.get("estado") != "IMPLEMENTED":
                bad.append(f"{a.get('id')}: {tc} con estado {caso.get('estado')} en el reporte")
    out["load-automation-subordinate-traceable"] = (not bad, bad)

    # Automatización web subordinada: un reporte de web-automation por AUT web (automated-tests/web/<aut>/).
    # Cada AT de superficie WEB debe figurar AUTOMATED o PARTIAL, y la ejecución en CI debe estar EXECUTED.
    bad = []
    web_ats = [a for a in ats.values() if str(a.get("surface", "")).upper() == "WEB"]
    if web_ats:
        reps = _reportes(pack, "web", "web-automation-report.yaml")
        if not reps:
            bad.append("falta automated-tests/web/<aut>/web-automation-report.yaml para AT de superficie WEB")
        casos = {}
        for aut, rep in reps:
            for c in rep.get("casos", []) or []:
                if isinstance(c, dict):
                    casos[c.get("id")] = c
            ejecucion = (rep.get("ejecucion") or {}).get("estado")
            if ejecucion != "EXECUTED":
                bad.append(f"{aut}: ejecución web {ejecucion or 'ausente'}: sin EXEC para los AT de superficie WEB")
        for a in web_ats if reps else []:
            tc = a.get("testcase_ref")
            caso = casos.get(tc)
            if caso is None:
                bad.append(f"{a.get('id')}: {tc} no aparece en ningún reporte de web-automation")
            elif caso.get("estado") not in ("AUTOMATED", "PARTIAL"):
                bad.append(f"{a.get('id')}: {tc} con estado {caso.get('estado')} en el reporte")
    out["web-automation-subordinate-traceable"] = (not bad, bad)

    covered = {e.get("testcase_ref") for e in execs.values()}
    miss = sorted(t for t in tcs if t not in covered)
    out["manual-and-automated-coverage-reported"] = (not miss, [f"{t}: sin EXEC" for t in miss])
    return out


PROFILE = {
    "engineering": ["at-references-approved-tc", "ssp-scope-respected", "tda-traces-to-tdr-and-tc", "test-data-ready", "exec-evaluates-tc-oracle",
                    "execution-mode-requirements", "cicd-provenance-complete", "no-secrets-or-scope-drift",
                    "no-unauthorized-pii", "no-destructive-or-unauthorized-prod", "api-automation-subordinate-traceable", "load-automation-subordinate-traceable", "web-automation-subordinate-traceable"],
    "review": {"at-references-approved-tc": "at-to-tc-traceable", "tda-traces-to-tdr-and-tc": "test-data-traceable",
               "exec-evaluates-tc-oracle": "exec-against-oracle", "execution-mode-explicit": "execution-mode-explicit",
               "manual-execution-evidence-complete": "manual-execution-evidence-complete",
               "standalone-execution-reproducible": "standalone-execution-reproducible",
               "cicd-provenance-complete": "cicd-provenance-verified",
               "manual-and-automated-coverage-reported": "manual-and-automated-coverage-reported"},
}


def ssp_scope_check(pack, ssp_tc_ids):
    """Con SSP, los AT y EXEC del pack solo pueden referenciar TC de la selección del SSP.

    ssp_tc_ids: "*" sin SSP (sin restricción); "-" SSP sin TC seleccionados; o TC-IDs separados por comas.
    """
    if ssp_tc_ids in (None, "", "*"):
        return True, []
    permitidos = set() if ssp_tc_ids == "-" else {x.strip() for x in ssp_tc_ids.split(",") if x.strip()}
    refs = [(d.get("id"), d.get("testcase_ref")) for carpeta, patron in (("automated-tests", "AT-*.md"), ("executions", "EXEC-*.md"))
            for d in _docs(pack / carpeta, patron).values()]
    bad = [f"{eid}: {tc} fuera de la selección del SSP" for eid, tc in refs if tc and tc not in permitidos]
    return (not bad), bad


def checks(pack, design, profile, ssp_tc_ids="*"):
    res = analyze(pack, design)
    res["ssp-scope-respected"] = ssp_scope_check(pack, ssp_tc_ids)
    # execution-mode-requirements = modo explícito + requisitos por modo
    parts = ("execution-mode-explicit", "manual-execution-evidence-complete", "standalone-execution-reproducible", "exec-rerun-history")
    res["execution-mode-requirements"] = (all(res[p][0] for p in parts), [d for p in parts for d in res[p][1]])
    out = []
    items = [(n, n) for n in PROFILE["engineering"]] if profile == "engineering" else list(PROFILE["review"].items())
    for n, gate_id in items:
        ok, detail = res[n]
        out.append({"id": gate_id, "result": "PASS" if ok else "FAIL", "evidence_ref": f"{Path(pack).name}/{n}", "detail": detail})
    if profile == "review":
        sec = res["no-secrets-or-scope-drift"][1] + res["no-unauthorized-pii"][1] + res["no-destructive-or-unauthorized-prod"][1]
        out.append({"id": "security-clean", "result": "FAIL" if sec else "PASS", "evidence_ref": f"{Path(pack).name}/security", "detail": sec,
                    **({"requires_hil": True} if sec else {})})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--design-pack", required=True)
    ap.add_argument("--profile", choices=["engineering", "review"], default="engineering")
    ap.add_argument("--ssp-tc-ids", default="*", help="TC del SSP separados por comas; '*' sin SSP; '-' SSP sin TC")
    a = ap.parse_args(argv)
    try:
        c = checks(a.pack, a.design_pack, a.profile, a.ssp_tc_ids)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        print(json.dumps({"checks": [], "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"checks": c}, ensure_ascii=False, indent=2))
    return 0 if all(x["result"] == "PASS" for x in c) else 1


if __name__ == "__main__":
    sys.exit(main())
