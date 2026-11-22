#!/usr/bin/env python3
"""Control local y auditable del run de Business Knowledge (G0-G6). Solo biblioteca estándar."""
import argparse, datetime, json, pathlib, sys

PATHMAP_VERSION = '2.0.0'
GATES = ['G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6']
# (id, skill, gate de cierre, entregables). El gate de entrada es siempre el gate incluido previo.
TASKS = [
    ('T01', 'biz-context-objectives-analyst', 'G1', ['BCP', 'BO']),
    ('T02', 'biz-stakeholder-capability-mapper', 'G2', ['STK', 'BCAP']),
    ('T03', 'biz-glossary-curator', 'G3', ['TRM']),
    ('T04', 'biz-rules-modeler', 'G4', ['BR']),
    ('T05', 'biz-information-model-designer', 'G5', ['IMD']),
    ('T07', 'biz-scenario-modeler', 'G5', ['BSN']),
    ('T06', 'biz-pack-validator-publisher', 'G6', ['BCP']),
]
# Dependencias explícitas: IMD y BSN dependen de las reglas (T04); G6 valida ambos. Sin entrada = encadenamiento lineal.
DEPS = {'T05': ['T04'], 'T07': ['T04'], 'T06': ['T05', 'T07']}
def _pathmap():
    for d in pathlib.Path(__file__).resolve().parents:
        f = d / 'assets' / 'pathmap.json'
        if f.is_file(): return json.loads(f.read_text(encoding='utf-8'))
    raise SystemExit('assets/pathmap.json no encontrado')
OUT_DIR = {k: v.rstrip('/') for k, v in _pathmap()['document_types'].items()}  # fuente unica: assets/pathmap.json
ORCH_ROOT = _pathmap()['orchestrator_root'].strip('/')  # campo orchestrator_root de pathmap.json
# 'incremental' actualiza una línea base existente: omite el contexto y el mapa de actores/capacidades (G1, G2).
OMITTABLE = ['G5']  # D-24: un cambio que no toca el modelo de información puede omitir T05/G5 con justificación
SCENARIOS = {'greenfield': [], 'brownfield': [], 'evolution': [], 'incremental': ['G1', 'G2']}
STATES = {'PENDING', 'READY', 'IN_PROGRESS', 'BLOCKED', 'NEEDS_REVIEW', 'DONE', 'FAILED'}
TRANS = {'PENDING': {'READY', 'BLOCKED'}, 'READY': {'IN_PROGRESS', 'BLOCKED'},
         'IN_PROGRESS': {'NEEDS_REVIEW', 'FAILED', 'BLOCKED'}, 'NEEDS_REVIEW': {'DONE', 'FAILED', 'BLOCKED'},
         'FAILED': {'READY'}, 'BLOCKED': {'READY'}, 'DONE': set()}
GATE_STATUS = {'NOT_READY', 'PENDING_APPROVAL', 'APPROVED', 'OMITTED'}


def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def fail(s): raise ValueError(s)
def load(p): return json.loads(pathlib.Path(p).read_text(encoding='utf-8'))
def save(p, o): pathlib.Path(p).write_text(json.dumps(o, indent=2, ensure_ascii=False), encoding='utf-8')
def paths(r): return r / 'execution-plan.json', r / 'task-ledger.json', r / 'gate-register.json'


def included(omitted): return [g for g in GATES if g not in omitted]


