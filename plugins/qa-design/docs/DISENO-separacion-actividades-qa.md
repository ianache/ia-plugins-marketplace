# Diseño: separación de actividades de QA por ámbito y superficie

Estado: **propuesta para revisión**. No hay cambios de código asociados todavía. Este documento no modifica el comportamiento del plugin.

Audiencia: responsables de `qa-design` que aprueban el diseño antes de implementarlo.

---

## 1. Problema

1. El plan (`plan.yaml`) se define en G0 y crea una tarea `T05-<surface>` por superficie. Para API, G0 exige declarar `scope.microservices`, y el check `tc-api-assigned` de T03 falla si un TC referencia un `api_id` no declarado en G0. La asignación real de TC a AUT no se conoce a priori: se descubre al diseñar y al revisar los TC.
2. `api_id` es un campo obligatorio del TC (`tc_contract` 1.4). Así un TC aprobado queda acoplado a un AUT antes de que exista la vinculación.
3. `qa-test-design` mezcla planificación (QTS, QTP) con diseño (TSN, TC, TDR).
4. `qa-agentic-test-engineer` implementa en un mismo skill los TC manuales y los automatizados, para cada superficie.

## 2. Definiciones

- **AUT (Application Under Test):** rol. Es el componente que un TC prueba. No es un tipo documental. Puede ser un microservicio (documentado con `SVC` y `HCB`), un Shell o aplicación web (`WEB`) o una aplicación móvil (`MOB`). Un TC, un AT o un MT lo referencian por el ID de su documento en la KB.
- **AT (Automated Test):** implementación automatizada de exactamente un TC aprobado. Tipo existente en el estándar.
- **MT (Manual Test):** no se crea como documento. Ver §6.
- **Ámbito:** planificación (DSP/SSP), diseño (TSN/TC/TDR), implementación (manual o automatizada), ejecución y evidencia (EXEC/EVD), análisis (QQI).

## 3. Principios

1. **El TC se diseña sin AUT.** Un TC aprobado no se modifica. La vinculación con el AUT se registra en el AT.
2. **Planificación y diseño son revisiones distintas.** La planificación depende del DSP/SSP, el riesgo y los recursos. El diseño depende de los requisitos y del TSN.
3. **La implementación automatizada se vincula al AUT al final.** Solo cuando el AUT está identificado se generan las tareas de implementación.
4. **Documentación en la KB, código en el repositorio del componente.** Toda la documentación de prueba (TSN, TC, TDR, TDA, AT, QTE, EXEC, EVD) vive en la KB del producto. El código vive en `test/functional/` y `test/load/` del componente.
5. **El plugin no ejecuta pipelines.** Genera y documenta las pruebas. La ejecución automatizada la hace el pipeline de CI/CD al abrir un MR a las ramas configuradas. El plugin consume sus resultados.
6. **Espacio de trabajo = KB del producto.** El plugin corre desde esa carpeta con Claude CLI, o con esa carpeta añadida al proyecto en Claude Desktop. Todas las rutas del pathmap son relativas a esa raíz.

## 4. Skills

| Skill | Actividad | Entrada principal | Salida | Estado |
|---|---|---|---|---|
| `qa-feature-analyzer` | Análisis (T01) | DSP/SSP | `QFA` | Sin cambios |
| `qa-test-planner` | Planificación | QFA aprobado | `QTP` (estrategia, plan, priorización, superficies, entornos) | Nuevo: se separa de `qa-test-design` |
| `qa-test-design` | Diseño | QTP aprobado | `TSN`, `TC`, `TDR`, matriz de trazabilidad | Recortado: deja de producir QTP |
| `qa-test-design-reviewer` | Revisión de diseño | QTD | `QTR` | Sin cambios de rol |
| `qa-manual-test-engineer` | Implementación manual | TC manuales aprobados | Plan de ejecución manual dentro de `QTE`, `TDA` manuales, `EXEC`/`EVD` manuales | Nuevo: sale de `qa-agentic-test-engineer` |
| `qa-automation-engineer` | Implementación automatizada | TC automatizados y AUT vinculado | `AT`, `TDA` automatizados, referencias a código en el repo del AUT, `EXEC`/`EVD` ingeridos del pipeline | Refactor: sale de `qa-agentic-test-engineer` |
| `qa-agentic-test-reviewer` | Revisión de implementación | `QTE` | `QER` | Cambia de entradas: revisa manual y automatizada |
| `qa-quality-intelligence` | Análisis de calidad | `EXEC`/`EVD` | `QQI` | Sin cambios |
| `qa-sdlc-orchestrator` | Control del flujo | Plan | Plan, estado, gates | Cambia: nuevos gates, expansión dinámica, espera de eventos externos |

