#!/usr/bin/env python3
"""Validate TC detail structure. Exit 1 for blocking issues. Stdlib only.

Dos niveles:
- Legacy (sin `tc_contract` en el frontmatter): reglas previas (secciones, columnas, IDs, automation_status).
- Contrato 1.3/1.4 (`tc_contract: "1.4"`, o "1.3" en TC existentes): además exige Intención, oracle con Pass when / Fail when,
  cleanup e idempotencia, requisitos de evidencia por modo, restricciones de ejecución, trazabilidad
  coherente con el frontmatter, Surface Target completo, IDs referenciados definidos, enumeraciones
  válidas y ningún placeholder sin rellenar.
Las enumeraciones deben coincidir con resources/schemas/test-case.schema.yaml (lo verifica la prueba).
"""
import argparse, json, re
from pathlib import Path

REQUIRED = ['Precondiciones','Datos de prueba','Pasos','Resultado esperado (oracle)','Postcondiciones y limpieza']
FIELDS = {'Precondiciones':['PC-ID','Estado inicial requerido','Cómo comprobarlo'], 'Datos de prueba':['TD-ID','Técnica/estrategia','Valor exacto'], 'Pasos':['STEP-ID','Acción concreta','Resultado esperado observable'], 'Resultado esperado (oracle)':['OR-ID','Aserción exacta','Fuente AC/BR/API']}
PATTERNS = {'Precondiciones':r'PC-\d+', 'Datos de prueba':r'TD-\d+', 'Pasos':r'STEP-\d+', 'Resultado esperado (oracle)':r'OR-\d+'}

AUTOMATION = {'MANUAL_ONLY','AUTOMATION_CANDIDATE','PARTIALLY_AUTOMATED','AUTOMATED'}
SURFACES = {'API','WEB','MOBILE','CROSS_SURFACE','DATABASE','EVENT','BATCH','INTEGRATION'}
TEST_LEVELS = {'unit','integration','system','e2e','security','performance'}
TEST_TYPES = {'positivo','negativo','seguridad','rendimiento','regresion'}
PRIORITIES = {'P0','P1','P2','P3'}
CRITICALITY = {'CRITICAL','HIGH','MEDIUM','LOW'}
EVIDENCE_MODES = ('MANUAL','AUTOMATED_STANDALONE','AUTOMATED_CICD')
CONTRACT_VERSION = '1.4'
CONTRACT_VERSIONS = {'1.3', '1.4'}  # 1.4 añade api_id (microservicio) para superficie API
API_ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$')
CONTRACT_SECTIONS = ['Elemento bajo prueba (Surface Target)','Intención','Precondiciones','Datos de prueba','Pasos','Resultado esperado (oracle)','Postcondiciones y limpieza','Requisitos de evidencia','Restricciones de ejecución','Trazabilidad','Automatización']
# Atributos obligatorios por superficie (resources/surface-target-standard.md).
SURFACE_ATTRS = {
    'API': ['api_id','base_url_or_service','http_method','endpoint_path','operation_id','request_contract','auth_scheme','response_contract'],
    'WEB': ['application_id','component_id','route_or_url','navigation_path','user_role','interaction_control','ui_state'],
    'MOBILE': ['application_id','platform','app_version','screen_id','navigation_path','user_role','interaction_control'],
    'DATABASE': ['datastore_id','schema','table_or_view','operation_or_query','transaction_context','data_scope'],
    'EVENT': ['broker_or_bus','topic_or_queue','event_type','schema_id_version','producer','consumer','correlation_key'],
    'BATCH': ['job_id','scheduler_or_trigger','entrypoint','input_dataset','output_artifact','execution_parameters'],
    'INTEGRATION': ['source_system','target_system','interface_id','protocol','operation_or_message','correlation_id'],
    'CROSS_SURFACE': ['journey_id','ordered_targets','entry_surface','exit_surface','correlation_id','end_to_end_oracle'],
}
PLACEHOLDER = re.compile(r'<[^>\n]+>|\bTBD\b|\bXXX\b|\bTODO\b')


def fm_fields(text):
    """Campos planos del frontmatter (las claves anidadas se ignoran)."""
    if not text.startswith('---'):
        return {}
    out = {}
    for line in text.split('---', 2)[1].splitlines():
        m = re.match(r'^([A-Za-z_]\w*):\s*(.*)$', line)
        if m:
            out[m.group(1)] = re.sub(r'\s+#.*$', '', m.group(2)).strip().strip('"')
    return out


def as_list(v):
    v = (v or '').strip()
    if v.startswith('[') and v.endswith(']'):
        v = v[1:-1]
    return [x.strip().strip('"') for x in v.split(',') if x.strip()]


