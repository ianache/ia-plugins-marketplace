#!/usr/bin/env python3
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'scripts'))
from validate_pathmap import verify
if __name__=='__main__':
 if len(sys.argv)!=4: raise SystemExit('usage: validate.py <workspace> <kind> <output-path>')
 print(verify(*sys.argv[1:]))
