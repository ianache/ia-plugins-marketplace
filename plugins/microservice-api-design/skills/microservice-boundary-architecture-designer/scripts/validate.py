#!/usr/bin/env python3
from pathlib import Path
import argparse,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--workspace',required=True);p.add_argument('--type',required=True);p.add_argument('--file',required=True);a=p.parse_args()
root=Path(__file__).resolve().parents[3]
sys.exit(subprocess.call([sys.executable,str(root/'scripts/validate_pathmap.py'),'--workspace',a.workspace,'--type',a.type,'--file',a.file,'--check']))
