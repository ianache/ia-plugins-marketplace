#!/usr/bin/env python3
"""Validate TC detail structure. Exit 1 for blocking issues. Stdlib only."""
import argparse, json, re
from pathlib import Path

REQUIRED = ['Elemento bajo prueba (Surface Target)','Precondiciones','Datos de prueba','Pasos','Resultado esperado (oracle)','Postcondiciones y limpieza']
FIELDS = {'Precondiciones':['PC-ID','Estado inicial requerido','Cómo comprobarlo'], 'Datos de prueba':['TD-ID','Técnica/estrategia','Valor exacto'], 'Pasos':['STEP-ID','Acción concreta','Resultado esperado observable'], 'Resultado esperado (oracle)':['OR-ID','Aserción exacta','Fuente AC/BR/API']}
PATTERNS = {'Precondiciones':r'PC-\d+', 'Datos de prueba':r'TD-\d+', 'Pasos':r'STEP-\d+', 'Resultado esperado (oracle)':r'OR-\d+'}

SURFACE_FIELDS = {'API': ['api_id', 'base_url_or_service', 'http_method', 'endpoint_path', 'operation_id', 'request_contract', 'auth_scheme', 'response_contract'], 'WEB': ['application_id', 'component_id', 'route_or_url', 'navigation_path', 'user_role', 'interaction_control', 'ui_state'], 'MOBILE': ['application_id', 'platform', 'app_version', 'screen_id', 'navigation_path', 'user_role', 'interaction_control'], 'DATABASE': ['datastore_id', 'schema', 'table_or_view', 'operation_or_query', 'transaction_context', 'data_scope'], 'EVENT': ['broker_or_bus', 'topic_or_queue', 'event_type', 'schema_id_version', 'producer', 'consumer', 'correlation_key'], 'BATCH': ['job_id', 'scheduler_or_trigger', 'entrypoint', 'input_dataset', 'output_artifact', 'execution_parameters'], 'INTEGRATION': ['source_system', 'target_system', 'interface_id', 'protocol', 'operation_or_message', 'correlation_id'], 'CROSS_SURFACE': ['journey_id', 'ordered_targets', 'entry_surface', 'exit_surface', 'correlation_id', 'end_to_end_oracle']}
PLACEHOLDER = re.compile(r'<[^>]+>|\b(?:TODO|TBD|pendiente|por definir)\b',re.I)
def check_surface(text):
    issues=[]
    fm=re.match(r'\A---\s*\n(.*?)\n---',text,re.S)
    meta=fm.group(1) if fm else ''
    sm=re.search(r'^surface:\s*(\w+)',meta,re.M)
    tm=re.search(r'^surface_target_id:\s*(.+)$',meta,re.M)
    if not sm or sm.group(1).upper() not in SURFACE_FIELDS:return ['surface: missing or unsupported']
    kind=sm.group(1).upper()
    if not tm or PLACEHOLDER.search(tm.group(1)):issues.append('surface_target_id missing or placeholder')
    section=re.search(r'^## Elemento bajo prueba \(Surface Target\)\s*$(.*?)(?=^## |\Z)',text,re.M|re.S)
    if not section:return issues+['Surface Target section missing']
    rows={}
    for line in section.group(1).splitlines():
        if line.startswith('|'):
            cells=[x.strip() for x in line.strip('|').split('|')]
            if len(cells)==2:rows[cells[0]]=cells[1]
    for f in ['Surface','Producto / aplicación / servicio','Elemento bajo prueba','Ambiente / versión / build','Acceso / invocación','Contrato o especificación']+SURFACE_FIELDS[kind]:
        val=rows.get(f,'')
        if not val or val in ('-','---') or PLACEHOLDER.search(val):issues.append('Surface Target missing: '+f)
    if rows.get('Surface','').upper()!=kind:issues.append('Surface mismatch')
    return issues

AUTOMATION={'MANUAL_ONLY','AUTOMATION_CANDIDATE','PARTIALLY_AUTOMATED','AUTOMATED'}

def check(text):
    issues=check_surface(text)
    if text.startswith('---'):
        fm=text.split('---',2)[1]
        m=re.search(r'^automation_status:\s*(\S+)',fm,re.M)
        if not m or m.group(1) not in AUTOMATION:issues.append('frontmatter: automation_status inválido o ausente')
        if re.search(r'^execution:',fm,re.M):issues.append('frontmatter: campo obsoleto execution (usar automation_status)')
    sections={}
    for heading in REQUIRED:
        m=re.search(r'^## '+re.escape(heading)+r'\s*$',text,re.M)
        if not m:
            issues.append('missing section: '+heading); continue
        tail=text[m.end():]; end=re.search(r'^## ',tail,re.M); sections[heading]=tail[:end.start() if end else None]
    for heading, fields in FIELDS.items():
        if heading not in sections:continue
        body=sections[heading]
        for field in fields:
            if field not in body:issues.append(heading+': missing column '+field)
        if not re.search(PATTERNS[heading],body):issues.append(heading+': missing concrete ID row')
        rows=[r for r in body.splitlines() if r.startswith('|') and not re.match(r'^\|[- :|]+$',r)]
        if len(rows)<2:issues.append(heading+': missing data row')
    if 'Postcondiciones y limpieza' in sections and not sections['Postcondiciones y limpieza'].strip():issues.append('missing cleanup')
    return issues

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pack',required=True);args=ap.parse_args()
    p=Path(args.pack);files=sorted((p/'TC').glob('*.md')) if (p/'TC').exists() else sorted(p.glob('TC-*.md'))
    result={str(f):check(f.read_text(encoding='utf-8')) for f in files}
    if not files:result['pack']=['no TC files found']
    print(json.dumps({'checks':[{'id':'tc-detail-complete','result':'FAIL' if any(result.values()) else 'PASS','evidence_ref':str(p),'detail':result}]},ensure_ascii=False,indent=2))
    return int(any(result.values()))
if __name__=='__main__':raise SystemExit(main())
