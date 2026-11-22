#!/usr/bin/env python3
"""Validación estática mínima: no valida semántica, OKF completo ni aprobaciones."""
import argparse,pathlib,sys
p=argparse.ArgumentParser();p.add_argument('file');a=p.parse_args();f=pathlib.Path(a.file)
if not f.is_file():sys.exit('ERROR: archivo inexistente')
s=f.read_text(encoding='utf-8');required=['type:','id:','title:','description:','version:','status:','owner:','classification:','tags:','generated:','sources:','pack:','skill:']
if not s.startswith('---\n') or s.count('---\n')<2:sys.exit('ERROR: frontmatter faltante')
header=s.split('---',2)[1];missing=[k for k in required if k not in header]
if missing:sys.exit('ERROR: campos ausentes '+', '.join(missing))
print('OK: estructura mínima; requiere revisión humana y validación OKF completa')
