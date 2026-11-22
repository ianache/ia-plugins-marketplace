#!/usr/bin/env python3
"""Estima esfuerzo y costo de User Stories y de un Sprint (práctica de estimación v3) y propone la cabecera del Milestone.

    python estimate.py <entrada.json> [--coefficients <coef.json>] [--format json|text]

Entrada (JSON):
  {
    "sprint": {"working_days": 10, "seats": 2, "fx_pen_per_usd": 3.75},        # todos opcionales salvo working_days
    "tc_dir": "testing/qtd/TC",                                                  # opcional: cuenta TC por historia (qa-design)
    "stories": [
      {"id": "CL2-US-036", "aliases": ["US-036"], "criteria": 5, "factors": ["E", "D"], "open_questions": 0,
       "qa": {"manual_tc": 4, "automated_tc": 2}},                                # "qa" opcional si hay tc_dir
      {"id": "CL2-US-037", "us_file": "requirements/context-packs/user-stories/CL2-US-037.md", "factors": []}
    ]
  }
`criteria` se toma de los `### AC-n` del archivo `us_file` si no se indica. `qa` se toma de los TC de `tc_dir`
(frontmatter `user_story` y `execution: manual|automated`) si no se indica.

Cálculo (coeficientes en assets/estimation-coefficients.json):
  Desarrollo humano = (fijas + por_criterio × AC) × (1 + factores), redondeado hacia arriba al múltiplo de 2 h   [v2, aprobada]
  QA humano  = diseño por historia + TC manuales × h_manual + TC automatizados × h_revisión                    [aprobada, sin calibrar]
  Agente     = desarrollo humano × razón + diseño QA + TC automatizados × h_agente + TC manuales × h_agente     [aprobada, sin calibrar]
  /time = suma de horas humanas (↑ a hora entera); /cost = /time × tarifa
  /time_agent = suma de horas de agente (↑ a hora entera)
  /cost_agent = suscripción mensual × puestos × (días hábiles del Sprint / días hábiles del mes); en S/ solo si hay tipo de cambio
No consulta ni modifica GitLab. Los grupos de coeficientes no aprobados se informan en `warnings`. Solo biblioteca estándar.
"""
import argparse
import json
import math
import pathlib
import re
import sys

DEFAULTS = pathlib.Path(__file__).resolve().parents[1] / "assets" / "estimation-coefficients.json"
FRONT = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
AC = re.compile(r"(?m)^###\s+AC-\d+")


class EstimateError(ValueError):
    pass


def ceil_to(value, step):
    return math.ceil(round(value / step, 9)) * step


def money(value):
    return f"{value:,.2f}"


def num(value):
    return f"{value:g}"


def front_of(text):
    m = FRONT.match(text)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^(\w+):\s*(.*?)\s*$", line)
        if kv:
            meta[kv.group(1)] = kv.group(2).strip("'\"")
    return meta


def count_tc(tc_dir):
    """{id de historia: {'manual': n, 'automated': n}} a partir de los TC de qa-design."""
    counts = {}
    for p in sorted(pathlib.Path(tc_dir).rglob("*.md")):
        meta = front_of(p.read_text(encoding="utf-8"))
        if meta.get("type") != "TC" or not meta.get("user_story"):
            continue
        kind = "automated" if meta.get("execution", "manual").lower() in ("automated", "automatizado", "auto") else "manual"
        slot = counts.setdefault(meta["user_story"], {"manual": 0, "automated": 0})
        slot[kind] += 1
    return counts


def validate_coefficients(c):
    try:
        h = c["human"]
        for k in ("fixed_h", "per_criterion_h", "round_up_to_h", "rate_pen_per_h"):
            if not isinstance(h[k], (int, float)) or h[k] < 0:
                raise EstimateError(f"coeficiente human.{k} inválido")
        if h["round_up_to_h"] <= 0:
            raise EstimateError("human.round_up_to_h debe ser > 0")
        if c["agent_cost"]["month_working_days"] <= 0:
            raise EstimateError("agent_cost.month_working_days debe ser > 0")
        c["qa"]["design_per_story"], c["qa"]["manual_tc"], c["qa"]["automated_tc"], c["agent_effort"]["dev_agent_h_per_human_h"]
    except KeyError as ex:
        raise EstimateError(f"faltan coeficientes: {ex}") from ex