def check(r):
    plan, ledger, gates = map(load, paths(r))
    tasks = plan['tasks']; ids = [t['id'] for t in tasks]
    if not ids or len(ids) != len(set(ids)): fail('IDs de tarea vacíos o duplicados')
    if plan.get('pathmap_version') != PATHMAP_VERSION: fail('versión de pathmap distinta de ' + PATHMAP_VERSION)
    omitted = plan.get('omitted_gates', [])
    if omitted and not plan.get('omission_justification'): fail('gates omitidos sin justificación')
    by = {t['id']: t for t in tasks}
    for t in tasks:
        if t['gate'] not in GATES or t['entry_gate'] not in GATES: fail('gate desconocido en ' + t['id'])
        if GATES.index(t['entry_gate']) >= GATES.index(t['gate']):
            fail('gate cycle: %s entra en %s pero cierra %s' % (t['id'], t['entry_gate'], t['gate']))
        for d in t['depends_on']:
            if d not in by: fail('dependencia inexistente ' + d)
            if GATES.index(by[d]['gate']) > GATES.index(t['entry_gate']): fail('gate cycle: %s depende de un gate posterior vía %s' % (t['id'], d))
        if not t['outputs'] or not t['output_paths']: fail('contrato incompleto en ' + t['id'])
    seen, stack = set(), set()
    def visit(x):
        if x in stack: fail('ciclo en ' + x)
        if x in seen: return
        stack.add(x)
        for d in by[x]['depends_on']: visit(d)
        stack.discard(x); seen.add(x)
    for x in by: visit(x)
    if {e['task_id'] for e in ledger['entries']} != set(ids): fail('el ledger no coincide con el plan')
    if any(e['status'] not in STATES for e in ledger['entries']): fail('estado de tarea inválido')
    gs = {g['id']: g for g in gates['gates']}
    if set(gs) != set(GATES): fail('gates incompletos')
    if any(g['status'] not in GATE_STATUS for g in gs.values()): fail('estado de gate inválido')
    if any(g['status'] == 'APPROVED' and not all(g.get(k) for k in ('approver', 'decided_at', 'evidence')) for g in gs.values()):
        fail('aprobación de gate sin sustento')
    return plan, ledger, gates


def init(a):
    r = pathlib.Path(a.run); ws = pathlib.Path(a.workspace).resolve()
    if not r.resolve().is_relative_to(ws / ORCH_ROOT):
        fail('el run debe estar en ' + ORCH_ROOT)
    omitted = list(SCENARIOS[a.scenario]) + [g for g in (getattr(a, 'omit', None) or []) if g not in SCENARIOS[a.scenario]]
    if omitted and not a.justification: fail('el escenario ' + a.scenario + ' omite ' + ','.join(omitted) + ': use --justification')
    r.mkdir(parents=True, exist_ok=False)
    chosen = [t for t in TASKS if t[2] not in omitted]
    chosen_ids = [t[0] for t in chosen]
    inc = included(omitted); tasks = []; prev = None
    for tid, skill, gate, outs in chosen:
        if tid in DEPS:
            deps = [d for d in DEPS[tid] if d in chosen_ids] or ([prev] if prev else [])
        else:
            deps = [prev] if prev else []
        tasks.append({'id': tid, 'skill': skill, 'depends_on': deps, 'outputs': outs,
                      'output_paths': {o: OUT_DIR.get(o, ORCH_ROOT + '/' + r.name) for o in outs},
                      'entry_gate': inc[inc.index(gate) - 1], 'gate': gate, 'pathmap_version': PATHMAP_VERSION})
        prev = tid
    save(r / 'execution-plan.json', {'run_id': r.name, 'scenario': a.scenario, 'workspace_root': str(ws),
                                     'pathmap_version': PATHMAP_VERSION, 'omitted_gates': omitted,
                                     'omission_justification': a.justification, 'tasks': tasks})
    save(r / 'task-ledger.json', {'run_id': r.name, 'entries': [{'task_id': t['id'], 'skill': t['skill'], 'status': 'PENDING',
                                  'attempt': 0, 'updated_at': None, 'actor': None, 'evidence': [], 'reason': None} for t in tasks], 'history': []})
    save(r / 'gate-register.json', {'run_id': r.name, 'gates': [
        {'id': g, 'status': 'OMITTED' if g in omitted else ('PENDING_APPROVAL' if g == 'G0' else 'NOT_READY'),
         'approver': None, 'decided_at': None, 'evidence': []} for g in GATES]})
    check(r); print('inicializado', r)


def status(r):
    p, l, g = check(r)
    done = sum(e['status'] == 'DONE' for e in l['entries'])
    pend = [x['id'] for x in g['gates'] if x['status'] not in ('APPROVED', 'OMITTED')]
    return {'done': done, 'total': len(l['entries']), 'gates_pending': pend}


def check_evidence(ev, ws):
    """D-21: la evidencia debe ser un archivo existente dentro del workspace; se guarda su ruta relativa (portable)."""
    if not ev or not str(ev).strip(): fail('se requiere evidencia')
    root = pathlib.Path(ws).resolve(); f = pathlib.Path(ev)
    f = (f if f.is_absolute() else root / f).resolve()
    if not f.is_file(): fail('la evidencia debe ser un archivo existente: ' + str(ev))
    if not f.is_relative_to(root): fail('la evidencia debe estar dentro del workspace: ' + str(ev))
    return f.relative_to(root).as_posix()

