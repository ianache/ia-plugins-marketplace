#!/usr/bin/env python3
"""Conservative FDT structural validator. Semantic accuracy requires human review."""
import pathlib,sys,argparse,yaml
from okf_validate import validate as okf_validate
REQUIRED_SECTIONS=['Propósito y alcance','Trazabilidad','Contratos','Modelo de dominio','Modelo de datos','Interacciones','Secuencia','Seguridad','Consistencia','Resiliencia','Observabilidad','Pruebas','Construcción','Validación']
def validate_fdt(path):
    errors=okf_validate(path,'profile')
    text=path.read_text(encoding='utf-8')
    meta=yaml.safe_load(text[4:].split('\n---\n',1)[0]) if text.startswith('---\n') and '\n---\n' in text[4:] else {}
    if meta.get('type')!='FDT':errors.append('type must be FDT')
    for key in ('service_id','bounded_context_id','pack','skill'):
        if not meta.get(key):errors.append('missing '+key)
    for section in REQUIRED_SECTIONS:
        if '## '+section not in text:errors.append('missing section '+section)
    if 'sequenceDiagram' not in text and 'SEQ-' not in text:errors.append('missing sequence diagram or SEQ reference')
    return errors

def validate_manifest(path):
    if not path.is_file():return ['missing FDT manifest']
    data=yaml.safe_load(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or not isinstance(data.get('functionalities'),list) or not data['functionalities']:return ['manifest requires nonempty functionalities']
    errors=[]; seen=set()
    for entry in data['functionalities']:
        if not isinstance(entry,dict) or not entry.get('id') or not entry.get('file'):errors.append('invalid manifest entry');continue
        if entry['id'] in seen:errors.append('duplicate FDT ID '+entry['id'])
        seen.add(entry['id'])
        p=(path.parent/entry['file']).resolve()
        if not p.is_relative_to(path.parent.resolve()):errors.append('unsafe FDT path');continue
        if not p.is_file():errors.append('missing '+str(p));continue
        errors.extend(entry['id']+': '+e for e in validate_fdt(p))
        if entry.get('status') not in ('reviewed','approved'):errors.append(entry['id']+': manifest status must be reviewed/approved')
    return errors
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('file');ap.add_argument('--manifest',action='store_true');a=ap.parse_args()
    issues=validate_manifest(pathlib.Path(a.file)) if a.manifest else validate_fdt(pathlib.Path(a.file))
    if issues:
        for e in issues:print('ERROR:',e)
        sys.exit(2)
    print('FDT structurally valid; semantic/approval checks not performed')