def estimate_story(s, c, tc_counts, base_dir):
    h, q = c["human"], c["qa"]
    sid = s.get("id")
    if not sid:
        raise EstimateError("cada historia necesita 'id'")
    warnings = []
    criteria = s.get("criteria")
    if criteria is None and s.get("us_file"):
        criteria = len(AC.findall((base_dir / s["us_file"]).read_text(encoding="utf-8")))
    if not isinstance(criteria, int) or criteria < 1:
        raise EstimateError(f"{sid}: 'criteria' debe ser un entero >= 1 (o indique us_file con escenarios '### AC-n')")
    codes = s.get("factors", [])
    unknown = [f for f in codes if f not in h["factors"]]
    if unknown:
        raise EstimateError(f"{sid}: factores desconocidos {unknown}; válidos: {sorted(h['factors'])} (las preguntas abiertas van en 'open_questions')")
    oq = s.get("open_questions", 0)
    if not isinstance(oq, int) or oq < 0:
        raise EstimateError(f"{sid}: 'open_questions' debe ser un entero >= 0")
    factor_sum = sum(h["factors"][f] for f in set(codes)) + min(oq * h["open_question"]["per_question"], h["open_question"]["max"])
    raw = (h["fixed_h"] + h["per_criterion_h"] * criteria) * (1 + factor_sum)
    dev_h = ceil_to(raw, h["round_up_to_h"])
    size = next((k for k in ("S", "M", "L") if dev_h <= h["size_max_h"][k]), "XL")
    confidence = "Alta" if factor_sum <= h["confidence_max_factor_sum"]["Alta"] + 1e-9 else ("Media" if factor_sum <= h["confidence_max_factor_sum"]["Media"] + 1e-9 else "Baja")
    if size == "XL":
        warnings.append(f"{sid}: talla XL ({num(dev_h)} h); dividir antes del Sprint Planning")
    elif size == "L":
        warnings.append(f"{sid}: talla L; revisar si conviene dividirla")
    qa = s.get("qa")
    if qa is None:
        found = [tc_counts[k] for k in [sid] + list(s.get("aliases", [])) if k in tc_counts]
        qa = {"manual_tc": sum(f["manual"] for f in found), "automated_tc": sum(f["automated"] for f in found)} if found else None
    if qa is None:
        warnings.append(f"{sid}: sin casos de prueba (TC) informados: el esfuerzo de QA no se estimó")
        qa = {"manual_tc": 0, "automated_tc": 0, "estimated": False}
    manual, auto = qa.get("manual_tc", 0), qa.get("automated_tc", 0)
    qa_estimated = qa.get("estimated", True)
    qa_human = (q["design_per_story"]["human_h"] if qa_estimated else 0) + manual * q["manual_tc"]["human_h"] + auto * q["automated_tc"]["human_h"]
    qa_agent = (q["design_per_story"]["agent_h"] if qa_estimated else 0) + manual * q["manual_tc"]["agent_h"] + auto * q["automated_tc"]["agent_h"]
    dev_agent = dev_h * c["agent_effort"]["dev_agent_h_per_human_h"]
    return {"id": sid, "criteria": criteria, "factors": sorted(set(codes)), "open_questions": oq, "factor_sum": round(factor_sum, 4),
            "dev_human_h": dev_h, "size": size, "confidence": confidence,
            "qa": {"manual_tc": manual, "automated_tc": auto, "estimated": qa_estimated, "human_h": qa_human, "agent_h": qa_agent},
            "dev_agent_h": dev_agent, "human_h": dev_h + qa_human, "agent_h": dev_agent + qa_agent}, warnings


