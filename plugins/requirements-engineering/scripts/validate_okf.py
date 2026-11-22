#!/usr/bin/env python3
"""Validador del perfil STD-OKF-001 v0.1.0-stable para documentos conceptuales Markdown.
No certifica aprobación humana ni veracidad de fuentes. Requiere PyYAML.
"""
import argparse,datetime,re,sys
from pathlib import Path
import yaml
REQUIRED=('type','id','title','description','version','status','owner','classification','tags','generated','sources')
APPROVED=set('ACP ADH ADR AGG API ASIS ASR AT BC BCAP BCP BIC BIQ BO BR BSN C4 CFR CHG CLS CMP CTLG CTX DBM DBR DDR DMD DSH DSM DSP ENT EPC EPS ERR EVD EVT EXEC FDT FLW GOV HCB HOF IAC IAR IBL ICM ICP IDP IDS IFO IGR IHO IIA IMD IMP IOB IRB IRL IRP IRQ ISA ISD ITA ITP IXL IXP KPI LDM MOB PCH PDM QAR QDC QER QFA QQI QTD QTE QTP QTR QTS RCP RMP RSK RUN SCR SEQ SOL SSP STD STK STR SVC TC TDA TDR TKN TRM TSN UAP UCB UCM UCX UOW US UWR UXR VO WEB'.split())
PROPOSED=set()  # STD-OKF-001 v0.1.0-stable aprueba todos los tipos; se conserva la rama por compatibilidad
US_PRODUCT=re.compile(r'[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*')
ENUM_STATUS={'draft','stable','deprecated'}
ENUM_CLASS={'public','internal','confidential','restricted'}
def timestamp(value):
 if isinstance(value,datetime.datetime):return value.tzinfo is not None and value.utcoffset() is not None
 if not isinstance(value,str):return False
 try:
  d=datetime.datetime.fromisoformat(value.replace('Z','+00:00'));return d.tzinfo is not None and d.utcoffset() is not None
 except ValueError:return False

