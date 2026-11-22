#!/usr/bin/env python3
"""Resolve and validate DDD output locations from the workspace root."""
import argparse, json, pathlib, sys
MAP=pathlib.Path(__file__).resolve().parents[1]/'assets'/'pathmap.json'
def data(): return json.loads(MAP.read_text(encoding='utf-8'))
def relative(kind):
 d=data(); out=d['document_types'].get(kind) or d['auxiliary'].get(kind)
 if not out: raise ValueError('Unmapped document type/output: '+kind)
 return pathlib.Path(out)
def resolve(workspace,kind,filename):
 base=pathlib.Path(workspace).resolve(); name=pathlib.Path(filename)
 if name.name!=filename or filename in ('.','..'): raise ValueError('filename must be basename')
 p=(base/relative(kind)/filename).resolve()
 if not p.is_relative_to(base): raise ValueError('outside workspace')
 return p
def verify(workspace,kind,path):
 p=pathlib.Path(path).resolve(); expected=(pathlib.Path(workspace).resolve()/relative(kind)).resolve()
 if p.parent!=expected: raise ValueError('wrong output directory: '+str(p)+' expected '+str(expected))
 if not p.is_file() or p.stat().st_size==0: raise ValueError('output missing or empty: '+str(p))
 expected_type=data().get('typed_outputs',{}).get(kind)
 if expected_type:
  import re
  fm=re.match(r'\A---\s*\n(.*?)\n---\s*\n',p.read_text(encoding='utf-8'),re.S)
  if not fm or not re.search(r'(?m)^type:\s*[\"\']?'+re.escape(expected_type)+r'\b',fm.group(1)):
   raise ValueError('OKF type mismatch: expected '+expected_type)
 return p
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('action',choices=['resolve','verify']);a.add_argument('--workspace',required=True);a.add_argument('--kind',required=True);a.add_argument('--file',required=True);x=a.parse_args()
 try:
  print(resolve(x.workspace,x.kind,x.file) if x.action=='resolve' else verify(x.workspace,x.kind,x.file))
 except ValueError as e: print('ERROR:',e,file=sys.stderr);sys.exit(2)
