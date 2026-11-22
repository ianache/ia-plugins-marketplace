# QA SDLC Pack — Plugin Anthropic / Claude Code

Plugin con 9 skills empaquetados bajo `skills/<skill-name>/SKILL.md`, detectados por Claude Code al instalar el plugin. Se conservan contratos, scripts, tests, plantillas y recursos del paquete base.

## Instalación local

```bash
claude --plugin-dir /ruta/qa-sdlc-anthropic-plugin
```

Alternativamente, agregar este directorio a un marketplace de plugins de Claude Code y habilitar `qa-sdlc-pack`.

## Skills incluidos

- `qa-sdlc-orchestrator`
- `qa-feature-analyzer`
- `qa-test-design`
- `qa-test-design-reviewer`
- `qa-agentic-test-engineer`
- `qa-agentic-test-reviewer`
- `qa-quality-intelligence`
- `postman-automation`
- `loadtest-automation`

## Clasificación de skills

- **Especialistas del plan (6):** `qa-feature-analyzer`, `qa-test-design`, `qa-test-design-reviewer`, `qa-agentic-test-engineer`, `qa-agentic-test-reviewer`, `qa-quality-intelligence`.
- **Orquestador (1):** `qa-sdlc-orchestrator`.
- **Subordinados:** `postman-automation` (TC de API funcional) y `loadtest-automation` (TC `rendimiento`), uno por microservicio API y tipo de prueba. No tienen tarea propia en el plan: los invoca `qa-agentic-test-engineer` dentro de `T05-API`, y el gate de ingeniería verifica sus reportes.

## Política de Test Cases

Cada TC requiere precondiciones comprobables, datos exactos y técnica de diseño, pasos numerados, resultado esperado observable por paso, oráculos, postcondiciones, trazabilidad y Surface Target específico (API, WEB, MOBILE, DATABASE, EVENT, BATCH, INTEGRATION, CROSS_SURFACE). No inventar contratos o rutas ausentes: bloquear y solicitar evidencia.

## Gates

El orquestador controla aprobaciones y estados. El reviewer propone el gate de diseño y exige `tc-detail-complete` y `surface-target-complete`. Ningún gate de salida puede bloquear a su propia tarea productora. Validar el DAG antes de ejecución.

## Tests

```bash
python -m pytest -q skills/qa-test-design-reviewer/tests
```

La presencia estructural no sustituye la revisión semántica independiente ni la evidencia de acceso real al elemento bajo prueba.
