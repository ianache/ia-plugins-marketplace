#!/usr/bin/env python3
from pathlib import Path
import json,sys
root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'.claude-plugin/plugin.json').read_text())
assert manifest['name']=='ux-ui-design'
required=['SKILL.md','references/contract.md','references/technical-guidance.md','references/gate-checklist.md','templates/deliverable.md','templates/gate-evidence.json','scripts/validate.py','examples/README.md','assets/README.md']
skills=list((root/'skills').iterdir())
assert len(skills)==7, f'Esperados 7 skills: {len(skills)}'
for skill in skills:
 for rel in required: assert (skill/rel).is_file(),f'{skill.name}/{rel}'
 text=(skill/'SKILL.md').read_text()
 assert text.startswith('---\n') and f'name: {skill.name}' in text
print(f'OK: {len(skills)} skills con recursos y manifest Claude')
