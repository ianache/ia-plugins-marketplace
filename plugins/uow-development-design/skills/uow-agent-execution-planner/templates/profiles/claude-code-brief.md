# Instrucciones para el agente — <UOW-ID>

Estás implementando la unidad de trabajo `<UOW-ID>` (US `<US-ID>`). Léela completa antes de empezar: `<ruta de la UOW>`, `<ruta del UCB>`, `<ruta del UCM>` y `<ruta del UAP>`.

## Reglas
- Trabaja solo en `allowed_paths` del UCM. No toques `forbidden_paths`.
- No cambies contratos (API, eventos, esquema de BD) ni amplíes el alcance. Si el contrato es ambiguo o falta algo, detente.
- Empieza siempre por la prueba (TDD) y ejecuta el comando de verificación de cada paso.
- No escribas secretos; usa las variables de entorno indicadas. No ejecutes acciones destructivas ni contra PROD.
- Ante una desviación, regístrala en `<record_in>` y consulta a `<escalate_to>`.

## Flujo sugerido (Superpowers)
1. `superpowers:using-git-worktrees` para aislar el trabajo en la rama `<rama de trabajo>` desde `<source_commit>`.
2. Ejecuta el plan con `superpowers:subagent-driven-development` o `superpowers:executing-plans`.
3. Antes de cerrar, `superpowers:verification-before-completion` y `superpowers:requesting-code-review`.

## Entrega
Commits pequeños con `[<UOW-ID>]`, MR hacia `<target_branch>` y la evidencia de cada criterio de terminado.
