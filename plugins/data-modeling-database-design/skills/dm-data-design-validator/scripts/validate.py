#!/usr/bin/env python3
"""Validación STD-OKF-001 v1.3.0 (delegada en scripts/validate_okf.py de la raíz del plugin)."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from validate_okf import main
if __name__ == '__main__':
    sys.exit(main())
