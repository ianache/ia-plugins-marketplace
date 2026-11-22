#!/usr/bin/env python3
"""Validate output paths against Architecture Design pathmap v1.2.0."""
import argparse, pathlib, sys
MAP={k:v.rstrip('/') for k,v in __import__('json').loads((__import__('pathlib').Path(__file__).resolve().parents[1]/'assets'/'pathmap.json').read_text(encoding='utf-8'))['document_types'].items()}  # fuente unica: assets/pathmap.json
def validate(workspace, document_type, destination, override=False, explicit_instruction=None):
    root=pathlib.Path(workspace).resolve()
    target=pathlib.Path(destination)
    if not target.is_absolute(): target=root/target
    target=target.resolve()
    if not target.is_relative_to(root):
        raise ValueError('Output outside workspace is not allowed by this validator')
    if override:
        if not explicit_instruction or not explicit_instruction.strip():
            raise ValueError('Override requires a recorded explicit user instruction')
        return True
    dtype=document_type.upper()
    if dtype not in MAP: raise ValueError(f'Unmapped document type: {dtype}')
    expected=(root/MAP[dtype]).resolve()
    if target.parent != expected: raise ValueError(f'Wrong destination for {dtype}: {target.parent}; expected {expected}')
    return True

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--workspace',default='.');ap.add_argument('--type',required=True);ap.add_argument('--output',required=True);ap.add_argument('--explicit-override',action='store_true');ap.add_argument('--user-instruction');a=ap.parse_args()
    try: validate(a.workspace,a.type,a.output,a.explicit_override,a.user_instruction)
    except ValueError as e: print('FAIL:',e,file=sys.stderr);sys.exit(1)
    print('PASS')