`qa-automation-engineer` tiene adaptadores por superficie. La superficie determina el framework y la ruta del código; no determina la identidad del AUT:

| Superficie | Framework | Código en el componente | Ejecución |
|---|---|---|---|
| API (funcional) | Postman / newman, mediante `postman-automation` (subordinado) | `test/functional/postman.json` | Plantilla `postman-testing.yaml` |
| API (carga) | k6, mediante `loadtest-automation` (subordinado) | `test/load/k6.js` | Plantilla `k6loadtesting.yaml` |
| Web | Playwright o Selenium, según el stack declarado por el producto | `test/functional/` del Shell o de la aplicación web | Por componente (tarea de CI pendiente) |
| Móvil | Appium + Cucumber (suite existente) | `test/functional/` de la aplicación | Plantilla `appmobile-android.yaml` (pendiente de revisión por CI/CD) |

Carga solo para API en esta versión (decisión 4).

## 5. Plan del workflow

```
G0 (superficies, DSP/SSP; sin microservicios)
 └─ T01 análisis (qa-feature-analyzer)                     → QFA
     └─ T02 planificación (qa-test-planner)                 → QTP        [TEST_PLANNING_GATE]
         └─ T03 diseño (qa-test-design)                     → TSN/TC/TDR [TEST_DESIGN_GATE]
             └─ T04 revisión de diseño (qa-test-design-reviewer) → QTR   [TEST_DESIGN_REVIEW_GATE]
                 ├─ T05 publicación de TC (orquestador)                  [TESTCASE_PUBLICATION_GATE]
                 ├─ T06 vinculación TC → AUT (qa-automation-engineer)    [AUT_BINDING_GATE]
                 │    └─ expansión: T07-<AUT>-automation por cada AUT vinculado
                 └─ T08 implementación manual (qa-manual-test-engineer)  [MANUAL_TEST_GATE]

 T07-<AUT>-automation (espera el pipeline de CI en cada MR)  → AT, EXEC, EVD
     └─ T09 revisión de implementación (qa-agentic-test-reviewer) → QER  [TEST_ENGINEERING_REVIEW_GATE]
         └─ T10 inteligencia de calidad (qa-quality-intelligence)       → QQI [QUALITY_INTELLIGENCE_GATE]
             └─ T11 decisión humana (orquestador)                        [HUMAN_GATE]
```

Puntos clave:

- **G0 ya no pide microservicios.** Solo superficies y DSP/SSP.
- **T06 (vinculación)** resuelve, para cada TC automatizado, el AUT según la KB del producto. Si no encuentra el documento del AUT, la tarea queda `BLOCKED` con intervención humana. No se inventa un AUT.
- **Expansión.** Tras `AUT_BINDING_GATE` en PASS, el orquestador crea una tarea `T07-<AUT>-automation` por AUT vinculado, en una nueva `plan_revision`. T09 depende del conjunto congelado en ese gate.
- **Espera externa.** T07 para `AUTOMATED_CICD` pasa a un estado nuevo `WAITING_EXTERNAL` hasta que el pipeline del MR termina. El orquestador lo registra con el ID y la URL del pipeline.
- **Ingesta.** `qa-automation-engineer`, en modo ingesta, lee los artefactos del pipeline y crea los `EXEC` y `EVD`. El destino final de las evidencias lo decide la tarea de CI/CD más adelante; el diseño solo fija que el `EXEC` referencia el pipeline.
- **Entorno por rama destino del MR.** Según las plantillas de CI: `integration` → DEV, `develop` → QA, `release` → PRE. El `EXEC` toma el entorno de ahí.

### 5.1 Identificadores

Renumerar T01–T08 rompe el código y las pruebas existentes. Propuesta: conservar los nombres de tarea y añadir los nuevos con sufijo, y migrar a numeración limpia solo en la versión MAJOR de la siguiente etapa. Esto es una decisión a confirmar antes de implementar.

