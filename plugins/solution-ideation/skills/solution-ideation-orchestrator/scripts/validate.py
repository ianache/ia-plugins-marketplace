#!/usr/bin/env python3
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
if len(sys.argv)<2:
 print('Uso: python scripts/validate.py documento.md [--publication]');sys.exit(2)
sys.exit(subprocess.call([sys.executable,str(ROOT/'scripts/validate_okf.py'),*sys.argv[1:]]))
