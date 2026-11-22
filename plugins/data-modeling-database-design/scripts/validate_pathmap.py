#!/usr/bin/env python3
"""Validate a typed skill output against the Data Modeling pathmap."""
import argparse
import json
import pathlib
import re
import sys

PM = json.loads((pathlib.Path(__file__).resolve().parents[1] / 'assets' / 'pathmap.json').read_text(encoding='utf-8'))

def _frontmatter(text):
    match = re.match(r"\A---\s*\n(.*?)\n---\s*\n", text, re.S)
    return match.group(1) if match else None

def _expected_dir(workspace, run_id, document_type):
    root = pathlib.Path(workspace).resolve() / PM['deliverable_root'].format(run_id=run_id).strip('/')
    return (root / PM['document_types'][document_type].strip('/')).resolve()

def validate(workspace, run_id, path, document_type=None):
    workspace = pathlib.Path(workspace).resolve()
    path = pathlib.Path(path)
    path = (workspace / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(workspace):
        return False, 'La ruta sale del workspace'
    if not document_type:
        return False, 'Falta --type para una salida de skill; BLOCKED'
    if document_type not in PM['document_types']:
        return False, 'Tipo sin mapeo; BLOCKED'
    if path.parent != _expected_dir(workspace, run_id, document_type):
        return False, f'Directorio incorrecto: esperado {_expected_dir(workspace, run_id, document_type)}'
    if not path.is_file():
        return False, 'Archivo no existe'
    frontmatter = _frontmatter(path.read_text(encoding='utf-8'))
    if frontmatter is None:
        return False, 'Falta frontmatter YAML'
    found = re.search(r"(?m)^type:\s*['\"]?([A-Za-z0-9_-]+)", frontmatter)
    if not found or found.group(1) != document_type:
        return False, 'type OKF distinto del contrato'
    return True, 'Ruta y type conformes (validar OKF completo por separado)'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', default='.')
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--file', required=True)
    parser.add_argument('--type', required=True)
    args = parser.parse_args()
    valid, message = validate(args.workspace, args.run_id, args.file, args.type)
    print(json.dumps({'valid': valid, 'message': message}, ensure_ascii=False))
    return 0 if valid else 1

if __name__ == '__main__':
    sys.exit(main())
