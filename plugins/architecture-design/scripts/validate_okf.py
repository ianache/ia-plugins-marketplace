#!/usr/bin/env python3
"""Structural corporate OKF frontmatter validator. Does not assert semantic truth or human approval."""
import sys,re,datetime,argparse
from pathlib import Path
import yaml
APPROVED=set('ACP ADH ADR AGG API ASIS ASR AT BC BCAP BCP BIC BIQ BO BR BSN C4 CFR CHG CLS CMP CTLG CTX DBM DBR DDR DMD DSH DSM DSP ENT EPC EPS ERR EVD EVT EXEC FDT FLW GOV HCB HOF IAC IAR IBL ICM ICP IDP IDS IFO IGR IHO IIA IMD IMP IOB IRB IRL IRP IRQ ISA ISD ITA ITP IXL IXP KPI LDM MOB PCH PDM QAR QDC QER QFA QQI QTD QTE QTP QTR QTS RCP RMP RSK RUN SCR SEQ SOL SSP STD STK STR SVC TC TDA TDR TKN TRM TSN UAP UCB UCM UCX UOW US UWR UXR VO WEB'.split())
PROPOSED=set()  # STD-OKF-001 v1.11.0-stable aprueba todos los tipos; se conserva la rama por compatibilidad
REQUIRED=('type','id','title','description','version','status','owner','classification','tags','generated','sources')
def validate(path,allow_draft_types=False):
 p=Path(path);errors=[]
 if p.name in ('index.md','log.md'): return ['reserved OKF file: use dedicated rules']
 s=p.read_text(encoding='utf-8')
 m=re.match(r'\A---\s*\n(.*?)\n---\s*(?:\n|$)',s,re.S)
 if not m:return ['missing YAML frontmatter']
 try:d=yaml.safe_load(m.group(1))
 except yaml.YAMLError as e:return [f'invalid YAML: {e}']
 if not isinstance(d,dict):return ['frontmatter must be a mapping']
 for k in REQUIRED:
  if k not in d:errors.append(f'missing {k}')
 for k in ('type','id','title','description','version','owner','classification'):
  if k in d and (not isinstance(d[k],str) or not d[k].strip()):errors.append(f'invalid {k}')
 if d.get('type') not in APPROVED and not (allow_draft_types and d.get('type') in PROPOSED):errors.append('unapproved type')
 if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?',str(d.get('version',''))):errors.append('invalid SemVer')
 if d.get('status') not in ('draft','stable','deprecated'):errors.append('invalid status')
 if d.get('classification') not in ('public','internal','confidential','restricted'):errors.append('invalid classification')
 tags=d.get('tags');
 if not isinstance(tags,list) or any(not isinstance(t,str) or t!=t.lower() for t in tags) or len(set(map(str,tags)))!=len(tags):errors.append('invalid tags')
 g=d.get('generated')
 if not isinstance(g,dict) or not isinstance(g.get('by'),str) or not g.get('by'):errors.append('invalid generated.by')
 if not isinstance(g,dict) or not isinstance(g.get('at'),(str,datetime.datetime)):errors.append('invalid generated.at')
 else:
  try:
   dt=datetime.datetime.fromisoformat(str(g['at']).replace('Z','+00:00'))
   if dt.tzinfo is None:errors.append('generated.at requires timezone')
  except ValueError:errors.append('invalid generated.at ISO8601')
 src=d.get('sources')
 if not isinstance(src,list):errors.append('sources must be a list')
 else:
  for i,x in enumerate(src):
   if not isinstance(x,dict) or not isinstance(x.get('resource'),str) or not x.get('resource'):errors.append(f'sources[{i}].resource required')
 if 'verified' in d and (not isinstance(d['verified'],list) or any(not isinstance(v,dict) or 'by' not in v or 'at' not in v for v in d['verified'])):errors.append('invalid verified evidence')
 for alias in ('artifact_type','source_refs','reviewed_by','lifecycle_status'):
  if alias in d:errors.append(f'disallowed alias {alias}')
 if d.get('type') in ('AGG','VO','EVT') and not d.get('bounded_context_id'):errors.append('bounded_context_id required')
 if d.get('type')=='FDT' and any(not d.get(k) for k in ('service_id','bounded_context_id','pack','skill')):errors.append('FDT requires service_id,bounded_context_id,pack,skill')
 return errors
def main(argv=None):
 a=argparse.ArgumentParser();a.add_argument('paths',nargs='+');a.add_argument('--allow-draft-types',action='store_true');v=a.parse_args(argv)
 failures=0
 for path in v.paths:
  errors=validate(path,v.allow_draft_types)
  print(f'{path}: '+ ('PASS' if not errors else 'FAIL: '+'; '.join(errors)))
  failures+=bool(errors)
 return int(failures>0)
if __name__=='__main__':sys.exit(main())