def validate(path,publication=False):
 p=Path(path);issues=[]
 try:s=p.read_text(encoding='utf-8')
 except Exception as e:return [f'No se puede leer: {e}']
 if p.name in {'index.md','log.md'}:return ['Archivo reservado: usar reglas específicas de OKF; no aplicar validador conceptual genérico']
 m=re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)',s,re.S)
 if not m:return ['Frontmatter YAML delimitado por --- no encontrado al inicio']
 try:d=yaml.safe_load(m.group(1))
 except yaml.YAMLError as e:return [f'YAML inválido: {e}']
 if not isinstance(d,dict):return ['Frontmatter debe ser mapping YAML']
 for k in REQUIRED:
  if k not in d or d[k] is None or (isinstance(d[k],str) and not d[k].strip()):issues.append(f'Campo obligatorio faltante/vacío: {k}')
 for k in ('type','id','title','description','version','status','owner','classification'):
  if k in d and not isinstance(d[k],str):issues.append(f'{k} debe ser string')
 if d.get('type') and isinstance(d['type'],str):
  if publication and d['type'] not in APPROVED:issues.append(f'type no aprobado para publicación según catálogo v0.1.0-stable: {d["type"]}')
  elif d['type'] in PROPOSED:issues.append(f'type propuesto v1.3.0, pendiente de aprobación: {d["type"]}')
  elif d['type'] not in APPROVED:issues.append(f'type no registrado en catálogo: {d["type"]}')
 if isinstance(d.get('version'),str) and not re.fullmatch(r'0|[1-9]\d*',d['version'].split('.')[0]):issues.append('version inválida')
 if isinstance(d.get('version'),str) and not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?',d['version']):issues.append('version debe ser SemVer')
 if d.get('status') not in ENUM_STATUS:issues.append('status inválido')
 if d.get('classification') not in ENUM_CLASS:issues.append('classification inválida')
 tags=d.get('tags')
 if not isinstance(tags,list) or not all(isinstance(t,str) and t and t==t.lower() for t in tags):issues.append('tags debe ser lista de strings minúsculas')
 elif len(tags)!=len(set(tags)):issues.append('tags contiene duplicados')
 g=d.get('generated')
 if not isinstance(g,dict):issues.append('generated debe ser mapping con by/at')
 else:
  by=g.get('by');at=g.get('at')
  if not isinstance(by,str) or not re.fullmatch(r'(human:[^/\s]+|process:[^/\s]+|[^/\s]+/\d+\.\d+\.\d+(?:-[^/\s]+)?)',by):issues.append('generated.by debe identificar productor y versión o human:/process:')
  if not timestamp(at):issues.append('generated.at debe ser ISO 8601 con zona')
 sources=d.get('sources')
 if not isinstance(sources,list):issues.append('sources debe ser lista')
 else:
  for i,src in enumerate(sources):
   if not isinstance(src,dict) or not isinstance(src.get('resource'),str) or not src['resource'].strip():issues.append(f'sources[{i}].resource requerido')
  if not sources and publication and not re.search(r'(?im)^(?:##? )?(?:justificaci[oó]n de (?:creaci[oó]n original|fuentes)|originalidad)(?:\s|:)',s):issues.append('sources [] requiere justificación explícita de creación original')
 for k in ('related','supersedes'):
  if k in d and (not isinstance(d[k],list) or not all(isinstance(x,str) for x in d[k])):issues.append(f'{k} debe ser lista de IDs')
 if 'verified' in d:
  if not isinstance(d['verified'],list):issues.append('verified debe ser lista')
  else:
   for i,v in enumerate(d['verified']):
    if not isinstance(v,dict) or not v.get('by') or not timestamp(v.get('at')):issues.append(f'verified[{i}] requiere by y at con zona')
 if d.get('type') in {'AGG','VO','EVT'} and not d.get('bounded_context_id'):issues.append('bounded_context_id requerido para AGG/VO/EVT')
 if d.get('type')=='FDT':
  for k in ('service_id','bounded_context_id','pack','skill'):
   if not d.get(k):issues.append(f'{k} requerido para FDT')
 if d.get('type') in {'RCP','US','EPC'}:
  for k in ('pack','skill'):
   if not d.get(k):issues.append(f'{k} requerido por el pack productor Requirements Engineering')
 if d.get('type')=='US':
  prod=d.get('product');ident=d.get('id')
  if prod is not None and not (isinstance(prod,str) and US_PRODUCT.fullmatch(prod)):issues.append('product de US, si se informa, debe ser un código en MAYÚSCULAS (p. ej. CL2 o CL2-BAS); es metadato, no prefijo del ID')
  if not isinstance(ident,str) or not re.fullmatch(r'RCP-\d{3,}-US-\d{3,}',ident):issues.append(f'id de US debe ser RCP-NNN-US-NNN (p. ej. RCP-002-US-001); se encontró {ident!r}. Un ID previo (HU-NN-NN, US-001, CL2-US-014) va en legacy_id')
 if d.get('type')=='EPC':
  ident=d.get('id');rel=d.get('related')
  if not isinstance(ident,str) or not re.fullmatch(r'RCP-\d{3,}-EPC-\d{3,}',ident):issues.append(f'id de EPC debe ser RCP-NNN-EPC-NNN (p. ej. RCP-002-EPC-001); se encontró {ident!r}')
  if not isinstance(rel,list) or not rel:issues.append('EPC requiere related con los IDs de las US que agrupa')
 if not s[m.end():].strip():issues.append('Cuerpo Markdown vacío')
 if publication and d.get('status')=='stable' and 'verified' not in d:issues.append('status stable no sustituye evidencia de revisión; revisar gate externo')
 return issues

def main():
 a=argparse.ArgumentParser();a.add_argument('files',nargs='+');a.add_argument('--publication',action='store_true');args=a.parse_args();bad=False
 for f in args.files:
  issues=validate(f,args.publication)
  print(f'{f}: '+('OK (perfil documental; no aprobación humana)' if not issues else 'NO CONFORME'))
  for e in issues:print('  - '+e)
  bad|=bool(issues)
 return int(bad)
if __name__=='__main__':sys.exit(main())
