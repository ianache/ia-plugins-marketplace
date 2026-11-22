# Validation v1.0.0
- [x] Static plugin layout and seven SKILL.md entries
- [x] DAG cycle, missing dependency, skill and gate checks
- [x] Ledger transitions, evidence and gate prerequisites
- [x] Structural DDD contract validation
- [x] Plantillas BC, CTX, ACP (descubrimiento) y CTLG (catálogo BC) con frontmatter de perfil corporativo y tipo correcto (tests/test_templates.py)
- [x] Plantillas AGG, VO, CTLG (catálogo AGG y EVT), EVT y CFR con tipo correcto y referenciadas por sus skills (tests/test_templates.py)
- [ ] Real Claude Code invocation (requires user environment)
- [ ] Enterprise OKF v0.2 schema validation against official profile
- [ ] GitLab protected approvals / multiuser concurrency
- [ ] Semantic DDD quality and CL2 DSP-001 case review


## STD-OKF-001 v1.9.0-stable
El script `scripts/okf_validate.py` aplica validaciones estructurales y corporativas; no sustituye revisión humana ni pruebas de render Mermaid. Los ejemplos son sintéticos y no demuestran aprobación del DSP.


Actualización v0.4.0: catálogo AGG/VO/EVT aprobado; plantillas y validación de tipos DDD incluidos.

Fix v0.4.2: verificar rutas de salida de los seis skills, `design_root` en el plan y bloqueo de transición cuando falta una salida en `design/ddd/<run-id>/`.

Fix v0.4.2: comprobar que la inicialización usa `design/ddd` y rechaza `design/database`.
