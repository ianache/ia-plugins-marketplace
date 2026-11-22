# Práctica de estimación de esfuerzo y costo (v3)

Extiende la **práctica de estimación v2** (PO ianache, 2026-10-16) para estimar, por separado, el esfuerzo del **humano** y del **agente de IA**, e incluir el aseguramiento de calidad (QA) manual y automatizado. La estimación es de **referencia**: la confirma o corrige el equipo en el Sprint Planning y nunca es un compromiso.

Salidas: los cuatro valores de la cabecera de la descripción del Milestone y la sección «Referencia de esfuerzo y costo» del SSP.

| Comando | Quién | Significado |
|---|---|---|
| `/time` | humano | horas-persona: desarrollo con agentes (v2) más QA |
| `/cost` | humano | `/time` × S/ 30.00 por hora |
| `/time_agent` | agente de IA | horas de trabajo del agente |
| `/cost_agent` | agente de IA | suscripción prorrateada al Sprint |

## 1. Qué cambió respecto de la v2

| Tema | v2 | v3 |
|---|---|---|
| Alcance | Desarrollo con Claude (Superpowers), UX/UI con Claude Design y pruebas con Postman, K6 y Playwright, más la revisión humana; **sin QA posterior** (`TO TEST`, `IN TESTING`) | Igual, **más QA** (diseño de pruebas y ejecución de TC manuales y automatizados) como componente separado |
| Quién | Solo horas de la persona | Horas del humano y del agente por separado |
| Cabecera del Milestone | `/time`, `/cost` | `/time`, `/cost`, `/time_agent`, `/cost_agent` |

El componente de desarrollo se calcula **exactamente como en la v2** y se muestra aparte, para poder comparar con los Sprints anteriores.

## 2. Desarrollo del humano (v2, aprobada)

```
Horas = ( 3 + 2,5 × criterios de aceptación ) × ( 1 + suma de factores )     → redondeo hacia arriba al múltiplo de 2 h
```

- **3 h fijas:** arranque, plan de implementación, revisión humana y entrega a QA.
- **2,5 h por criterio:** desarrollo 1,25 h, UX/UI 0,5 h y pruebas 0,75 h, con la revisión incluida.
- **Criterios:** los escenarios `### AC-n` del archivo de la User Story (no del DSP ni del Issue).
- **Factores:** E integración externa +0,30 · S seguridad o sesión +0,20 · V vigencia o integridad +0,20 · F fundación +0,20 · D dependencia en el Sprint +0,10 · Q preguntas abiertas +0,05 cada una (máximo 0,15). D solo cuando la historia entra a un Sprint con su dependencia.
- **Talla:** S hasta 12 h · M 13–24 · L 25–40 (revisar si conviene dividir) · **XL** más de 40 (dividir antes del Sprint Planning).
- **Confianza:** Alta hasta 0,15 de factores · Media hasta 0,50 · Baja por encima.

Ejemplo: 5 criterios, factores E y D → (3 + 2,5 × 5) × 1,4 = 21,7 → **22 h**, talla M, confianza Media.

### Desarrollo con Superpowers
Las horas fijas y por criterio ya cubren el flujo de Superpowers. Al estimar, considerar sus etapas y qué parte es del humano y cuál del agente:

| Etapa (skill de Superpowers) | Humano | Agente |
|---|---|---|
| Diseño y plan (`brainstorming`, `writing-plans`) | decide y aprueba el diseño y el plan | propone alternativas y redacta el plan |
| Implementación (`test-driven-development`, `subagent-driven-development` o `executing-plans`) | dirige y desbloquea | escribe pruebas y código |
| Diagnóstico (`systematic-debugging`) | decide la causa y la corrección | investiga y propone |
| Verificación y revisión (`verification-before-completion`, `requesting-code-review`) | revisa y aprueba | ejecuta verificaciones y prepara la revisión |
| Integración (`finishing-a-development-branch`) | decide cómo integrar | prepara el cambio |

Una historia con muchas iteraciones de revisión o diagnóstico lo expresa con los factores (por ejemplo V, E, Q), no con horas ad hoc.

## 3. Aseguramiento de calidad (aprobada el 2026-10-24, sin datos históricos)

El QA se calcula a partir de los **casos de prueba (TC) aprobados** del pack `qa-design`, no de una cifra aparte:

- Cada `TC` declara `execution: manual` o `execution: automated`. Un TC manual lo ejecuta una persona y no genera `AT`; un TC automatizado lo implementa el agente (`qa-agentic-test-engineer`, un `AT` por TC) y lo revisa una persona.
- `qa-feature-analyzer` y `qa-test-design` producen el análisis (`QFA`) y el diseño (`QTD`, `TSN`, `TC`); `qa-test-design-reviewer` y `qa-agentic-test-reviewer` revisan de forma independiente.
- Un TC con `automation_candidate: true` que aún no tiene `AT` cuenta como **manual** hasta que se decida automatizarlo.

