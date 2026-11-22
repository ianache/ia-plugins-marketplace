#!/usr/bin/env python3
"""Readiness de EXEC (solo lectura). Una EXEC que depende de datos no es READY sin TDR/TDA o excepción aprobada.

Regla (STD-HANDOFF/contrato 5.4): MANUAL no requiere AT; AUTOMATED_STANDALONE y AUTOMATED_CICD exigen un AT que
referencie al TC; todo TDR del TC necesita un TDA READY o una excepción con decision_ref humano. El orquestador
coordina: no diseña datos ni ejecuta pruebas.
"""
import argparse, json, sys
from pathlib import Path

import yaml

MODES = {"MANUAL", "AUTOMATED_STANDALONE", "AUTOMATED_CICD"}


def front(path):
    raw = Path(path).read_text(encoding="utf8")
    return (yaml.safe_load(raw.split("---", 2)[1]) or {}) if raw.startswith("---") else {}


def _docs(folder, pattern):
    return {m["id"]: m for m in (front(f) for f in sorted(folder.glob(pattern)))} if folder.exists() else {}


def data_blockers(tc_meta, tdrs, tdas, exceptions):
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


def evaluate(pack, design):
    pack, design = Path(pack), Path(design)
    if not pack.is_dir() or not design.is_dir():
        raise ValueError("--pack y --design-pack deben ser directorios existentes")
    tcs, tdrs = _docs(design / "TC", "*.md"), _docs(design / "TDR", "*.md")
    ats = _docs(pack / "automated-tests", "AT-*.md")
    mf = pack / "test-data-manifest.yaml"
    man = yaml.safe_load(mf.read_text(encoding="utf8")) if mf.exists() else {}
    tdas = man.get("test_data") or []
    exc = {e["tdr_ref"] for e in (man.get("exceptions") or []) if e.get("tdr_ref") and e.get("decision_ref")}
    out = {}
    for eid, ex in _docs(pack / "executions", "EXEC-*.md").items():
        st, why = exec_readiness(ex, tcs, tdrs, tdas, exc, ats)
        out[eid] = {"readiness": st, "reasons": why}
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--pack", required=True)
    ap.add_argument("--design-pack", required=True)
    a = ap.parse_args(argv)
    try:
        out = evaluate(a.pack, a.design_pack)
    except (OSError, ValueError, KeyError, yaml.YAMLError) as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False))
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if all(v["readiness"] == "READY" for v in out.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
