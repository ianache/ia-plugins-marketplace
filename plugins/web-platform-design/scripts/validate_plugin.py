#!/usr/bin/env python3
import json,pathlib,re,subprocess,sys
r=pathlib.Path(__file__).resolve().parents[1]
p=json.loads((r/'.claude-plugin/plugin.json').read_text())
import re
assert p['name']=='web-platform-design' and re.fullmatch(r'\d+\.\d+\.\d+',p['version'])  # la versión vigente es la de plugin.json (SemVer)
ss=list((r/'skills').glob('*/SKILL.md'));assert len(ss)==7
for f in ss:
 t=f.read_text();m=re.match(r'\A---\n(.*?)\n---\n',t,re.S);assert m,f
 assert re.search(r'^name:\s*'+re.escape(f.parent.name)+r'\s*$',m.group(1),re.M),f
 assert re.search(r'^description:\s*\S+',m.group(1),re.M),f
 subprocess.run([sys.executable,str(f.parent/'scripts/validate_resources.py')],check=True)
print('OK Claude plugin '+p['version']+': 7 skills and complete resource sets')