def section(text, heading):
    m = re.search(r'^## ' + re.escape(heading) + r'\s*$', text, re.M)
    if not m:
        return None
    tail = text[m.end():]
    end = re.search(r'^## ', tail, re.M)
    return tail[:end.start() if end else None]


def bullets(body):
    """Pares `- clave: valor` de una sección."""
    out = {}
    for line in (body or '').splitlines():
        m = re.match(r'^\s*-\s+([\w.]+):\s*(.*)$', line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def items_under(body, label):
    """Elementos `- ...` bajo una etiqueta `Label:` (p. ej. Pass when:)."""
    items, on = [], False
    for line in (body or '').splitlines():
        if re.match(r'^\s*' + re.escape(label) + r':\s*$', line):
            on = True
            continue
        if on:
            m = re.match(r'^\s*-\s+(.+)$', line)
            if m:
                items.append(m.group(1).strip())
            elif line.strip():
                on = False
    return items


def legacy_issues(text):
    issues = []
    if text.startswith('---'):
        fm = text.split('---', 2)[1]
        m = re.search(r'^automation_status:\s*(\S+)', fm, re.M)
        if not m or m.group(1) not in AUTOMATION:
            issues.append('frontmatter: automation_status inválido o ausente')
        if re.search(r'^execution:', fm, re.M):
            issues.append('frontmatter: campo obsoleto execution (usar automation_status)')
    sections = {}
    for heading in REQUIRED:
        m = re.search(r'^## ' + re.escape(heading) + r'\s*$', text, re.M)
        if not m:
            issues.append('missing section: ' + heading)
            continue
        tail = text[m.end():]
        end = re.search(r'^## ', tail, re.M)
        sections[heading] = tail[:end.start() if end else None]
    for heading, fields in FIELDS.items():
        if heading not in sections:
            continue
        body = sections[heading]
        for field in fields:
            if field not in body:
                issues.append(heading + ': missing column ' + field)
        if not re.search(PATTERNS[heading], body):
            issues.append(heading + ': missing concrete ID row')
        rows = [r for r in body.splitlines() if r.startswith('|') and not re.match(r'^\|[- :|]+$', r)]
        if len(rows) < 2:
            issues.append(heading + ': missing data row')
    if 'Postcondiciones y limpieza' in sections and not sections['Postcondiciones y limpieza'].strip():
        issues.append('missing cleanup')
    return issues


def contract_issues(text, fm):
    issues = []
    enums = {'test_level': TEST_LEVELS, 'criticality': CRITICALITY, 'test_type': TEST_TYPES,
             'priority': PRIORITIES, 'surface': SURFACES}
    for k, allowed in enums.items():
        if fm.get(k) not in allowed:
            issues.append(f'frontmatter: {k} inválido o ausente ({fm.get(k)!r})')
    for k in ('tsn', 'dsp_ref'):
        if not fm.get(k):
            issues.append(f'frontmatter: {k} obligatorio')
    historias = as_list(fm.get('user_stories'))
    if not historias:
        issues.append('frontmatter: user_stories obligatorio (al menos una US)')
    for us in historias:
        if not re.fullmatch(r'US-\d+', str(us)):
            issues.append(f'frontmatter: user_stories contiene un ID de US inválido: {us!r}')
    if not as_list(fm.get('risks')):
        issues.append('frontmatter: risks obligatorio (al menos un RISK)')

    for h in CONTRACT_SECTIONS:
        if section(text, h) is None:
            issues.append('missing section: ' + h)

    intent = section(text, 'Intención')
    if intent is not None and not intent.strip():
        issues.append('Intención vacía')

    surf = section(text, 'Elemento bajo prueba (Surface Target)') or ''
    if fm.get('surface') in SURFACE_ATTRS:
        if not re.search(r'\|\s*Surface\s*\|\s*' + re.escape(fm['surface']) + r'\s*\|', surf):
            issues.append('Surface Target: la fila Surface no coincide con el frontmatter')
        for attr in SURFACE_ATTRS[fm['surface']]:
            if not re.search(r'\|\s*' + re.escape(attr) + r'\s*\|', surf):
                issues.append('Surface Target: falta atributo ' + attr)

    oracle = section(text, 'Resultado esperado (oracle)') or ''
    for label in ('Pass when', 'Fail when'):
        if not items_under(oracle, label):
            issues.append(f'Oracle: {label} sin condiciones observables')

    post = section(text, 'Postcondiciones y limpieza') or ''
    pb = bullets(post)
    if not pb.get('Idempotencia'):
        issues.append('Postcondiciones: falta Idempotencia')
    cr = pb.get('cleanup.required')
    if cr not in ('true', 'false'):
        issues.append('Postcondiciones: cleanup.required debe ser true o false')
    elif cr == 'true' and pb.get('cleanup.strategy_ref') in (None, '', 'null'):
        issues.append('Postcondiciones: cleanup.required true exige cleanup.strategy_ref')

    ev = bullets(section(text, 'Requisitos de evidencia') or '')
    for mode in EVIDENCE_MODES:
        if not ev.get(mode):
            issues.append(f'Requisitos de evidencia: falta {mode} (usar none si no aplica)')

    ex = bullets(section(text, 'Restricciones de ejecución') or '')
    for k in ('allowed_environments', 'forbidden_environments', 'destructive', 'requires_human_authorization'):
        if k not in ex:
            issues.append('Restricciones de ejecución: falta ' + k)
    allowed = set(as_list(ex.get('allowed_environments')))
    forbidden = set(as_list(ex.get('forbidden_environments')))
    if 'PRODUCTION' not in forbidden:
        issues.append('Restricciones de ejecución: PRODUCTION debe estar prohibido por defecto')
    if 'PRODUCTION' in allowed:
        issues.append('Restricciones de ejecución: PRODUCTION no puede estar permitido')
    if allowed & forbidden:
        issues.append('Restricciones de ejecución: entorno en allowed y forbidden: ' + ', '.join(sorted(allowed & forbidden)))
    if ex.get('destructive') == 'true' and ex.get('requires_human_authorization') != 'true':
        issues.append('Restricciones de ejecución: destructive true exige requires_human_authorization true')

    tr = bullets(section(text, 'Trazabilidad') or '')
    want = {'dsp_ref': [fm.get('dsp_ref', '')], 'user_stories': as_list(fm.get('user_stories')),
            'risks': as_list(fm.get('risks')), 'tsn': [fm.get('tsn', '')]}
    for k, expected in want.items():
        if k not in tr:
            issues.append('Trazabilidad: falta ' + k)
        elif sorted(as_list(tr[k])) != sorted(x for x in expected if x):
            issues.append(f'Trazabilidad: {k} no coincide con el frontmatter')

    td = section(text, 'Datos de prueba') or ''
    td_ids = set(re.findall(r'\bTD-\d+\b', td))
    for line in (section(text, 'Pasos') or '').splitlines():
        if line.startswith('|') and re.search(r'STEP-\d+', line):
            for ref in re.findall(r'\bTD-\d+\b', line):
                if ref not in td_ids:
                    issues.append(f'Pasos: {ref} no está definido en Datos de prueba')
    declared = set(as_list(fm.get('tdr_refs')))
    used = set(re.findall(r'\bTDR-(?!ID\b)[\w-]+\b', td))  # excluye la cabecera «TDR-ID»
    if used - declared:
        issues.append('Datos de prueba: TDR no declarado en tdr_refs: ' + ', '.join(sorted(used - declared)))

    body = text.split('---', 2)[2] if text.startswith('---') else text
    found = sorted(set(PLACEHOLDER.findall(body)))
    if found:
        issues.append('placeholders sin rellenar: ' + ', '.join(found[:5]))
    return issues


def is_legacy(text):
    return fm_fields(text).get('tc_contract') not in CONTRACT_VERSIONS


def check(text):
    issues = legacy_issues(text)
    fm = fm_fields(text)
    if fm.get('surface') == 'API':
        if not API_ID.match(fm.get('api_id') or ''):
            issues.append('frontmatter: api_id obligatorio para surface API (identificador del microservicio)')
        row = re.search(r'^\|\s*api_id\s*\|\s*([^|]+?)\s*\|', text, re.M)
        if row and row.group(1) != fm.get('api_id'):
            issues.append(f"Surface Target: api_id de la tabla ({row.group(1)}) no coincide con el frontmatter ({fm.get('api_id')})")
    if fm.get('tc_contract') in CONTRACT_VERSIONS:
        issues += contract_issues(text, fm)
    return issues


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pack', required=True); args = ap.parse_args()
    p = Path(args.pack)
    files = sorted((p / 'TC').glob('*.md')) if (p / 'TC').exists() else sorted(p.glob('TC-*.md'))
    texts = {str(f): f.read_text(encoding='utf-8') for f in files}
    result = {k: check(v) for k, v in texts.items()}
    if not files:
        result['pack'] = ['no TC files found']
    legacy = [k for k, v in texts.items() if is_legacy(v)]
    print(json.dumps({'checks': [{'id': 'tc-detail-complete', 'result': 'FAIL' if any(result.values()) else 'PASS',
                                  'evidence_ref': str(p), 'detail': result, 'legacy_without_tc_contract': legacy}]},
                     ensure_ascii=False, indent=2))
    return int(any(result.values()))


if __name__ == '__main__':
    raise SystemExit(main())
