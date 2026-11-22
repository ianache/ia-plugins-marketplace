#!/usr/bin/env python3
"""Checks deterministas del QA Test Design Pack. Stdlib + PyYAML.

Salida: JSON {"checks":[{id,result,evidence_ref,detail}]} apto para `qa_orchestrator.py gate --checks`
(el gate acepta esta salida tal cual). Solo cubre los checks `script`: el orquestador NO añade los
checks `independent-review`; quien revisa debe incluirlos en el JSON. No decide el gate.

Layout esperado del pack:
  coverage-matrix.yaml, requirements-test-traceability.yaml, TSN/*.md, TC/*.md
Formato en la plantilla de cada artefacto. Perfil `design` = TEST_DESIGN_GATE; `review` = TEST_DESIGN_REVIEW_GATE.
"""
import argparse, json, re, sys
from pathlib import Path

import yaml

TDR_SECTIONS = ["Datos requeridos", "Aislamiento y limpieza", "Privacidad y masking"]
SOURCE_TYPES = {"SYNTHETIC", "FIXTURE", "REFERENCE", "MASKED_COPY", "GENERATED", "SEEDED"}
PII = {"NONE", "SYNTHETIC", "MASKED", "REAL_AUTHORIZED"}
AUTOMATION = {"MANUAL_ONLY", "AUTOMATION_CANDIDATE", "PARTIALLY_AUTOMATED", "AUTOMATED"}
SECRET = re.compile(
    r"(?i)(?:password|passwd|secret|token|api[_-]?key|authorization)\s*[:=]\s*[\"']?(?!ref:|env:|vault:|secret:|<|\{|\$|\*)[^\s\"']{8,}"
    r"|-----BEGIN [A-Z ]*PRIVATE KEY-----|glpat-[A-Za-z0-9_-]{10,}|AKIA[0-9A-Z]{16}")

SECTIONS = {"precond": r"##\s+Precondiciones", "data": r"##\s+Datos de prueba", "oracle": r"##\s+Resultado esperado"}


def front(path):
    raw = Path(path).read_text(encoding="utf8")
    if not raw.startswith("---"):
        raise ValueError(f"{path.name}: sin frontmatter")
    return yaml.safe_load(raw.split("---", 2)[1]), raw


def section(raw, pat):
    m = re.search(pat + r"[^\n]*\n(.*?)(?=\n##\s|\Z)", raw, re.S)
    return (m.group(1).strip() if m else "")