## 6. Manual: sin documento MT

- El plan de ejecución manual vive en el `QTE`, en `test-execution-plan.md`, junto con los pasos del TC.
- `EXEC` con `execution_mode: MANUAL` y `EVD` registran la ejecución.
- Un documento MT duplicaría la especificación del TC. Si en el futuro se necesitan guiones manuales reutilizables, se evalúa como tipo nuevo con cambio HIL del estándar.

## 7. Cambios de contrato

| Elemento | Cambio | Impacto |
|---|---|---|
| `tc_contract` | Se elimina `api_id` como campo obligatorio del TC. La vinculación pasa al AT. | MAJOR |
| `QTD` | Deja de incluir estrategia y plan, que pasan a `QTP`. La definición de unidad documental del estándar cambia. | Requiere cambio HIL del estándar |
| `QTP` | Se usa como salida de `qa-test-planner`. Ya es un tipo aprobado. | Sin cambio de tipo |
| `AT` | Declara `related` hacia el AUT (SVC/HCB, WEB o MOB) y `code_ref` (repo, ruta, commit). | Cambio de plantilla |
| Gates | Nuevos: `TEST_PLANNING_GATE`, `AUT_BINDING_GATE`, `MANUAL_TEST_GATE`, `AUTOMATION_GATE`. `TEST_ENGINEERING_GATE` se reparte entre manual y automatizado. | MAJOR |
| Plan | `plan_revision` para expansión; estado `WAITING_EXTERNAL`. | MINOR en el esquema, con cambios de orquestador |

## 8. Versionado

Se trata como MAJOR de `qa-design`: se renombran y dividen skills, cambian entradas y salidas, y cambia el DAG. Cada skill afectado sube su versión. Los runs en curso con la versión 2.x siguen con su plan original; las nuevas ejecuciones usan el DAG nuevo.

## 9. Riesgos y pendientes

1. **Estándar:** dividir `QTD` requiere revisar su definición de unidad documental. Es un cambio HIL.
2. **Escritura en repositorios de componentes:** el skill de automatización escribe código en el repo del AUT. Debe hacerlo en una rama con MR y con aprobación humana, sin commit directo.
3. **Consistencia KB ↔ código:** el AT debe apuntar a un commit concreto. Si el código cambia, el AT queda desactualizado. Hace falta un check de consistencia del SHA.
4. **Contrato de ingesta:** los formatos de evidencia que producen las plantillas (newman HTML, reporte de k6, reporte de Playwright, Allure de la suite móvil) deben estar documentados para que la ingesta sea determinista.
5. **Móvil:** el job `android_execution` referencia `testng.xml`, que no existe en `test/functional/`. Es responsabilidad del pipeline, fuera del alcance de este plugin.
6. **Tests existentes:** `check_test_engineering.py`, `check_tc_detail.py`, `test_qa_plugin.py` y los `test_skill_contract.py` de cada skill asumen el diseño actual. Hay que actualizarlos.
7. **Pruebas que faltan hoy:** la expansión dinámica del plan, la espera externa y la ingesta no tienen cobertura. Se diseñan con pruebas antes de implementar.

## 10. Orden de implementación propuesto

1. Actualizar el estándar (solo `QTD`) con aprobación HIL.
2. Orquestador: `WAITING_EXTERNAL`, expansión por `plan_revision`, nuevos gates y pruebas.
3. `qa-test-planner` (separación de QTP) y recorte de `qa-test-design`.
4. `qa-manual-test-engineer` y `qa-automation-engineer` con sus adaptadores.
5. Revisor de implementación, pruebas de contrato y pruebas de extremo a extremo con un producto de prueba en la KB.
6. Guía de buenas prácticas y CHANGELOG (MAJOR).

## 11. Decisiones tomadas

- MT: sin documento nuevo.
- Planificación separada de diseño.
- Implementación dividida en manual y automatizada, con adaptadores por superficie.
- Carga: solo API.
- Ruta de pruebas: `test/` (singular).
- Espacio de trabajo: KB del producto.
- Documentación de pruebas en la KB; código en el componente.
- El pipeline ejecuta las pruebas en MR; el plugin consume resultados.
