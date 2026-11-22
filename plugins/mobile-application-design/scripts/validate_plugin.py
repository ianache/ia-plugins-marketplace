#!/usr/bin/env python3
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
p=json.loads((root/'.claude-plugin/plugin.json').read_text())
assert p['name']=='mobile-application-design'
skills=list((root/'skills').glob('*/SKILL.md'))
assert len(skills)==7, len(skills)
for f in skills:
    s=f.read_text();assert s.startswith('---\n') and 'name: '+f.parent.name in s
    for rel in ['references/contract.md','references/gate-checklist.md','references/technical-guidance.md','templates/deliverable.md','templates/gate-evidence.json','scripts/validate.py','examples/README.md','assets/README.md']:
        assert (f.parent/rel).is_file(),str(f.parent/rel)
print('OK: plugin manifest, 7 skills, resources')
