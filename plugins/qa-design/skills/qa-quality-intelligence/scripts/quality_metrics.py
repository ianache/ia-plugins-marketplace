#!/usr/bin/env python3
"""Métricas de calidad segmentadas por modo de ejecución. Stdlib + PyYAML.

Lee las EXEC del Engineering Pack (--pack) y el Design Pack (--design-pack) y calcula métricas globales y por
segmento: execution_mode, automation_status, test_surface, environment, pipeline, suite, risk y requirement.
No emite recomendación ni decide el gate: solo evidencia determinista para `qa-quality-intelligence`.

Una falla de pipeline, entorno, datos o herramienta NO se cuenta como falla funcional; una falla sin
`failure_class` (o UNCLASSIFIED) se reporta como no clasificada y el check correspondiente falla.
"""
import argparse, json, sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml

MODES = ("MANUAL", "AUTOMATED_STANDALONE", "AUTOMATED_CICD")
NON_FUNCTIONAL = {"PIPELINE", "ENVIRONMENT", "TEST_DATA", "TOOLING"}
DIMENSIONS = ("execution_mode", "automation_status", "test_surface", "environment", "pipeline", "suite", "risk", "requirement")


def front(path):
    raw = Path(path).read_text(encoding="utf8")
    return (yaml.safe_load(raw.split("---", 2)[1]) or {}) if raw.startswith("---") else {}


def _docs(folder, pattern):
    return {m["id"]: m for m in (front(f) for f in sorted(folder.glob(pattern)))} if folder.exists() else {}


def _secs(e):
    try:
        return (datetime.fromisoformat(str(e["finished_at"])) - datetime.fromisoformat(str(e["started_at"]))).total_seconds()
    except (KeyError, ValueError, TypeError):
        return None


def summarize(execs, evds):
    n = len(execs)
    cnt = {r: sum(1 for e in execs if e.get("result") == r) for r in ("PASSED", "FAILED", "ERROR", "BLOCKED")}
    failed = [e for e in execs if e.get("result") in ("FAILED", "ERROR")]
    fc = lambda e: e.get("failure_class") or "UNCLASSIFIED"  # noqa: E731
    finished = [e for e in execs if e.get("result") in ("PASSED", "FAILED", "ERROR")]
    durs = [d for d in (_secs(e) for e in execs) if d is not None]
    return {
        "executions": n, **{k.lower(): v for k, v in cnt.items()},
        "pass_rate": round(cnt["PASSED"] / n, 3) if n else None,
        "functional_failures": sum(1 for e in failed if fc(e) == "FUNCTIONAL"),
        "non_functional_failures": sum(1 for e in failed if fc(e) in NON_FUNCTIONAL),
        "unclassified_failures": sum(1 for e in failed if fc(e) == "UNCLASSIFIED"),
        "rerun_rate": round(sum(1 for e in execs if e.get("rerun_of")) / n, 3) if n else None,
        "avg_duration_s": round(sum(durs) / len(durs), 1) if durs else None,
        "evidence_completeness": round(sum(1 for e in finished if any(r in evds for r in e.get("evidence_refs") or [])) / len(finished), 3) if finished else None,
    }


