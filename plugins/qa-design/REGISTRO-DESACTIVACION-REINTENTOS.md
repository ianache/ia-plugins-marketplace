# Registro: desactivación de reintentos en gates de qa-design

- **Fecha del cambio:** 2026-11-20
- **Alcance:** todos los gates del plugin `qa-design` (8 gates).
- **Cambio:** `max_retries` pasa a `0` en todos los gates. `on_retries_exhausted` no cambia (`REQUEST_HIL`).
- **Motivo:** los reintentos afectaban la dinámica de avance del flujo.
- **Comportamiento resultante:** el primer `FAIL` de cualquier check de un gate `CONDITIONAL_HIL` produce `BLOCKED` con `reason: retries_exhausted` y abre una intervención humana (`human_intervention`). Con `halt_scope: all` (por defecto) la ejecución completa se detiene. Los gates `MANDATORY_HIL` ya tenían `max_retries: 0`. La incertidumbre (`UNCERTAIN`) ya bloqueaba sin reintento y sigue igual.

## Gates impactados

| Gate | Tarea | Modo | `max_retries` antes | `max_retries` ahora | Efecto del primer FAIL |
| :--- | :-: | :--- | :-: | :-: | :--- |
| `FEATURE_ANALYSIS_GATE` | T01 | CONDITIONAL_HIL | 2 | 0 | BLOCKED + intervención humana |
| `TEST_DESIGN_GATE` | T02 | CONDITIONAL_HIL | 2 | 0 | BLOCKED + intervención humana |
| `TEST_DESIGN_REVIEW_GATE` | T03 | CONDITIONAL_HIL | 1 | 0 | BLOCKED + intervención humana |
| `TESTCASE_PUBLICATION_GATE` | T04 | MANDATORY_HIL | 0 | 0 | Sin cambio (ya era 0) |
| `TEST_ENGINEERING_GATE` | T05-\<superficie\> | CONDITIONAL_HIL | 2 | 0 | BLOCKED + intervención humana |
| `TEST_ENGINEERING_REVIEW_GATE` | T06 | CONDITIONAL_HIL | 1 | 0 | BLOCKED + intervención humana |
| `QUALITY_INTELLIGENCE_GATE` | T07 | CONDITIONAL_HIL | 1 | 0 | BLOCKED + intervención humana |
| `HUMAN_GATE` | T08 | MANDATORY_HIL | 0 | 0 | Sin cambio (ya era 0) |

Gates con cambio real: 6 de 8. Gates sin cambio: `TESTCASE_PUBLICATION_GATE` y `HUMAN_GATE`.

## Archivos modificados

- `skills/qa-sdlc-orchestrator/resources/gate-policies.yaml`: fuente de verdad que lee el orquestador (8 valores).
- `skills/qa-sdlc-orchestrator/templates/QA-Orchestration-Plan.yaml`: plantilla (8 valores).
- `skills/<skill>/resources/gates/<GATE>.yaml`: copia por gate de cada especialista (8 archivos, uno por gate).
- `skills/qa-sdlc-orchestrator/tests/test_orchestrator.py`: `test_fail_retries_then_blocks` sustituida por `test_fail_blocks_without_retry`.
- `DOCUMENTACION.md`: columna "Reintentos" de la tabla de gates y párrafo del modo condicional.
- `CHANGELOG.md` (`[Sin publicar]`): entrada del cambio.

No cambian: los `resources/contracts/common-contract.yaml` (texto "gate FAIL con AUTO_RETRY o reopen"). `AUTO_RETRY` queda sin uso, pero `reopen` sigue siendo la vía de rehacer una tarea. Revisar si ese texto se actualiza en un cambio posterior.

## Para el análisis posterior

Métricas a recoger por gate, comparando con el periodo previo al cambio:

1. **Intervenciones humanas abiertas** por gate (`human_intervention` con `reason: retries_exhausted`). Esperado: aumento.
2. **Tiempo de bloqueo**: desde que se abre la intervención hasta su `RESOLVED`. Es el coste principal del cambio.
3. **Decisiones humanas** por tipo (`REVALIDATE`, `REWORK`, `CANCEL`) y su frecuencia por gate.
4. **Fallos que antes se recuperaban**: tareas con `attempt0` en `FAIL` seguido de `attempt1` en `PASS`. Son los casos donde el reintento aportaba valor; con el cambio ahora requieren intervención.
5. **Tasa de `FAIL` por check**: qué checks disparan más bloqueos (guía para ajustar criterios o especialistas).
6. **Calidad de salida**: incidencias detectadas después de `HUMAN_GATE` o `TESTCASE_PUBLICATION_GATE` que habrían pasado con reintentos. Requiere seguimiento manual.
7. **Paradas de ejecución (`halt_scope: all`)**: número y duración de paradas que afectan a tareas en paralelo (T04 y T05-\*).

Fuentes de datos: `events.jsonl` (eventos `GATE` y `HUMAN_DECISION`), `evidence/<GATE>/<TID>-attemptN.yaml` y `human_intervention` en `plan-status.yaml`.

Nota sobre la línea base: en el repo no hay runs reales de qa-design. Los ejemplos de `examples/` solo tienen 2 eventos `AUTO_RETRY`, así que la comparación debe hacerse con runs de producción.

## Pendiente de decisión

- **Versión SemVer:** `qa-design` sube de `1.8.0` a `2.0.0` (MAJOR) por ser un endurecimiento de gates y un cambio incompatible de comportamiento, según `plugins/AGENTS.md`. Registrado en `CHANGELOG.md` como `[2.0.0] - 2026-11-20`.
- **Runs en curso:** `plan.yaml` copia `gate_policies` al hacer `init`. Los runs ya iniciados mantienen `max_retries` anterior hasta re-inicializarse o invalidar tareas.
