#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_okf import main
if __name__=='__main__': raise SystemExit(main(sys.argv[1:]))
