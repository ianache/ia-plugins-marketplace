#!/usr/bin/env python3
"""Asignación y verificación de IDs de User Stories (delegada en scripts/us_ids.py de la raíz del plugin)."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from us_ids import main
if __name__ == '__main__':
    sys.exit(main())