| Concepto | Humano | Agente |
|---|---|---|
| Diseño de pruebas por historia (QFA y QTD) | 0,5 h (revisión) | 1,0 h |
| TC manual | 0,5 h (ejecución, evidencia, defectos) | 0 h |
| TC automatizado | 0,25 h (revisión del AT y de la evidencia) | 0,5 h (implementación y ejecución) |

**Estos valores fueron aprobados por el PO (ianache, 2026-10-24) sin datos históricos**: se calibran con el primer Sprint cerrado (sección 7). Si la historia aún no tiene TC, el QA no se estima y se avisa; no se supone.

## 4. Tiempo del agente (`/time_agent`)

`/time_agent` = desarrollo humano × `dev_agent_h_per_human_h` (1,0, aprobada) + horas de agente del QA. La razón 1,0 es un punto de partida sin datos históricos: se calibra con las horas reales (sección 7). Es tiempo de trabajo del agente, no un costo: el costo del agente lo fija la suscripción.

## 5. Costos

- **`/cost` (humano)** = `/time` (redondeado hacia arriba a hora entera) × **S/ 30.00** por hora (promedio informado por el responsable). Si la tarifa cambia, se anota la fecha y se recalculan los Sprints no cerrados.
- **`/cost_agent`** = **USD 25.00** de suscripción mensual × puestos × (días hábiles del Sprint ÷ días hábiles del mes). La suscripción es un costo fijo: se prorratea por el periodo que ocupa el Sprint, no por horas de agente. Parámetros: puestos (por defecto 1; uno por persona que usa el agente), días hábiles del mes (22).
- **Moneda:** el valor se informa en soles. El tipo de cambio (S/ por USD) **lo informa una persona** (fuente y fecha). Vigente: **3,45** (ianache, 2026-10-24), en `assets/estimation-coefficients.json`; un Sprint puede indicar el suyo en `sprint.fx_pen_per_usd`. Sin tipo de cambio, `/cost_agent` se escribe `S/ PENDIENTE (USD xx.xx)`. No se asume un tipo de cambio.

## 6. Procedimiento

1. Confirmar que las User Stories del DSP están aprobadas y sus criterios al día.
2. Reunir las entradas: criterios (`us_file` o conteo), factores y preguntas abiertas por historia; TC manuales y automatizados de `qa-design` (`tc_dir` o conteo); días hábiles del Sprint, puestos y tipo de cambio.
3. Ejecutar `python scripts/estimate.py <entrada.json> --format text` (ejemplo en `examples/estimate-input.example.json`). El script no consulta ni modifica GitLab.
4. Revisar los **avisos** (tallas L/XL, historias sin TC, coeficientes sin calibrar, tipo de cambio pendiente) y dividir toda historia XL antes de seguir.
5. Completar la sección «Referencia de esfuerzo y costo» del SSP y los cuatro comandos de su descripción del Milestone con la salida.
6. Un humano confirma o corrige la estimación en el Sprint Planning; solo entonces se publica el Milestone (`mgt-work-publisher-synchronizer`).
7. **Reestimar** cuando cambie el número de criterios, se abra o cierre una pregunta, entre a un Sprint con dependencia, se divida la historia, cambien los TC o cambien los coeficientes.

## 7. Calibración

Al cerrar el Sprint se compara lo estimado con lo real, historia por historia:

- **Humano:** horas reportadas con `/spend` (`gitlab-ai-kpi-semanal`, `informe-mensual-horas-proyecto`).
- **Agente:** las horas con etiqueta `AI Cowork` o `@AI Cowork` en el `/spend` dan una referencia de uso de IA para ajustar `dev_agent_h_per_human_h`.
- **QA:** horas reales por TC manual y automatizado.
- Si la desviación media supera el 30 %, se ajustan los coeficientes con fecha y decisión del PO, y se reestiman los Sprints no cerrados. Los Sprints cerrados conservan sus horas originales como evidencia.

## 8. Historial de coeficientes

| Versión | Fecha | Alcance | Estado | Decisión |
|---|---|---|---|---|
| 1 | 2026-10-11 | Dev con Claude Code: 4 h fijas, 3 h por criterio | reemplazada | Punto de partida sin datos |
| 2 | 2026-10-16 | Desarrollo, UX/UI y pruebas con agentes: 3 h fijas, 2,5 h por criterio | **aprobada** | ianache (PO) |
| 3 | 2026-10-24 | Tarifa S/ 30,00 por hora, suscripción USD 25,00 al mes y tipo de cambio 3,45 confirmados; **QA**, **razón de horas del agente**, 22 días hábiles por mes, QA incluido en `/time` y cabecera con `/cost_agent` y `/time_agent` | **aprobada** | ianache (PO); calibrar con el primer Sprint |

## 9. Límites

- La estimación es de referencia y no sustituye la capacidad ni el compromiso del equipo.
- Los coeficientes de QA y del agente están aprobados pero no tienen datos históricos: el script lo informa en cada ejecución hasta que se calibren.
- No incluye infraestructura ni licencias distintas de la suscripción del agente.
- El costo del agente depende de la suscripción vigente y del tipo de cambio informado; no refleja consumo por uso.
