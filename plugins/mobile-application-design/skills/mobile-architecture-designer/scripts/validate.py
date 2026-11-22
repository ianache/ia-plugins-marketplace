#!/usr/bin/env python3
"""Chequeo básico de frontmatter y headings; NO equivale a validación OKF completa."""
import sys
from pathlib import Path
REQUIRED=['type:','id:','title:','description:','version:','status:','owner:','classification:','tags:','generated:','sources:','pack:','skill:']
def validate(p):
    s=Path(p).read_text(encoding='utf-8')
    if not s.startswith('---\n') or '\n---\n' not in s[4:]: return ['frontmatter YAML ausente']
    fm=s.split('---',2)[1]
    return [f'falta {k}' for k in REQUIRED if not any(line.startswith(k) for line in fm.splitlines())]
if __name__=='__main__':
    if len(sys.argv)!=2: sys.exit('Uso: python validate.py <artefacto.md>')
    errors=validate(sys.argv[1]); print('\n'.join(errors) if errors else 'OK estructura mínima'); sys.exit(bool(errors))