def compute(pack, design):
    pack, design = Path(pack), Path(design)
    if not pack.is_dir() or not design.is_dir():
        raise ValueError("--pack y --design-pack deben ser directorios existentes")
    execs = list(_docs(pack / "executions", "EXEC-*.md").values())
    evds = _docs(pack / "evidence", "EVD-*.md")
    tcs = _docs(design / "TC", "*.md")
    tdrs = _docs(design / "TDR", "*.md")
    cm = yaml.safe_load((design / "coverage-matrix.yaml").read_text(encoding="utf8")) if (design / "coverage-matrix.yaml").exists() else {}
    mf = pack / "test-data-manifest.yaml"
    man = yaml.safe_load(mf.read_text(encoding="utf8")) if mf.exists() else {}
    tdas = man.get("test_data") or []
    exc = {e["tdr_ref"] for e in (man.get("exceptions") or []) if e.get("decision_ref")}

    def keys(e, dim):
        tc = tcs.get(e.get("testcase_ref"), {})
        if dim == "execution_mode": return [e.get("execution_mode") or "UNKNOWN"]
        if dim == "automation_status": return [tc.get("automation_status") or "UNKNOWN"]
        if dim == "test_surface": return [tc.get("surface") or "UNKNOWN"]
        if dim == "environment": return [e.get("environment") or "UNKNOWN"]
        if dim == "pipeline": return [str((e.get("ci") or {}).get("pipeline_id") or "NONE")]
        if dim == "suite": return [str(e.get("suite") or "NONE")]
        if dim == "risk": return list(tc.get("risks") or ["UNKNOWN"])
        return [str(tc.get("user_story") or "UNKNOWN")]

    segments = {}
    for dim in DIMENSIONS:
        groups = defaultdict(list)
        for e in execs:
            for k in keys(e, dim):
                groups[k].append(e)
        segments[dim] = {k: summarize(v, evds) for k, v in sorted(groups.items())}

    by_mode = {m: sum(1 for e in execs if e.get("execution_mode") == m) for m in MODES}
    total = len(execs)
    covered = lambda mode: {e.get("testcase_ref") for e in execs if e.get("execution_mode") == mode and e.get("result") in ("PASSED", "FAILED")}  # noqa: E731
    crit = {r["risk"] for r in (cm or {}).get("risks", []) if r.get("critical")}
    crit_hit = {r for e in execs for r in (tcs.get(e.get("testcase_ref"), {}).get("risks") or []) if r in crit}
    globalm = {
        **summarize(execs, evds),
        "manual_execution_coverage": round(len(covered("MANUAL")) / len(tcs), 3) if tcs else None,
        "automation_coverage": round(sum(1 for t in tcs.values() if t.get("automation_status") == "AUTOMATED") / len(tcs), 3) if tcs else None,
        "standalone_execution_rate": round(by_mode["AUTOMATED_STANDALONE"] / total, 3) if total else None,
        "cicd_execution_rate": round(by_mode["AUTOMATED_CICD"] / total, 3) if total else None,
        "tdr_tda_readiness": round(sum(1 for r in tdrs if any(a.get("tdr_ref") == r and a.get("readiness") == "READY" for a in tdas) or r in exc) / len(tdrs), 3) if tdrs else None,
        "critical_risk_coverage": round(len(crit_hit) / len(crit), 3) if crit else None,
        "defect_detection_by_mode": {m: sum(1 for e in execs if e.get("execution_mode") == m and e.get("result") == "FAILED" and e.get("failure_class") == "FUNCTIONAL") for m in MODES},
    }
    by_tc = defaultdict(set)
    for e in execs:
        if e.get("result") in ("PASSED", "FAILED"):
            by_tc[(e.get("testcase_ref"), e.get("environment"), (e.get("ci") or {}).get("commit_sha"))].add(e["result"])
    globalm["flaky_tests"] = sorted({k[0] for k, v in by_tc.items() if len(v) > 1})
    unclassified = sorted(e["id"] for e in execs if e.get("result") in ("FAILED", "ERROR") and (e.get("failure_class") or "UNCLASSIFIED") == "UNCLASSIFIED")
    unknown_mode = sorted(e["id"] for e in execs if e.get("execution_mode") not in MODES)
    return {"global": globalm, "segments": segments, "unclassified_failures": unclassified, "executions_without_valid_mode": unknown_mode}


def checks(pack, design):
    m = compute(pack, design)
    ref = Path(pack).name
    return [
        {"id": "results-segmented-by-mode", "result": "FAIL" if m["executions_without_valid_mode"] else "PASS",
         "evidence_ref": f"{ref}/segments", "detail": m["executions_without_valid_mode"]},
        {"id": "failures-classified-by-cause", "result": "FAIL" if m["unclassified_failures"] else "PASS",
         "evidence_ref": f"{ref}/failures", "detail": m["unclassified_failures"]},
    ]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--design-pack", required=True)
    ap.add_argument("--checks", action="store_true", help="solo los checks `script` del gate")
    a = ap.parse_args(argv)
    try:
        out = {"checks": checks(a.pack, a.design_pack)} if a.checks else compute(a.pack, a.design_pack)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not a.checks or all(c["result"] == "PASS" for c in out["checks"]) else 1


if __name__ == "__main__":
    sys.exit(main())