def analyze(pack, critical):
    pack = Path(pack)
    cm = yaml.safe_load((pack / "coverage-matrix.yaml").read_text(encoding="utf8"))
    tr = yaml.safe_load((pack / "requirements-test-traceability.yaml").read_text(encoding="utf8"))
    tsn = {}
    for f in sorted((pack / "TSN").glob("*.md")):
        m, _ = front(f)
        tsn[m["id"]] = m
    tc = {}
    for f in sorted((pack / "TC").glob("*.md")):
        m, raw = front(f)
        tc[m["id"]] = (m, raw)
    tdr = {}
    for f in sorted((pack / "TDR").glob("*.md")) if (pack / "TDR").exists() else []:
        m, raw = front(f)
        tdr[m["id"]] = (m, raw)
    deferred = {d["id"]: d for d in cm.get("deferred_items", [])}
    ready = {t["id"]: t for t in cm.get("test_cases", []) if t.get("readiness") == "READY"}
    pending = [t["id"] for t in cm.get("test_cases", []) if t.get("readiness") != "READY"
               and not (t["id"] in deferred and deferred[t["id"]].get("decision_ref"))]
    out = {}

    risks = {r["risk"]: r for r in cm.get("risks", [])}
    crit = set(critical) | {k for k, r in risks.items() if r.get("critical")}
    bad = sorted(r for r in crit if not risks.get(r, {}).get("tsn") or any(t not in tsn for t in risks[r]["tsn"]))
    out["critical-risk-has-tsn"] = (not bad, bad)

    notc = sorted(t for t, m in tsn.items() if not m.get("test_cases")
                  or any(c not in tc or tc[c][0].get("tsn") != t for c in m["test_cases"]))
    out["tsn-has-tc"] = (not notc, notc)

    noracle = []
    for cid in ready:
        if cid not in tc:
            noracle.append(f"{cid}: archivo ausente")
            continue
        raw = tc[cid][1]
        for k, pat in SECTIONS.items():
            if not section(raw, pat):
                noracle.append(f"{cid}: sin {k}")
    out["approved-tc-has-oracle-and-data"] = (not noracle, noracle)

    broken, seen = [], set()
    for e in tr.get("traceability", []):
        for k in ("dsp_ref", "requirement_ref", "risk_refs", "scenario_refs", "testcase_refs"):
            if not e.get(k):
                broken.append(f"entrada sin {k}")
        broken += [f"TSN inexistente {s}" for s in e.get("scenario_refs", []) if s not in tsn]
        broken += [f"TC inexistente {c}" for c in e.get("testcase_refs", []) if c not in tc]
        seen.update(e.get("testcase_refs", []))
    broken += [f"{c} sin trazabilidad" for c in tc if c not in seen]
    out["traceability-complete"] = (not broken, sorted(set(broken)))

    gaps = []
    for r in crit:
        want = set(risks.get(r, {}).get("surfaces", []))
        have = {tc[c][0].get("surface") for t in risks.get(r, {}).get("tsn", []) for c in tsn.get(t, {}).get("test_cases", []) if c in tc}
        if want - have:
            gaps.append(f"{r}: sin TC en {sorted(want - have)}")
    out["critical-surfaces-covered"] = (not gaps, gaps)

    missing = [f for f in ("qa-test-strategy.md", "qa-test-plan.md", "test-prioritization.md") if not (pack / f).exists()]
    missing += [f"{c}: sin priority" for c, (m, _) in tc.items() if not m.get("priority")]
    out["coverage-prioritization-defined"] = (not missing, missing)

    out["no-pending-clarification-in-scope"] = (not pending, pending)

    dq = [] if (pack / "test-data-plan.md").exists() else ["falta test-data-plan.md"]
    for cid in ready:
        if cid not in tc:
            continue
        m = tc[cid][0]
        if m.get("automation_status") not in AUTOMATION:
            dq.append(f"{cid}: automation_status inválido o ausente")
        if "execution" in m:
            dq.append(f"{cid}: campo obsoleto execution (usar automation_status)")
        if m.get("data_required") is False:
            continue
        refs = m.get("tdr_refs") or []
        if not refs:
            dq.append(f"{cid}: sin tdr_refs")
        for r in refs:
            if r not in tdr:
                dq.append(f"{cid}: TDR inexistente {r}")
            elif cid not in (tdr[r][0].get("test_cases") or []):
                dq.append(f"{r}: no referencia a {cid}")
    for rid, (m, raw) in tdr.items():
        if not m.get("test_cases") or any(c not in tc for c in m["test_cases"]):
            dq.append(f"{rid}: test_cases vacío o con TC inexistente")
        if m.get("source_type") not in SOURCE_TYPES:
            dq.append(f"{rid}: source_type inválido")
        dq += [f"{rid}: sin {h}" for h in TDR_SECTIONS if not section(raw, r"##\s+" + re.escape(h))]
    out["test-data-requirements-defined"] = (not dq, dq)

    unsafe = []
    for rid, (m, _) in tdr.items():
        if m.get("pii") not in PII:
            unsafe.append(f"{rid}: pii inválido o no autorizado")
        elif m["pii"] == "REAL_AUTHORIZED" and not m.get("decision_ref"):
            unsafe.append(f"{rid}: PII real sin decision_ref humano")
    scan = [pack / "test-data-plan.md"] + sorted((pack / "TDR").glob("*.md") if (pack / "TDR").exists() else []) + [pack / "TC" / f"{c}.md" for c in tc]
    unsafe += [f"{f.name}: posible secreto persistido" for f in scan if f.exists() and SECRET.search(f.read_text(encoding="utf8"))]
    out["test-data-safe"] = (not unsafe, unsafe)
    return out


PROFILE = {
    "design": ["critical-risk-has-tsn", "tsn-has-tc", "approved-tc-has-oracle-and-data", "test-data-requirements-defined", "test-data-safe", "traceability-complete",
               "critical-surfaces-covered", "coverage-prioritization-defined", "no-pending-clarification-in-scope"],
    "review": {"critical-risk-has-tsn": "no-critical-risk-uncovered", "tsn-has-tc": "no-tsn-without-tc",
               "approved-tc-has-oracle-and-data": "no-approved-tc-without-oracle", "test-data-requirements-defined": "no-tc-without-test-data-requirement",
               "test-data-safe": "test-data-safe", "traceability-complete": "critical-traceability-complete"},
}


def checks(pack, critical, profile):
    res = analyze(pack, critical)
    names = PROFILE["design"] if profile == "design" else list(PROFILE["review"])
    out = []
    for n in names:
        ok, detail = res[n]
        out.append({"id": n if profile == "design" else PROFILE["review"][n], "result": "PASS" if ok else "FAIL",
                    "evidence_ref": f"{Path(pack).name}/{n}", "detail": detail})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--pack", required=True)
    ap.add_argument("--critical-risks", default="")
    ap.add_argument("--profile", choices=["design", "review"], default="design")
    a = ap.parse_args(argv)
    try:
        c = checks(a.pack, [x for x in a.critical_risks.split(",") if x], a.profile)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        print(json.dumps({"checks": [], "error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps({"checks": c}, ensure_ascii=False, indent=2))
    return 0 if all(x["result"] == "PASS" for x in c) else 1


if __name__ == "__main__":
    sys.exit(main())
