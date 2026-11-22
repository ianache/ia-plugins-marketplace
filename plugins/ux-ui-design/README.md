# UX/UI Design — Claude Code Plugin v1.2.1

Plugin nativo de Claude Code. **6 skills especializados + 1 orchestrator**. Separado de Web Platform Design y Mobile Application Design.

## Instalación y uso

Descomprimir y cargar desde un marketplace de plugins Claude Code o probar localmente con `claude --plugin-dir /ruta/ux-ui-design-claude-plugin-v0.1.0` (según versión del CLI). Invocar el orchestrator mediante la selección de skills de Claude Code. Los scripts auxiliares se ejecutan manualmente; el plugin no supone acceso a Figma, Stitch o Claude Design.

## Política de carpetas

- `.comsatel/ux-ui-design/runs/<run-id>/`: plan, estados, evidencias y aprobaciones; no son OKF conceptuales.
- `design/ux-ui/<run-id>/`: entregables conceptuales OKF v0.2 según STD-OKF-001 v0.1.0-stable.
- Para publicación a KB gobernada, usar Merge Request y autorización humana. No modificar directamente `design/web/` ni `design/mobile/`.

## Workflows

- Greenfield: G0→G1→G2→G3→G4→G5→G6.
- Brownfield: inventario de diseño existente y gap analysis en G0; luego gates aplicables.
- Evolution: análisis de impacto y compatibilidad visual en G0; revalidación de pantallas/componentes afectados.

## Límites

El plugin define experiencia, flujos, pantallas, Atomic Design, tokens y prototipos. **No** decide partición de MicroUIs, módulos Flutter, BFF, contratos OpenAPI ni genera código productivo. Los Bounded Contexts aportan contexto, pero no imponen partición de pantallas ni componentes. Las referencias a herramientas externas son evidencia, no ejecución simulada.

## Catálogo de tipos OKF

`UXR`, `FLW`, `SCR`, `CMP`, `TKN`, `HOF` **son tipos aprobados en STD-OKF-001 v0.1.0-stable** (no estaban en el catálogo v1.2.0). Para decisiones arquitectónicas existentes puede utilizarse `ADR` si aplica.

## Recursos

Cada `skills/<nombre>/` incluye `SKILL.md`, `references/contract.md`, `references/technical-guidance.md`, `references/gate-checklist.md`, `templates/deliverable.md`, `templates/gate-evidence.json`, `scripts/validate.py`, `examples/README.md` y `assets/README.md`.

## Verificación

`python scripts/validate_plugin.py` y `python -m unittest discover -s tests -v`.

## CLI de control

```bash
python scripts/workflow.py init --workspace . --run-id UX-001 --scenario greenfield   # no distingue mayúsculas
# completar sources en scope-manifest.yaml y vaciar missing_sources
python scripts/workflow.py approve --workspace . --run-id UX-001 --gate G0 --actor human:<nombre> --evidence <ref>   # alias: approve-gate
python scripts/workflow.py start|complete --workspace . --run-id UX-001 --task <skill> [--evidence <archivo-en-design>]
python scripts/workflow.py status|check --workspace . --run-id UX-001
```

Reglas (las mismas de web-platform-design): G0 exige `sources` completas en `scope-manifest.yaml`; el aprobador debe ser `human:<nombre>`; una tarea solo inicia si el gate previo está aprobado (G1 requerimientos, G2 pantallas, G3 sistema visual, G4 prototipo, G5 calidad, G6 handoff). Requiere PyYAML para aprobar G0. El modo anterior `workflow.py <run-id>` sigue funcionando.
