# Mobile Application Design — Claude Code Plugin v1.2.1 (DTC-105)

Plugin Anthropic Claude Code: `.claude-plugin/plugin.json` y 7 directorios `skills/<name>/SKILL.md` descubiertos automáticamente. Cada skill contiene `references/`, `templates/`, `scripts/`, `examples/` y `assets/`.

## Skills
1. mobile-application-reconstruction-analyzer — G1
2. mobile-architecture-designer — G2
3. mobile-navigation-state-designer — G3
4. mobile-api-offline-integration-designer — G4
5. mobile-evolution-release-planner — G5
6. mobile-development-handoff — G6
7. mobile-design-orchestrator — G0–G6

## Instalación Claude Code
Descomprimir el ZIP y agregar la carpeta raíz como plugin local mediante el mecanismo de plugins habilitado en su instalación de Claude Code. El plugin no requiere dependencias Python para los validadores básicos. El descubrimiento real no fue probado en Claude Code.

## Rutas de salida
- `.comsatel/mobile-application-design/runs/<run-id>/`: planificación, gates, decisiones y evidencias operativas.
- `design/mobile/<run-id>/`: entregables técnicos OKF v0.2, sujetos a STD-OKF-001 v1.11.0-stable.

## Inicialización y control de gates
```bash
python scripts/workflow.py init --workspace . --run-id MOB-001 --scenario greenfield   # no distingue mayúsculas
# completar sources en scope-manifest.yaml y vaciar missing_sources
python scripts/workflow.py approve --workspace . --run-id MOB-001 --gate G0 --actor human:<nombre> --evidence <ref>   # alias: approve-gate
python scripts/workflow.py start --workspace . --run-id MOB-001 --task <skill>
python scripts/workflow.py complete --workspace . --run-id MOB-001 --task <skill> --evidence <archivo-en-design>
python scripts/workflow.py approve --workspace . --run-id MOB-001 --gate <Gn> --actor human:<nombre> --evidence <ref>
python scripts/workflow.py status|check --workspace . --run-id MOB-001
```
Reglas (las mismas de web-platform-design): G0 exige `sources` completas en `scope-manifest.yaml`; el aprobador debe ser `human:<nombre>`; una tarea solo inicia si el gate previo está aprobado. Requiere PyYAML para aprobar G0.

El workflow **no** ejecuta automáticamente skills, no autentica humanos, no publica en GitLab ni garantiza conformidad semántica OKF.

## Fronteras
DDD y API son fuentes gobernadas; Mobile no se particiona 1:1 con MicroUIs ni Bounded Contexts. UX/UI es dueño de experiencia y Atomic Design; Mobile implementa arquitectura y contratos técnicos.
