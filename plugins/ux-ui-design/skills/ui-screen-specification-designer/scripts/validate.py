#!/usr/bin/env python3
"""Validador estructural de frontmatter OKF corporativo; no certifica semántica ni aprobación."""
from pathlib import Path
import sys,re
try:
 import yaml
except ImportError:
 print('Falta PyYAML: python -m pip install PyYAML',file=sys.stderr);sys.exit(2)
REQUIRED={'type','id','title','description','version','status','owner','classification','tags','generated','sources'}
def validate(path):
 text=Path(path).read_text(encoding='utf-8')
 if not text.startswith('---\n') or '\n---\n' not in text[4:]:return ['Frontmatter YAML ausente']
 front=text.split('---',2)[1]
 try: data=yaml.safe_load(front)
 except yaml.YAMLError as exc:return [str(exc)]
 if not isinstance(data,dict):return ['Frontmatter no es mapa']
 errs=[f'Falta {x}' for x in sorted(REQUIRED-set(data))]
 if data.get('status') not in {'draft','stable','deprecated'}:errs.append('status inválido')
 if data.get('classification') not in {'public','internal','confidential','restricted'}:errs.append('classification inválido')
 if not re.fullmatch(r'\d+\.\d+\.\d+',str(data.get('version',''))):errs.append('version no SemVer')
 if not isinstance(data.get('generated'),dict) or not all(data['generated'].get(k) for k in ('by','at')):errs.append('generated.by/at requeridos')
 if not isinstance(data.get('sources'),list):errs.append('sources debe ser lista')
 elif any(not isinstance(s,dict) or not s.get('resource') for s in data['sources']):errs.append('source sin resource')
 return errs
if __name__=='__main__':
 if len(sys.argv)!=2:print('Uso: validate.py archivo.md');sys.exit(2)
 errors=validate(sys.argv[1]);print('\n'.join(errors) if errors else 'OK estructural');sys.exit(bool(errors))
