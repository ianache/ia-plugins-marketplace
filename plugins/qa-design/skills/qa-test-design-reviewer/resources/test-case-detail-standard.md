# Estándar de detalle de Test Cases — QA SDLC Pack

Aplicable a TC-* `READY`. Cada dato y resultado debe derivarse de requisitos aprobados; si no está definido, registrar AMB y bloquear.

## Reglas de completitud
1. PC-ID, estado inicial, comprobación observable y preparación.
2. TD-ID, estrategia/técnica, clase/partición/límite/condición, valor exacto o referencia versionada, seed, resultado esperado y cleanup.
3. STEP-ID secuencial, acción concreta, entrada TD-ID y expected result del paso, con evidencia esperada.
4. Oracle global preciso con fuente AC/BR/API, método de verificación, umbral y tolerancia cuando apliquen.
5. Postcondiciones y cleanup para ejecución repetible.
6. No valores TBD, etc., correcto, funciona, según corresponda, sin definición verificable.
7. Las técnicas se eligen por riesgo y tipo de dato; no imponer todas a todos los casos.
8. Seguridad y privacidad: datos sintéticos o anonimizados; secretos referenciados, no embebidos.

## Gate
Rechazar READY si falta una sección, no hay filas de tablas, no hay referencias de datos o pasos, o no existe un resultado esperado por paso. La revisión semántica independiente verifica exactitud contra el requisito y suficiencia de la estrategia; el script solo detecta faltantes estructurales.
