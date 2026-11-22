#!/usr/bin/env python3
"""Resolve and verify output destinations. No network calls."""
import argparse,difflib,json,pathlib,re,sys
MAP=pathlib.Path(__file__).resolve().parents[1]/'assets/pathmap.json'
def load_map(): return json.loads(MAP.read_text(encoding='utf-8'))
SERVICE_RE=re.compile(r'[a-z0-9][a-z0-9._-]*')
def resolve(workspace,document_type,filename,service=None,codebase_service=None):
    data=load_map(); dirs=data['document_types']
    if document_type not in dirs: raise ValueError('Unmapped document type: '+document_type)
    template=dirs[document_type]
    if '{service}' in template:
        if not service or not SERVICE_RE.fullmatch(service): raise ValueError('Service id required (lowercase letters, digits, . _ -) for type '+document_type)
        template=template.replace('{service}',service)
    root=pathlib.Path(workspace).resolve()
    if '{codebase_service}' in template:
        name=codebase_service or service
        if not name or not SERVICE_RE.fullmatch(name): raise ValueError('Service id required for type '+document_type)
        if not (root/'codebase'/name).is_dir(): raise ValueError(f"No existe codebase/{name}. Pida al humano la ruta del servicio dentro de codebase/.")
        template=template.replace('{codebase_service}',name)
    target=(root/template/filename).resolve()
    if not target.is_relative_to(root): raise ValueError('Path escapes workspace')
    return target
def resolve_openapi(workspace,service,codebase_service=None):
    # OpenAPI en el codebase del servicio; si no existe la carpeta, el humano debe indicar la ruta
    if not service or not SERVICE_RE.fullmatch(service): raise ValueError('Service id required')
    cfg=load_map()['openapi']; root=pathlib.Path(workspace).resolve(); name=codebase_service or service
    base=root/'codebase'/name
    if not base.is_dir():
        cands=sorted(d.name for d in (root/'codebase').iterdir() if d.is_dir()) if (root/'codebase').is_dir() else []
        near=difflib.get_close_matches(name,cands,n=3,cutoff=0.5)
        raise ValueError(f"No existe codebase/{name}. Pida al humano la ruta del servicio dentro de codebase/ (--codebase-service <carpeta>)."+(f" Similares: {', '.join(near)}." if near else ''))
    rel=cfg['alternative'] if (root/cfg['alternative_when_exists'].replace('{service}',name)).is_dir() else cfg['primary']
    target=(root/rel.replace('{service}',name)).resolve()
    if not target.is_relative_to(root): raise ValueError('Path escapes workspace')
    return target
def validate(workspace,document_type,path,service=None,codebase_service=None):
    path=pathlib.Path(path).resolve(); template=load_map()['document_types'].get(document_type,'')
    if service is None and '{service}' in template:
        # inferir <servicio> de la ruta: design/microservices/<servicio>/...
        rel=template.strip('./').split('/'); i=rel.index('{service}')
        parts=path.relative_to(pathlib.Path(workspace).resolve()).parts if path.is_relative_to(pathlib.Path(workspace).resolve()) else ()
        service=parts[i] if len(parts)>i else None
    if codebase_service is None and '{codebase_service}' in template and service is None:
        rel=template.strip('./').split('/'); i=rel.index('{codebase_service}'); ws=pathlib.Path(workspace).resolve()
        parts=path.relative_to(ws).parts if path.is_relative_to(ws) else ()
        codebase_service=parts[i] if len(parts)>i else None
    expected=resolve(workspace,document_type,path.name,service,codebase_service)
    if path!=expected: raise ValueError(f'Incorrect path: {path}; expected: {expected}')
    return True
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--workspace',required=True);a.add_argument('--type',required=True);a.add_argument('--file',required=True);a.add_argument('--service');a.add_argument('--check',action='store_true');x=a.parse_args()
    try:
        if x.check: validate(x.workspace,x.type,x.file,x.service);print('OK')
        else: print(resolve(x.workspace,x.type,x.file,x.service))
    except ValueError as e: print(str(e),file=sys.stderr);sys.exit(2)
