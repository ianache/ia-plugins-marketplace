#!/usr/bin/env python3
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
from validate_okf import main as validate_okf_main
from validate_adr_body import main as validate_adr_body_main
if __name__=='__main__':
    argv=sys.argv[1:]
    raise SystemExit(max(validate_okf_main(argv), validate_adr_body_main(argv)))
