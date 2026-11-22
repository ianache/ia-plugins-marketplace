import sys,unittest,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from validate_okf import validate
class TestOKF(unittest.TestCase):
 def make(self,text):
  f=tempfile.NamedTemporaryFile(mode='w',suffix='.md',delete=False);f.write(text);f.close();self.addCleanup(lambda:Path(f.name).unlink(missing_ok=True));return f.name
 def test_valid(self):
  doc="""---
type: US
id: RCP-002-US-001
title: Historia
version: '1.0.0'
description: Historia de prueba
status: draft
owner: team:requirements
classification: internal
tags: [requirements]
product: CL2
pack: requirements-engineering
skill: af-user-story-designer
generated:
  by: af-user-story-designer/1.1.0
  at: '2026-10-22T21:00:00-05:00'
sources:
  - resource: requirements/input.md
---
# Historia
"""
  self.assertEqual([],validate(self.make(doc)))
 def test_invalid(self):
  self.assertTrue(validate(self.make('---\ntype: US\n---\n# Hola')))
 def test_unapproved(self):
  self.assertTrue(any('no aprobado' in x for x in validate(self.make('---\ntype: ZZZ\n---\n# Hola'),True)))
if __name__=='__main__':unittest.main()