def transition(a):
    r = pathlib.Path(a.run); p, l, g = check(r)
    task = next((t for t in p['tasks'] if t['id'] == a.task), None)
    if not task: fail('tarea desconocida')
    e = next(x for x in l['entries'] if x['task_id'] == a.task); old, new = e['status'], a.to
    if new not in TRANS[old]: fail('transición prohibida %s -> %s' % (old, new))
    if new in ('READY', 'IN_PROGRESS'):
        if any(next(x for x in l['entries'] if x['task_id'] == d)['status'] != 'DONE' for d in task['depends_on']): fail('dependencias sin DONE')
        if next(x for x in g['gates'] if x['id'] == task['entry_gate'])['status'] != 'APPROVED': fail('gate de entrada sin aprobar: ' + task['entry_gate'])
    ev = check_evidence(a.evidence, p['workspace_root']) if (a.evidence or new in ('NEEDS_REVIEW', 'DONE')) else None
    if new == 'DONE' and old != 'NEEDS_REVIEW': fail('debe pasar por revisión')
    if new == 'IN_PROGRESS': e['attempt'] += 1
    e.update(status=new, updated_at=now(), actor=a.actor, reason=a.reason)
    if ev: e['evidence'].append(ev)
    l['history'].append({'task_id': a.task, 'from': old, 'to': new, 'at': e['updated_at'], 'actor': a.actor, 'reason': a.reason})
    save(paths(r)[1], l); print(a.task, old, '->', new)


def approve(a):
    r = pathlib.Path(a.run); p, l, g = check(r)
    item = next((x for x in g['gates'] if x['id'] == a.gate), None)
    if not item: fail('gate desconocido')
    if item['status'] in ('APPROVED', 'OMITTED'): fail('el gate ya está resuelto: ' + item['status'])
    if not a.actor.startswith('human:'): fail('el aprobador debe ser human:<nombre>')
    ev = check_evidence(a.evidence, p['workspace_root'])
    inc = included(p.get('omitted_gates', [])); prev = inc[inc.index(a.gate) - 1] if a.gate != 'G0' else None
    if prev and next(x for x in g['gates'] if x['id'] == prev)['status'] != 'APPROVED': fail('gate previo sin aprobar: ' + prev)
    for t in p['tasks']:
        if t['gate'] == a.gate and next(e for e in l['entries'] if e['task_id'] == t['id'])['status'] != 'DONE':
            fail('tarea %s sin DONE' % t['id'])
    item.update(status='APPROVED', approver=a.actor, decided_at=now(), evidence=[ev])
    save(paths(r)[2], g); print(a.gate, 'APPROVED (declaración registrada; la identidad no se autentica)')


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('init'); s.add_argument('run'); s.add_argument('--scenario', required=True, choices=sorted(SCENARIOS))
    s.add_argument('--workspace', default='.'); s.add_argument('--justification')
    s.add_argument('--omit', action='append', default=[], choices=OMITTABLE, help='omite un gate y su tarea (requiere --justification); hoy solo G5 (IMD) cuando el cambio no toca el modelo de información')
    sub.add_parser('check').add_argument('run'); sub.add_parser('status').add_argument('run')
    s = sub.add_parser('transition'); s.add_argument('run'); s.add_argument('--task', required=True)
    s.add_argument('--to', required=True, choices=sorted(STATES)); s.add_argument('--actor', required=True)
    s.add_argument('--reason', required=True); s.add_argument('--evidence')
    s = sub.add_parser('approve-gate'); s.add_argument('run'); s.add_argument('--gate', required=True)
    s.add_argument('--actor', required=True); s.add_argument('--evidence', required=True)
    a = ap.parse_args()
    try:
        if a.cmd == 'init': init(a)
        elif a.cmd == 'check': check(pathlib.Path(a.run)); print('DAG, ledger y gates válidos estructuralmente')
        elif a.cmd == 'status': print(json.dumps(status(pathlib.Path(a.run))))
        elif a.cmd == 'transition': transition(a)
        else: approve(a)
    except (ValueError, KeyError, FileNotFoundError, json.JSONDecodeError) as ex:
        print('ERROR:', ex, file=sys.stderr); sys.exit(2)


if __name__ == '__main__':
    main()
