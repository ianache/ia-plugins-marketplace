#!/usr/bin/env python3
"""Valida rutas, nombres y consistencia de índices de los entregables de Project Management, sin aprobar su contenido."""
import argparse,json,pathlib,re,sys
MAP={k:v.rstrip('/') for k,v in __import__('json').loads((__import__('pathlib').Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'))['document_types'].items()}  # fuente unica: assets/pathmap.json
def _fm(text):
    m=re.match(r"\A---\s*\n(.*?)\n---\s*\n",text,re.S)
    return m.group(1) if m else None
def validate(workspace, document_type, path, override=None):
    workspace=pathlib.Path(workspace).resolve()
    actual=pathlib.Path(path)
    actual=(workspace/actual).resolve() if not actual.is_absolute() else actual.resolve()
    if not actual.is_relative_to(workspace):return False,"La ruta sale del workspace"
    if override:
        target=pathlib.Path(override)
        target=(workspace/target).resolve() if not target.is_absolute() else target.resolve()
        if target.parent!=actual.parent:return False,"La ruta no coincide con override explícito"
    else:
        if document_type not in MAP:return False,"Tipo sin mapeo; BLOCKED"
        target=(workspace/MAP[document_type]).resolve()
        if actual.parent!=target:return False,f"Directorio incorrecto: esperado {target}"
    if not actual.is_file():return False,"Archivo no existe"
    fm=_fm(actual.read_text(encoding="utf-8"))
    if fm is None:return False,"Falta frontmatter YAML"
    found=re.search(r"(?m)^type:\s*['\"]?([A-Za-z0-9_-]+)",fm)
    if not found or found.group(1)!=document_type:return False,"type OKF distinto del contrato"
    ident=re.search(r"(?m)^id:\s*['\"]?([A-Za-z0-9_-]+)",fm)
    if not ident or not actual.name.startswith(ident.group(1)):return False,"El nombre del archivo debe comenzar con el id del frontmatter"
    return True,"Ruta, type e id conformes (validar OKF completo por separado)"
def main():
    p=argparse.ArgumentParser();p.add_argument("--workspace",default=".");p.add_argument("--type",required=True);p.add_argument("--file",required=True);p.add_argument("--override");a=p.parse_args()
    ok,msg=validate(a.workspace,a.type,a.file,a.override)
    print(json.dumps({"valid":ok,"message":msg},ensure_ascii=False));return 0 if ok else 1
if __name__=="__main__":sys.exit(main())