def run(data, c, base_dir=pathlib.Path(".")):
    validate_coefficients(c)
    warnings = []
    for group in ("human", "agent_cost", "agent_effort", "qa"):
        if c[group].get("status") != "aprobado":
            warnings.append(f"coeficientes '{group}' en estado '{c[group].get('status')}': la estimación es una propuesta sin aprobar")
    pending_cal = [g for g in ("agent_effort", "qa") if c[g].get("calibration") == "pendiente"]
    if pending_cal:
        warnings.append("coeficientes " + ", ".join(f"'{g}'" for g in pending_cal) + " aprobados sin calibrar con datos reales: compararlos con las horas del primer Sprint cerrado")
    sprint = data.get("sprint", {})
    days = sprint.get("working_days")
    if not isinstance(days, (int, float)) or days <= 0:
        raise EstimateError("sprint.working_days debe ser un número > 0")
    tc_counts = count_tc(base_dir / data["tc_dir"]) if data.get("tc_dir") else {}
    stories = []
    for s in data.get("stories", []):
        e, w = estimate_story(s, c, tc_counts, base_dir)
        stories.append(e)
        warnings += w
    if not stories:
        raise EstimateError("no hay historias para estimar")
    time_h = math.ceil(round(sum(s["human_h"] for s in stories), 9))
    time_agent_h = math.ceil(round(sum(s["agent_h"] for s in stories), 9))
    cost = time_h * c["human"]["rate_pen_per_h"]
    ac = c["agent_cost"]
    seats = sprint.get("seats", ac["seats"])
    usd = ac["subscription_usd_per_month"] * seats * (days / ac["month_working_days"])
    fx = sprint.get("fx_pen_per_usd", ac["fx_pen_per_usd"])
    cost_agent_pen = usd * fx if fx else None
    if not fx:
        warnings.append("sin tipo de cambio (sprint.fx_pen_per_usd): /cost_agent se informa en USD y el valor en S/ queda PENDIENTE")
    header = {
        "cost": f"S/ {money(cost)}",
        "cost_agent": (f"S/ {money(cost_agent_pen)} (USD {money(usd)})" if fx else f"S/ PENDIENTE (USD {money(usd)})"),
        "time": f"{time_h} h",
        "time_agent": f"{time_agent_h} h",
    }
    return {"coefficients_version": c["version"], "stories": stories,
            "totals": {"dev_human_h": sum(s["dev_human_h"] for s in stories), "qa_human_h": sum(s["qa"]["human_h"] for s in stories),
                       "time_h": time_h, "time_agent_h": time_agent_h, "cost_pen": cost, "cost_agent_usd": round(usd, 2),
                       "cost_agent_pen": round(cost_agent_pen, 2) if fx else None,
                       "rate_pen_per_h": c["human"]["rate_pen_per_h"], "seats": seats, "sprint_working_days": days},
            "header": header, "warnings": warnings}


def to_text(r):
    lines = ["Historia | AC | Factores | Dev h | Talla | Confianza | QA manual/auto | QA h | Humano h | Agente h"]
    for s in r["stories"]:
        lines.append(f"{s['id']} | {s['criteria']} | {','.join(s['factors']) or '-'}+Q{s['open_questions']} | {num(s['dev_human_h'])} | {s['size']} | {s['confidence']} | "
                     f"{s['qa']['manual_tc']}/{s['qa']['automated_tc']} | {num(s['qa']['human_h'])} | {num(s['human_h'])} | {num(s['agent_h'])}")
    t = r["totals"]
    lines += ["", f"/cost {r['header']['cost']}", f"/cost_agent {r['header']['cost_agent']}", f"/time {r['header']['time']}", f"/time_agent {r['header']['time_agent']}",
              "", f"Desarrollo (v2) {num(t['dev_human_h'])} h + QA {num(t['qa_human_h'])} h = {t['time_h']} h × S/ {money(t['rate_pen_per_h'])}"]
    lines += ["AVISO " + w for w in r["warnings"]]
    return "\n".join(lines)


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--coefficients", default=str(DEFAULTS))
    ap.add_argument("--format", default="json", choices=["json", "text"])
    a = ap.parse_args(argv)
    try:
        path = pathlib.Path(a.input)
        data = json.loads(path.read_text(encoding="utf-8"))
        coeffs = json.loads(pathlib.Path(a.coefficients).read_text(encoding="utf-8"))
        r = run(data, coeffs, path.resolve().parent)
        print(to_text(r) if a.format == "text" else json.dumps(r, ensure_ascii=False, indent=2))
        return 0
    except (EstimateError, OSError, json.JSONDecodeError) as ex:
        print("ERROR:", ex, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
