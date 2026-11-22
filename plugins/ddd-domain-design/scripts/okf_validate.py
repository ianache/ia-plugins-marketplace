#!/usr/bin/env python3
"""STD-OKF-001 v0.1.0-stable validator. Profile checks are deterministic; publication checks are conservative."""
import argparse,datetime,pathlib,re,sys
import yaml
APPROVED=set('ACP ADH ADR AGG API ASIS ASR AT BC BCAP BCP BIC BIQ BO BR BSN C4 CFR CHG CLS CMP CTLG CTX DBM DBR DDR DMD DSH DSM DSP ENT EPC EPS ERR EVD EVT EXEC FDT FLW GOV HCB HOF IAC IAR IBL ICM ICP IDP IDS IFO IGR IHO IIA IMD IMP IOB IRB IRL IRP IRQ ISA ISD ITA ITP IXL IXP KPI LDM MOB PCH PDM QAR QDC QER QFA QQI QTD QTE QTP QTR QTS RCP RMP RSK RUN SCR SEQ SOL SSP STD STK STR SVC TC TDA TDR TKN TRM TSN UAP UCB UCM UCX UOW US UWR UXR VO WEB'.split())
PROPOSED=set()  # STD-OKF-001 v0.1.0-stable aprueba todos los tipos; se conserva la rama por compatibilidad
REQUIRED='type id title description version status owner classification tags generated sources'.split()
SEMVER=re.compile(r'^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$')
ACTOR=re.compile(r'^(human:[^\s/]+|process:[^\s/]+|[^\s/]+/\d+\.\d+\.\d+(?:-[\w.-]+)?)$')
DATE=re.compile(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$')
def validate(path,level='profile',run=None):
 errors=[]; text=path.read_text(encoding='utf-8'); name=path.name
 if name in ('index.md','log.md'):
  if name=='log.md': return ['log.md reserved: requires separate OKF validation rules'] if level=='publish' else []
  if level=='publish': return ['index.md reserved: requires separate OKF validation rules']
  return []
 if not text.startswith('---\n') or '\n---\n' not in text[4:]:return ['Missing YAML frontmatter']
 front,body=text[4:].split('\n---\n',1)
 try: meta=yaml.safe_load(front)
 except yaml.YAMLError as ex:return ['Invalid YAML: '+str(ex)]
 if not isinstance(meta,dict):return ['Frontmatter must be a map']
 if not isinstance(meta.get('type'),str) or not meta['type'].strip():errors.append('type must be a nonempty string')
 if 'okf_version' in meta:errors.append('okf_version only allowed in root index.md')
 if level=='okf':return errors
 for k in REQUIRED:
  if k not in meta:errors.append('Missing '+k)
 for k in ('artifact_type','source_refs','reviewed_by','lifecycle_status'):
  if k in meta:errors.append('Forbidden alias '+k)
 if meta.get('type') in PROPOSED:
  if level=='publish':errors.append('Proposed type pending approval (STD-OKF-001 v0.1.0-stable): '+str(meta.get('type')))
 elif meta.get('type') not in APPROVED:errors.append('Unregistered type (corporate catalog): '+str(meta.get('type')))
 for k in ('id','title','description','owner'):
  if not isinstance(meta.get(k),str) or not meta[k].strip():errors.append(k+' must be nonempty string')
 rawver=re.search(r'(?m)^version:\s*(.+?)\s*$',front)
 if rawver and not (rawver.group(1).startswith('"') and rawver.group(1).endswith('"')):errors.append('version must be quoted')
 if not isinstance(meta.get('version'),str) or not SEMVER.fullmatch(meta['version']):errors.append('version must be SemVer string')
 if meta.get('status') not in ('draft','stable','deprecated'):errors.append('invalid status')
 if meta.get('classification') not in ('public','internal','confidential','restricted'):errors.append('invalid classification')
 tags=meta.get('tags')
 if not isinstance(tags,list) or any(not isinstance(t,str) or t!=t.lower() for t in tags) or (isinstance(tags,list) and len(tags)!=len(set(map(str,tags)))):errors.append('tags must be lowercase unique strings')
 g=meta.get('generated')
 if not isinstance(g,dict):errors.append('generated must be map')
 else:
  if not isinstance(g.get('by'),str) or not ACTOR.fullmatch(g['by']):errors.append('invalid generated.by')
  if not isinstance(g.get('at'),str) or not DATE.fullmatch(g['at']):errors.append('generated.at must be quoted ISO 8601 with zone')
 sources=meta.get('sources')
 if not isinstance(sources,list):errors.append('sources must be list')
 elif sources:
  for i,s in enumerate(sources):
   if not isinstance(s,dict) or not isinstance(s.get('resource'),str) or not s['resource'].strip():errors.append('sources['+str(i)+'].resource required')
 elif 'creación original' not in body.lower() and 'creacion original' not in body.lower():errors.append('sources: [] requires original-creation justification in body')
 if meta.get('type') in ('AGG','VO','EVT'):
  for k in ('bounded_context_id','pack','skill'):
   if not isinstance(meta.get(k),str) or not meta[k].strip():errors.append(k+' required for DDD artifact')
 for k in ('product','bounded_context_id','service_id','schema_id','pack','skill','resource'):
  if k in meta and (not isinstance(meta[k],str) or not meta[k].strip()):errors.append(k+' must be nonempty string')
 for k in ('related','supersedes'):
  if k in meta and (not isinstance(meta[k],list) or not all(isinstance(v,str) for v in meta[k])):errors.append(k+' must be list of IDs')
 for v in meta.get('related',[]) if isinstance(meta.get('related',[]),list) else []:
  if isinstance(v,str) and not re.search(r'\[[^\]]+\]\([^)]*'+re.escape(v)+r'[^)]*\)',body):errors.append('related '+v+' missing Markdown link')
 if 'verified' in meta:
  if not isinstance(meta['verified'],list):errors.append('verified must be list')
  else:
   for x in meta['verified']:
    if not isinstance(x,dict) or not x.get('by') or not x.get('at'):errors.append('verified entries require by and at')
 if level=='publish':
  if not sources:errors.append('publication requires provenance sources')
  if run is None:errors.append('publication requires --run for gate evidence')
  else:
   gr=run/'gate-register.yaml'
   if not gr.exists():errors.append('missing gate-register.yaml')
   else:
    gates=yaml.safe_load(gr.read_text()).get('gates',[])
    if not gates or any(g.get('status')!='APPROVED' or not g.get('approver') or not g.get('evidence') for g in gates):errors.append('all required gates need approved status, approver and evidence')
  if '```mermaid' in body and not re.search(r'```mermaid\s*\n(?:flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|C4Context|C4Container)',body):errors.append('Mermaid block syntax not recognized; render verification required')
  if not isinstance(meta.get('verified'),list) or not meta.get('verified'):errors.append('publication requires actual review evidence in verified')
 return errors
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('files',nargs='+',type=pathlib.Path);p.add_argument('--level',choices=['okf','profile','publish'],default='profile');p.add_argument('--run',type=pathlib.Path);a=p.parse_args();bad=False
 for f in a.files:
  issues=validate(f,a.level,a.run);print(f, 'PASS' if not issues else 'FAIL');[print(' -',e) for e in issues];bad|=bool(issues)
 sys.exit(1 if bad else 0)
