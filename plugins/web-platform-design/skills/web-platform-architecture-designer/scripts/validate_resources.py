#!/usr/bin/env python3
from pathlib import Path
import json,sys
p=Path(__file__).resolve().parents[1]
required=['SKILL.md','references/contract.md','references/gate-checklist.md','references/technical-guidance.md','templates/deliverable.md','templates/deliverable-specific.md','templates/gate-evidence.json','scripts/validate.py','examples/sample-input.json','examples/sample-output.json','assets/diagram-conventions.md']
missing=[x for x in required if not (p/x).is_file()]
for x in ('templates/gate-evidence.json','examples/sample-input.json','examples/sample-output.json'):json.loads((p/x).read_text())
if missing:sys.exit('Missing: '+', '.join(missing))
print('OK',p.name)
