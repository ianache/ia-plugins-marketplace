---
type: STD
title: Estándar corporativo de metadatos Markdown
description: Perfil uniforme de frontmatter OKF v0.2 para los Skills Packs y Knowledge Bases de COMSATEL.
id: STD-OKF-001
version: "0.1.0"
status: stable
owner: team:architecture
classification: internal
tags: [okf, metadata, governance]
generated:
  by: process:standard-authoring
  at: "2026-11-22T11:53:49-05:00"
sources:
  - id: okf-spec
    resource: https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md
    title: Especificación OKF v0.2
---
# STD-OKF-001 — Perfil COMSATEL de metadatos Markdown

**Estado de esta revision:** `v0.1.0-stable`. Esta es la linea base vigente; se retiraron los historiales previos para iniciar desde cero.

**Decisión de gobierno (2026-10-18):** catálogo inicial aprobado y estado documental establecido en `stable` por autorización del responsable. La publicación en repositorio y la homologación de tipos históricos son actividades independientes.

## Alcance y precedencia

Aplica a los documentos conceptuales Markdown de todos los packs y KB. Google OKF v0.2 exige únicamente `type` no vacío en frontmatter YAML; los demás campos exigidos a continuación son requisitos adicionales del perfil COMSATEL para publicación. Los consumidores deben tolerar campos y tipos desconocidos. `index.md` y `log.md` son archivos reservados con reglas especiales: no aplicarles la plantilla general. Solo `index.md` raíz puede declarar `okf_version: "0.2"`.

## Diccionario de metadatos

| Campo | Tipo | Requisito COMSATEL | Semántica |
|---|---|---|---|
| `type` | string | Obligatorio (OKF) | Sigla registrada del artefacto; excepción `Attested Computation` |
| `id` | string | Obligatorio | ID documental estable, único dentro de KB; no sustituye el ID OKF derivado de ruta |
| `title` | string | Obligatorio | Título legible |
| `description` | string | Obligatorio | Una frase para recuperación e indexación |
| `version` | string | Obligatorio | SemVer entre comillas |
| `status` | enum | Obligatorio | `draft`, `stable`, `deprecated` |
| `owner` | string | Obligatorio | Equipo/rol custodio |
| `classification` | enum | Obligatorio | `public`, `internal`, `confidential`, `restricted` |
| `tags` | list[string] | Obligatorio | Minúsculas, sin duplicados |
| `generated` | map | Obligatorio | `by` y `at`, autoría del contenido actual |
| `generated.by` | string | Obligatorio | `human:<id>`, `process:<id>` o `<producer>/<version>` |
| `generated.at` | datetime | Obligatorio | ISO 8601 con zona; último cambio significativo |
| `sources` | list[map] | Obligatorio | Procedencia; `[]` solo para creación original con justificación |
| `sources[].resource` | string | Condicional | Obligatorio en cada fuente; URI o ruta |
| `sources[].id` | string | Condicional | Obligatorio cuando se cita `[^id]` en el cuerpo |
| `sources[].title` | string | Opcional | Título de fuente |
| `sources[].author` | string | Opcional | Actor de fuente |
| `sources[].last_modified` | datetime | Opcional | Fecha de modificación de fuente |
| `sources[].usage_count` | integer | Opcional | Señal de uso, no puntuación de confianza |
| `usage_window` | map | Condicional | `{from,to}` para recuentos de uso |
| `verified` | list[map] | Condicional | Verificaciones reales, cada una con `by` y `at`; ausencia = no verificado |
| `stale_after` | datetime | Opcional | Instante de revisión por obsolescencia |
| `resource` | string | Condicional | URI canónica del recurso descrito, cuando exista |
| `product` | string | Condicional | Producto |
| `bounded_context_id` | string | Condicional | Bounded Context |
| `service_id` | string | Condicional | Microservicio |
| `schema_id` | string | Condicional | Esquema BD |
| `pack` | string | Condicional | Pack productor |
| `skill` | string | Condicional | Skill productor |
| `related` | list[string] | Opcional | IDs relacionados, acompañados de enlaces Markdown |
| `supersedes` | list[string] | Opcional | IDs reemplazados |
| `runtime`, `parameters`, `computation`, `executor`, `attester` | variable | Condicional | Contrato especial OKF §10 para `Attested Computation` |

No usar `artifact_type`, `source_refs`, `reviewed_by`, `lifecycle_status` como alias nuevos. No inventar fechas históricas ni entradas `verified`. `status: stable` no demuestra verificación humana.

## Plantilla común

```yaml
---
type: LDM
title: "Modelo lógico — Distribuidores"
description: "Entidades y relaciones del bounded context Distribuidores."
id: CL2-LDM-001
version: "1.0.0"
status: draft
classification: internal
owner: team:data-architecture
product: CL2
bounded_context_id: BC-DISTRIBUTORS
pack: data-modeling-database-design
skill: dm-logical-model-designer
tags: [cl2, data-modeling, logical-model]
generated:
  by: dm-logical-model-designer/0.1.0
  at: "2026-10-18T16:10:00Z"
sources:
  - id: req-001
    resource: /requirements/distributors.md
    title: "Requerimientos de distribuidores"
related: [CL2-BC-001]
---
```

## Aggregate, Value Object and Event types

El catalogo vigente define `AGG`, `VO` y `EVT` como tipos documentales. La aprobacion del tipo no aprueba automaticamente los artefactos producidos.

Por autorización explícita del responsable se incorporan `AGG`, `VO` y `EVT` como tipos documentales. Los tipos preexistentes permanecen vigentes. La decisión no constituye aprobación automática de los artefactos producidos.

## Ficha de Diseno Tecnico de Funcionalidad

`FDT` representa una capacidad funcional o caso de uso tecnico, no necesariamente un unico endpoint. Su perfil requiere `service_id`, `bounded_context_id`, `pack` y `skill`; referencias trazables a requerimientos, reglas, contratos, datos y pruebas; interacciones hexagonales; y diagrama SEQ o justificacion de reutilizacion. No se deben inventar evidencias, casos de prueba ni decisiones ADR. La aprobacion del tipo no aprueba fichas particulares.

Se incorpora **FDT — Ficha de Diseño Técnico de Funcionalidad** como tipo documental oficial. Una FDT representa una capacidad funcional o caso de uso técnico, no necesariamente un único endpoint. Puede vincular múltiples operaciones OpenAPI, eventos o procesos internos. Su perfil requiere `service_id`, `bounded_context_id`, `pack` y `skill`; referencias trazables a requerimientos, reglas, contratos, datos y pruebas; interacciones hexagonales; y diagrama SEQ o justificación de reutilización. No se deben inventar evidencias, casos de prueba ni decisiones ADR. La aprobación del tipo no implica aprobación de fichas particulares.

## Tipos documentales ampliados

El catalogo vigente incluye tipos documentales para UX/UI, Web, Mobile, DDD, microservicios, QA, requisitos, conocimiento de negocio, gestion de entrega, ideacion, calidad de KB, infraestructura y unidades de trabajo. Las tablas siguientes definen su semantica y reglas de uso.

Se incorporan sesenta y nueve tipos: ocho para especificaciones UX/UI, Web y Mobile, cinco para DDD y Microservicios (`ENT`, `ASIS`, `SVC`, `IMP`, `HCB`) y catorce para QA (`QFA`, `QTD`, `QTP`, `QTR`, `TSN`, `QTE`, `AT`, `QER`, `QQI`, `QDC`, `TDR`, `TDA`, `EXEC`, `EVD`) uno para Requisitos (`IMD`) cinco para Conocimiento de Negocio (`TRM`, `BCP`, `BO`, `STK`, `BCAP`) siete para Gestión de Entrega (`PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`), uno para Ideación (`SOL`) y uno para Calidad de KB (`QAR`) y veinte para Infraestructura (`IDS`, `IRQ`, `IBL`, `IIA`, `ITP`, `ICP`, `IFO`, `ISA`, `ICM`, `ITA`, `IOB`, `IRL`, `ISD`, `IAC`, `IDP`, `IRB`, `IAR`, `IHO`, `IXP`, `IXL`, `IGR`) y seis para Unidades de Trabajo de desarrollo asistido (`UOW`, `UCX`, `UCB`, `UCM`, `UAP`, `UWR`). Son **tipos documentales**, no equivalen a nombres de carpetas, funcionalidades, pantallas físicas ni tecnologías. Las siglas nuevas quedan incluidas en el catálogo vigente. `HOF` es un tipo aprobado de carácter transversal para un contrato de handoff versionado y consumible por Web/Mobile; no debe duplicarse como `WEB-HOF` y `MOB-HOF`. Los tipos `ADR`, `C4`, `SEQ`, `API`, `FDT`, `ASR` y `DSP` (y `ADR` también en Infraestructura) se reutilizan sin crear alias.

### Tipos y semántica

| Tipo | Nombre | Unidad documental | Productor preferente | Consumidor típico |
|---|---|---|---|---|
| `UXR` | UX Requirement | Requisito de experiencia verificable | `ux-requirements-flow-designer` | UX/UI, QA |
| `FLW` | User Flow | Flujo, estados, decisiones y excepciones | `ux-requirements-flow-designer` | UX/UI, Web, Mobile |
| `SCR` | Screen Specification | Pantalla o vista funcional y sus estados | `ui-screen-specification-designer` | UX/UI, Web, Mobile |
| `CMP` | UI Component Specification | Componente reutilizable del Design System | `ui-atomic-design-system-designer` | UX/UI, Web, Mobile |
| `TKN` | Design Token Specification | Tokens semánticos y convenciones de uso | `ui-atomic-design-system-designer` | UX/UI, Web, Mobile |
| `WEB` | Web Platform Technical Design | Aplicación, Shell, MicroUI, módulo o composición técnica Web | `web-platform-architecture-designer` y skills Web | Desarrollo Web |
| `MOB` | Mobile Application Technical Design | Aplicación, módulo o feature Mobile | `mobile-architecture-designer` y skills Mobile | Desarrollo Mobile |
| `HOF` | UX/UI Development Handoff Contract | Contrato de entrega de diseño aprobado por plataforma/alcance | `ux-ui-development-handoff` | Web y Mobile |
| `ENT` | Entity Specification | Entidad de dominio con identidad propia, dentro de un aggregate | `ddd-tactical-model-designer` | Microservicios, Datos |
| `ASIS` | As-Is Architecture Reconstruction | Reconstrucción evidenciada de la arquitectura existente de un servicio | `microservice-reconstruction-analyzer` | Arquitectura, Microservicios |
| `SVC` | Service Design Specification | Límites, responsabilidades y arquitectura hexagonal To-Be de un servicio | `microservice-boundary-architecture-designer` | Microservicios, Desarrollo |
| `IMP` | Impact and Evolution Analysis | Impacto, compatibilidad, migración y rollback entre As-Is y To-Be | `microservice-evolution-planner` | Arquitectura, Microservicios |
| `HCB` | Codebase Handoff Contract | Contrato de entrega de diseño de un microservicio a la KB y al repositorio de código | `microservice-codebase-handoff` | Desarrollo, coding agents |
| `QFA` | QA Feature Analysis Pack | Análisis QA trazable de un DSP: riesgos, ambigüedades, evidencia y superficies | `qa-feature-analyzer` | QA, diseño de pruebas |
| `QTD` | QA Test Design Pack | Paquete de diseño de pruebas: cobertura, trazabilidad, TSN y TC; sin estrategia ni plan (ver QTP) | `qa-test-design` | QA, revisión de diseño |
| `QTP` | QA Test Plan y priorización | Estrategia, plan de pruebas y priorización por riesgo y superficie | `qa-test-design` | QA |
| `QTR` | QA Test Design Review | Revisión independiente del diseño de pruebas | `qa-test-design-reviewer` | QA, orquestador |
| `TSN` | Test Scenario | Situación de prueba de alto nivel con 1..N Test Cases | `qa-test-design` | QA |
| `QTE` | QA Test Engineering Pack | Plan de ejecución, harness, ejecuciones y evidencia por superficie | `qa-agentic-test-engineer` | QA, revisión de ingeniería |
| `AT` | Automated Test | Implementación automatizada de exactamente un Test Case aprobado | `qa-agentic-test-engineer` | QA, CI/CD |
| `QER` | QA Test Engineering Review | Revisión independiente de implementación, ejecución y evidencia | `qa-agentic-test-reviewer` | QA, orquestador |
| `QQI` | QA Quality Intelligence Pack | Correlación de evidencia QA y recomendación de calidad | `qa-quality-intelligence` | QA, decisión de calidad |
| `QDC` | Quality Decision | Decisión de calidad humana registrada | `qa-sdlc-orchestrator` | QA, gestión |
| `TDR` | Test Data Requirement | Requisito de datos de prueba de un TC o TSN: entidades, relaciones, invariantes, clases de equivalencia, valores límite, estado esperado, aislamiento, privacidad y limpieza; no fija el mecanismo físico de provisión | `qa-test-design` | QA, ingeniería de pruebas |
| `TDA` | Test Data Asset | Activo que materializa un TDR: dataset, fixture, factory o generador, seed y limpieza | `qa-agentic-test-engineer` | QA, ejecución |
| `EXEC` | Test Execution | Una ejecución de un TC, con o sin AT, con su `execution_mode`, entorno, ejecutor, resultado y marcas de tiempo; cada re-ejecución genera una EXEC nueva | `qa-agentic-test-engineer` | QA, revisión, inteligencia de calidad |
| `EVD` | Test Evidence | Evidencia verificable de una EXEC: resultado observado, logs, capturas, reportes y artefactos con hash y procedencia | `qa-agentic-test-engineer` | QA, revisión |
| `UOW` | Unit of Work | Unidad de trabajo asignable a un developer que desarrolla asistido por un agente IA: un slice vertical de una User Story con alcance, límites, dependencias, criterios de terminado y trazabilidad | `uow-slice-designer` | Desarrollo, QA, Gestión |
| `UCX` | UOW Context Pack | Insumos versionados de una US para derivar UOW (US, DSP/SSP, FDT, API, BD, UX, ADR, handoffs existentes) con hechos, inferencias, supuestos y desconocidos separados | `uow-context-assembler` | Diseño de UOW |
| `UCB` | UOW Contract Binding | Enlace de una UOW con las operaciones API y los objetos de datos exactos (tablas, migraciones) y su coherencia | `uow-contract-binder` | Desarrollo, QA |
| `UCM` | UOW Codebase Map | Repositorio, rama y commit base, rutas permitidas y zonas prohibidas, convenciones y análisis del código existente para una UOW | `uow-codebase-mapper` | Desarrollo, agentes de código |
| `UAP` | UOW Agent Execution Plan | Plan de ejecución para el agente IA de una UOW: pasos verificables con prueba primero, verificación, condiciones de parada y protocolo de desviaciones | `uow-agent-execution-planner` | Desarrollo, agentes de código |
| `UWR` | UOW Readiness Review | Revisión independiente de completitud, trazabilidad y ausencia de alcance inventado del paquete de una UOW | `uow-readiness-reviewer` | Gestión, Desarrollo |
| `IMD` | Information Model | Modelo de información conceptual de negocio: conceptos, atributos de negocio, relaciones, cardinalidades y reglas, previo a cualquier modelo lógico o físico | `biz-information-model-designer` | Modelado de datos, DDD, Requisitos |
| `TRM` | Business Term | Término, concepto o sigla de negocio con nombre, sinónimos, definición y fuentes | `biz-glossary-curator` | Requisitos, Modelado de datos, DDD, UX |
| `BCP` | Business Context Pack | Contexto de negocio gobernado de una iniciativa: problema u oportunidad, alcance, restricciones, supuestos, riesgos y preguntas abiertas | `biz-context-objectives-analyst` | Requisitos, UX/UI, Arquitectura |
| `BO` | Business Objective | Objetivo de negocio con resultado esperado e indicadores (KPI) | `biz-context-objectives-analyst` | Requisitos, QA, Arquitectura |
| `STK` | Stakeholder | Actor o parte interesada con interés, responsabilidad e influencia | `biz-stakeholder-capability-mapper` | Requisitos, UX/UI |
| `BCAP` | Business Capability | Capacidad, cadena de valor o proceso de negocio y su relación con objetivos y actores | `biz-stakeholder-capability-mapper` | Requisitos, Arquitectura, DDD |
| `BSN` | Business Scenario | Secuencia de reglas de negocio aplicada por un actor sobre una capacidad, con precondiciones, pasos, excepciones y resultado, trazada a `BR` y `TRM` | `biz-scenario-modeler` | Requisitos, QA, UX/UI, Arquitectura |
| `PCH` | Project Charter | Acta de iniciativa: propósito, alcance, criterios de éxito, restricciones y partes interesadas | `mgt-charter-roadmap-planner` | Gestión, Requisitos, QA |
| `RMP` | Roadmap | Fases, hitos, criterios de salida y dependencias de una iniciativa | `mgt-charter-roadmap-planner` | Gestión, Arquitectura |
| `SSP` | Sprint Scope Pack | Alcance comprometido de un Sprint a partir de un DSP aprobado: objetivo, historias incluidas, dependencias, riesgos, compromiso y control GitLab (Milestone e Issues) | `mgt-backlog-iteration-planner` | Gestión, Desarrollo, QA |
| `STR` | Status Report | Informe de estado de un periodo: avance, esfuerzo, KPI, riesgos y decisiones requeridas | `mgt-progress-reporting-analyst` | Gestión, Dirección |
| `RSK` | Risk Register | Registro de riesgos, dependencias y bloqueos de una iniciativa | `mgt-risk-change-controller` | Gestión, Arquitectura, QA |
| `CHG` | Change Request | Solicitud de cambio con impacto, alternativas y decisión humana | `mgt-risk-change-controller` | Gestión, Requisitos, Arquitectura |
| `CLS` | Closure Report | Cierre de hito o iniciativa: resultado frente a criterios de éxito, lecciones aprendidas y transferencia | `mgt-release-closure-auditor` | Gestión, Operación |
| `SOL` | Solution Proposal | Propuesta de solución de una iniciativa de ideación en una de sus etapas (oportunidad, problema, portafolio de conceptos, concepto seleccionado, plan de experimentos o handoff a Requisitos), distinguida por `ideation_stage` | skills de `solution-ideation` | Requisitos, Arquitectura, UX/UI |
| `QAR` | KB Quality Report | Informe de calidad y consistencia de una KB OKF: hallazgos por dimensión, estado de los gates, evidencias, riesgos, excepciones y plan de remediación | `kb-quality-reporter` | Gestión, Arquitectura |
| `IRP` | Informe o Reporte genérico | Informe de análisis que presenta hallazgos sobre un alcance, separando hechos, inferencias, supuestos, vacíos y preguntas abiertas; no especifica pantallas ni reporta estado de gestión | `ddd-domain-discovery` y otros skills que necesiten un informe de análisis | Revisión humana, arquitectura, requisitos |
| `IDS` | Infrastructure Discovery | Hallazgos de descubrimiento de infraestructura: hechos, inferencias e incertidumbres | `infrastructure-assessment` | Arquitectura, Infraestructura |
| `IRQ` | Infrastructure Requirements | Requisitos de infraestructura derivados de requisitos funcionales, NFR y restricciones | `infrastructure-assessment` | Arquitectura, QA, Infraestructura |
| `IBL` | Infrastructure Baseline | Línea base de la infraestructura existente con su nivel de confianza | `infrastructure-assessment` | Arquitectura, Operación |
| `IIA` | Infrastructure Impact Assessment | Impacto de un cambio sobre infraestructura, consumidores y operación | `infrastructure-assessment` | Arquitectura, Gestión |
| `ITP` | Infrastructure Topology | Topología lógica y física, redes, zonas y alta disponibilidad | `infrastructure-architecture-design` | Arquitectura, Seguridad, Operación |
| `ICP` | Capacity Plan | Dimensionamiento y plan de capacidad por componente | `infrastructure-architecture-design` | Arquitectura, Operación, FinOps |
| `IFO` | FinOps Estimate | Estimación de costos y palancas de optimización de la infraestructura | `infrastructure-architecture-design` | Gestión, Arquitectura, Finanzas |
| `ISA` | Infrastructure Security Architecture | Arquitectura de seguridad de la infraestructura | `infrastructure-security-design` | Seguridad, Arquitectura, Operación |
| `ICM` | Infrastructure Control Matrix | Matriz de controles de seguridad con responsable, estado y evidencia | `infrastructure-security-design` | Seguridad, Auditoría |
| `ITA` | Infrastructure Threat Assessment | Evaluación de amenazas y riesgo de seguridad de la infraestructura | `infrastructure-security-design` | Seguridad, Arquitectura |
| `IOB` | Observability Design | Diseño de observabilidad: métricas, logs, trazas, alertas y dashboards | `infrastructure-operations-design` | Operación, Arquitectura |
| `IRL` | Reliability Design | Diseño de confiabilidad: modos de falla, redundancia y tolerancia a fallos | `infrastructure-operations-design` | Operación, Arquitectura |
| `ISD` | SLO and Disaster Recovery Plan | SLI/SLO, RTO/RPO y estrategia de recuperación ante desastres | `infrastructure-operations-design` | Operación, Gestión, Arquitectura |
| `IAC` | Infrastructure as Code Specification | Especificación de infraestructura como código: módulos, variables, estado y políticas | `infrastructure-delivery-design` | Desarrollo, Operación |
| `IDP` | Infrastructure Deployment Plan | Plan de despliegue de infraestructura por entorno | `infrastructure-delivery-design` | Operación, Gestión |
| `IRB` | Infrastructure Rollback Plan | Plan de reversión de un despliegue de infraestructura | `infrastructure-delivery-design` | Operación, Gestión |
| `IAR` | Infrastructure Architecture Review | Revisión independiente del diseño de infraestructura | `infrastructure-governance-handoff` | Arquitectura, Gestión |
| `IHO` | Infrastructure Handoff Contract | Contrato de entrega del diseño de infraestructura a Desarrollo y Operación | `infrastructure-governance-handoff` | Desarrollo, Operación |
| `IXP` | Infrastructure Execution Plan | Plan de ejecución del orquestador: tareas, dependencias y gates | `infrastructure-orchestrator` | Gestión, Arquitectura |
| `IXL` | Infrastructure Execution Log | Bitácora de ejecución: eventos, resultados, evidencias y errores | `infrastructure-orchestrator` | Gestión, Auditoría |
| `IGR` | Infrastructure Gate Register | Registro de gates con prerrequisitos y aprobaciones humanas | `infrastructure-orchestrator` | Gestión, Auditoría |

**Nota de control:** la ampliación aprobada contiene **sesenta y nueve** siglas nuevas: las ocho de UX/UI, Web y Mobile (incluido el handoff transversal `HOF`), cinco de DDD y Microservicios (`ENT`, `ASIS`, `SVC`, `IMP`, `HCB`) catorce de QA (`QFA`, `QTD`, `QTP`, `QTR`, `TSN`, `QTE`, `AT`, `QER`, `QQI`, `QDC`, `TDR`, `TDA`, `EXEC`, `EVD`) uno de Requisitos (`IMD`) cinco de Conocimiento de Negocio (`TRM`, `BCP`, `BO`, `STK`, `BCAP`) siete de Gestión de Entrega (`PCH`, `RMP`, `SSP`, `STR`, `RSK`, `CHG`, `CLS`), uno de Ideación (`SOL`) y uno de Calidad de KB (`QAR`) y veinte de Infraestructura (`IDS`, `IRQ`, `IBL`, `IIA`, `ITP`, `ICP`, `IFO`, `ISA`, `ICM`, `ITA`, `IOB`, `IRL`, `ISD`, `IAC`, `IDP`, `IRB`, `IAR`, `IHO`, `IXP`, `IXL`, `IGR`) y seis para Unidades de Trabajo de desarrollo asistido (`UOW`, `UCX`, `UCB`, `UCM`, `UAP`, `UWR`). `QTS` y `TC`, usadas también por QA, ya están en el catálogo aprobado. Los tipos previos no se alteran. Se aprueba `HOF` como tipo documental propio y transversal. `HOF` (handoff UX/UI) y `HCB` (handoff a codebase) son siglas distintas a propósito, para evitar colisión.

### Reglas de identidad y alcance

- Un `UXR` describe intención, restricciones y criterios de aceptación de experiencia; no sustituye `US`, `BR` ni `ASR`.
- Un `FLW` identifica inicio, objetivos, transiciones, permisos, happy path, excepciones y enlaces a `SCR`; no prescribe arquitectura de navegación.
- Un `SCR` registra contenido, interacciones, estados vacíos/carga/error, permisos, accesibilidad y referencias a prototipos; no reemplaza archivos Figma.
- Un `CMP` declara nivel Atomic Design (`atom`, `molecule`, `organism`, `template`, `page`), variantes, estados, propiedades, reglas de reutilización y accesibilidad; no impone widgets Flutter ni componentes Angular.
- Un `TKN` define nombre, categoría, valor/referencia, semántica, modos y plataformas; no contiene credenciales ni assets binarios.
- Un `WEB` especifica decisiones técnicas de composición, Shell/MicroUIs o frontend modular, routing, state, ownership, BFF y contratos API. **Bounded Context ≠ MicroUI ≠ API**; justificar delimitación y alternativas.
- Un `MOB` especifica features/módulos, navegación, estado, capacidades nativas, persistencia, offline/sync, seguridad y compatibilidad Android/iOS. No hereda automáticamente la partición de MicroUIs Web.
- Un `HOF` declara baseline de `UXR`/`FLW`/`SCR`/`CMP`/`TKN`, prototipos aprobados, plataformas destinatarias, restricciones, decisiones pendientes y evidencia de aceptación. Los cambios se versionan y requieren nueva evaluación de impacto.
- Un `ENT` especifica una entidad con identidad dentro de un `AGG`: atributos, invariantes y ciclo de vida. No es una tabla ni un `VO`, y debe enlazar a su `AGG` y `BC`.
- Un `ASIS` documenta lo observado en un servicio existente, citando archivo y commit por afirmación. Distingue hecho de inferencia y no describe el diseño deseado.
- Un `SVC` define responsabilidades, ownership, adaptadores, puertos y dependencias de un servicio. Un `BC` no equivale obligatoriamente a un servicio y no redefine el DDD aprobado.
- Un `IMP` compara As-Is y To-Be: breaking changes, consumidores, datos, migraciones, rollout, rollback y riesgos. En Greenfield puede justificar N/A.
- Un `HCB` mapea artefactos de la KB `codebase/<MICROSERVICIO>` al repositorio, con rama destino, ref, commit, ADR, acción y validación. La CLI valida su estructura, no la aprobación humana.
- Un `QFA` transforma un DSP validado en riesgos (`RISK`), ambigüedades (`AMB`), evidencia y superficies; no produce TSN, TC ni AT y no modifica el DSP.
- Un `QTD` agrupa matriz de cobertura, trazabilidad, `TSN` y `TC`. La estrategia (`QTS`), el plan y la priorización se documentan en `QTP`, un documento aparte que precede al `QTD`. Un `TSN` tiene 1..N `TC`; un `TC` aprobado exige oracle, datos y precondiciones, y no implica automatización.
- Un `QTR` revisa el `QTD` sin rediseñarlo y debe emitirlo un revisor distinto del autor. Un `QER` hace lo mismo sobre el `QTE`.
- Un `QTE` documenta la implementación y ejecución de TC aprobados por superficie. Un `AT` referencia exactamente un TC primario y no puede existir sin un TC aprobado.
- Un `QQI` correlaciona evidencia y recomienda `READY`, `READY_WITH_RISK`, `NOT_READY` o `INSUFFICIENT_EVIDENCE`; no aprueba el release. Un `QDC` registra la decisión humana final y no la sustituye ningún gate automático.
- Un `TDR` define QUÉ datos requiere un TC o TSN y no elige el mecanismo físico de provisión; un `TDA` define CÓMO se crea o provee ese dato y siempre referencia al menos un `TDR`. Cadena: `TC → TDR → TDA → EXEC → EVD`. Se prefieren datos sintéticos; no se persisten secretos ni PII real no autorizada, y se aplica masking cuando corresponda. Un TC manual puede tener `TDR` sin `TDA` solo si declara quién provee el dato.
- Un `EXEC` registra una ejecución concreta de un `TC`. Su `execution_mode` (`MANUAL`, `AUTOMATED_STANDALONE` o `AUTOMATED_CICD`) pertenece a la `EXEC` y no al TC; `MANUAL` no requiere `AT` y los otros dos modos lo exigen. En `AUTOMATED_CICD` registra, cuando existan, proveedor, `pipeline_id`/URL, `job_id`/nombre, `commit_sha` y rama o tag, sin inventar identificadores. Cada re-ejecución crea una `EXEC` nueva y conserva el historial. Distingue falla funcional de falla de pipeline o de entorno.
- Un `EVD` pertenece a una `EXEC`, referencia sus artefactos con ruta y `sha256` y no contiene secretos ni PII no autorizada.
- Una `UOW` es la unidad que se asigna a un developer: un slice vertical de una US (puede haber varias por US) que un solo developer con su agente puede completar. Referencia por ID y versión los documentos de origen (`US`, `DSP`, `SSP`, `FDT`, `API`, `LDM`, `PDM`, `DBM`, `HOF`, `WEB`, `MOB`, `HCB`, `ADR`, `ASR`) sin copiarlos ni redefinirlos; no define requisitos, diseño de API ni modelo de datos. Su paquete (`UOW`, `UCB`, `UCM`, `UAP`, `UWR` y `uow-package.yaml`) se aprueba como una unidad con decisión humana ligada a su digest; la asignación es de Gestión. Se ubica en `management/uows/`.
- Un `UCX` distingue `FACT`, `INFERENCE`, `ASSUMPTION` y `UNKNOWN` y cita la fuente versionada de cada hecho; no decide el diseño. Un `UCB` solo enlaza contratos existentes y declara las brechas: no inventa operaciones, campos ni tablas. Un `UCM` fija la referencia base y los límites de escritura del agente; las rutas de código se resuelven por ADR y repositorio. Un `UAP` ordena pasos con prueba primero y verificación, y no incluye secretos ni acciones destructivas o en PROD sin autorización. Un `UWR` lo emite un revisor distinto del autor y es una propuesta: no aprueba la UOW.
- Un `IMD` describe conceptos de negocio y sus relaciones en lenguaje de negocio, con trazabilidad a reglas (`BR`) y términos del glosario; no define tipos de dato, claves ni tablas, que corresponden a `LDM`/`PDM`. Se ubica en `business/information-model/IMD-NNN-<slug>.md`.
- Un `TRM` define un término, concepto o sigla de negocio con significado específico; no incluye identificadores de artefactos ni vocabulario del método documental. Se ubica en `business/terms/TRM-NNN-<slug>.md` y se cataloga en `business/terms/CTLG-TRM.md` (tipo `CTLG`, ver la sección Catalogos). No se genera `index.md` para los términos.
- Un `BCP` compone y referencia el contexto de negocio de una iniciativa; no define requisitos, historias de usuario, ASR ni diseño. Va en `business/context-packs/`.
- Un `BO` describe un objetivo y sus KPI; un `STK`, una parte interesada; un `BCAP`, una capacidad o proceso de negocio. Ninguno impone solución técnica. Van en `business/objectives/`, `business/stakeholders/` y `business/capabilities/`.
- Un `PCH` y un `RMP` planifican la entrega y no definen requisitos ni arquitectura; un `SSP` organiza el trabajo de un Sprint a partir de un `DSP` aprobado sin ampliar su alcance; el compromiso es una decisión humana. Un `STR` informa con datos trazables y no redefine KPI; un `RSK` registra riesgos con dueño (una instancia por iniciativa); un `CHG` es una solicitud cuya decisión registra quién y cuándo; un `CLS` cierra con evidencia. Van en `management/{charters,roadmaps,sprints,status-reports,risks,changes,closure}/`.
- Un `SOL` describe una propuesta de solución en una etapa de ideación (`ideation_stage`: `opportunity`, `problem`, `portfolio`, `concept`, `experiment` o `handoff`). No es un requisito aprobado ni un `DSP`: Requisitos reconstruye su propio `RCP` a partir de él. **Tipo único aprobado:** las etapas se distinguen mediante `ideation_stage`; cualquier desagregación futura requiere control de cambios.
- Un `QAR` consolida los hallazgos, los gates y la evidencia de una auditoría de KB. No aprueba la publicación, que es una decisión humana, ni modifica la KB auditada.
- Los tipos de Infraestructura (`IDS`, `IRQ`, `IBL`, `IIA`, `ITP`, `ICP`, `IFO`, `ISA`, `ICM`, `ITA`, `IOB`, `IRL`, `ISD`, `IAC`, `IDP`, `IRB`, `IAR`, `IHO`, `IXP`, `IXL`, `IGR`) describen documentos de diseño de infraestructura, uno por artefacto producido por el plugin `infra-architecture-design`; el ADR de infraestructura usa el tipo `ADR` aprobado, sin alias. No definen requisitos de negocio, historias ni código. Distinguen hecho, inferencia y supuesto; no inventan evidencia, aprobaciones ni valores de precio o capacidad; toda decisión, aceptación de riesgo o *go/no-go* es humana y se registra con quién y cuándo. Los secretos no se incluyen en ningún documento. Se ubican en `knowledge/infrastructure/<artefacto>/`. `IXP`, `IXL` e `IGR` documentan el control del orquestador; el estado operativo ejecutable (`execution-plan.json`, `task-result.yaml`) no es un documento OKF.

### Perfiles condicionales

| Tipo | Metadatos adicionales requeridos cuando apliquen | Secciones mínimas del cuerpo |
|---|---|---|
| UXR | `product`, `pack`, `skill`; `related` hacia US/BR | objetivo, usuario/rol, necesidad, criterios de aceptación, dependencias |
| FLW | `product`, `pack`, `skill`; `related` hacia UXR/SCR | actores, precondiciones, flujo principal, alternativas, errores, permisos |
| SCR | `product`, `pack`, `skill`; `related` hacia FLW/CMP | propósito, elementos, estados, interacciones, accesibilidad, referencias de diseño |
| CMP | `pack`, `skill`; `product` si no es global | Atomic level, variantes, propiedades, estados, accesibilidad, reutilización |
| TKN | `pack`, `skill`; `product` si no es global | taxonomía, tokens, semántica, modos, plataforma, compatibilidad |
| WEB | `product`, `pack`, `skill`; `bounded_context_id` si corresponde | alcance, opciones y ADR, composición, ownership, integraciones, seguridad, despliegue |
| MOB | `product`, `pack`, `skill`; `bounded_context_id` si corresponde | alcance, módulos/features, navegación, estado, offline/sync, seguridad, release |
| HOF | `product`, `pack`, `skill`; `related` hacia baseline UX/UI | versiones, aceptación, trazabilidad, restricciones, entregables y destinatarios |
| ENT | `bounded_context_id`, `pack`, `skill`; `related` hacia AGG | identidad, atributos, invariantes, ciclo de vida |
| ASIS | `service_id`, `pack`, `skill`; `product` si aplica | alcance, evidencia (archivo y commit), componentes, dependencias, hechos e inferencias, incertidumbres |
| SVC | `service_id`, `pack`, `skill`; `related` hacia BC/CTX y ADR | responsabilidades, ownership, adaptadores y puertos, dependencias, C4, NFR |
| IMP | `service_id`, `pack`, `skill`; `related` hacia ASIS/SVC | cambios, compatibilidad, consumidores, migración, rollout, rollback, riesgos |
| HCB | `service_id`, `pack`, `skill`; `related` hacia ADR | destino KB, repositorio, ref y commit, artefactos, validación, controles de aprobación |
| QFA | `product`, `pack`, `skill`; `related` hacia DSP/US | alcance, riesgos, ambigüedades, evidencia, superficies, readiness |
| QTD | `product`, `pack`, `skill`; `related` hacia QFA y QTP | cobertura, trazabilidad, escenarios y casos |
| QTP | `product`, `pack`, `skill`; `related` hacia QTD | alcance del plan, priorización, ambientes, entradas y salidas |
| QTR | `product`, `pack`, `skill`; `related` hacia QTD | hallazgos con severidad, acciones correctivas, revisión humana requerida |
| TSN | `product`, `pack`, `skill`; `related` hacia RISK/US | situación, riesgo asociado, casos derivados, superficie |
| QTE | `product`, `pack`, `skill`; `related` hacia QTD | plan de ejecución, harness, ejecuciones, evidencia, defectos candidatos |
| AT | `product`, `pack`, `skill`; `related` hacia un TC | TC primario, framework, datos, ejecución, evidencia |
| QER | `product`, `pack`, `skill`; `related` hacia QTE | hallazgos, trazabilidad AT-TC, evidencia, seguridad, acciones correctivas |
| QQI | `product`, `pack`, `skill`; `related` hacia QTE/QER | procedencia, trazabilidad evaluada, recomendación, suficiencia de evidencia |
| QDC | `product`, `pack`, `skill`; `related` hacia QQI | decisión, responsable humano, riesgos aceptados, evidencia revisada |
| TDR | `product`, `pack`, `skill`; `related` hacia TC/TSN/RISK | entidades y datos requeridos, invariantes, clases de equivalencia y límites, combinaciones, estado esperado, aislamiento, privacidad y masking, limpieza, tipo de fuente |
| TDA | `product`, `pack`, `skill`; `related` hacia TDR | TDR que materializa, tipo y ubicación del activo, provisión o generación, determinismo, control de PII y secretos, limpieza, validación |
| EXEC | `product`, `pack`, `skill`; `execution_mode`; `related` hacia TC/AT/TDA | modo de ejecución, TC y AT, TDA usados, entorno, ejecutor, proveedor y pipeline/job si es CI/CD, commit, resultado, marcas de tiempo, referencias a EVD |
| EVD | `product`, `pack`, `skill`; `related` hacia EXEC | EXEC de origen, tipo de evidencia, ubicación y `sha256`, resultado observado, procedencia |
| UOW | `product`, `pack`, `skill`; `us_ref`; `mode`; `scope_state`; `related` hacia US/DSP/UCX/UCB/UCM/UAP | objetivo y resultado, alcance e inclusiones y exclusiones, criterios de aceptación cubiertos, contratos y datos, mapa de código, dependencias, plan para el agente, criterios de terminado, dimensión, riesgos y preguntas abiertas, handoff a QA, trazabilidad |
| UCX | `product`, `pack`, `skill`; `us_ref`; `mode`; `related` hacia US/DSP | alcance y modo, insumos versionados, hechos, inferencias, supuestos, desconocidos, conflictos entre fuentes, línea base |
| UCB | `product`, `pack`, `skill`; `uow_ref`; `related` hacia UOW/FDT/API/LDM/PDM/DBM | operaciones API vinculadas, objetos de datos, mapeo API a BD, eventos, brechas y coherencia, contratos que no cambian |
| UCM | `product`, `pack`, `skill`; `uow_ref`; `service_id`; `related` hacia UOW/HCB/ADR | repositorio y referencia base, rutas permitidas, zonas prohibidas, convenciones y ADR aplicables, análisis del código existente, migraciones y orden |
| UAP | `product`, `pack`, `skill`; `uow_ref`; `related` hacia UOW/UCB/UCM | perfil de ejecución, preparación del entorno, pasos verificables, verificación y criterios de terminado, condiciones de parada, protocolo de desviaciones, guardrails, entrega |
| UWR | `product`, `pack`, `skill`; `uow_ref`; `related` hacia UOW/UCB/UCM/UAP | alcance revisado, completitud, trazabilidad, hallazgos con severidad, alcance inventado, preguntas abiertas, recomendación propuesta |
| IMD | `product`, `pack`, `skill`; `related` hacia BR/RCP | conceptos, relaciones y cardinalidades, reglas asociadas, fuentes, preguntas abiertas |
| TRM | `product`, `pack`, `skill`; `related` hacia BR/IMD si aplica | nombre, sinónimos, definición, fuentes con nivel, notas |
| BCP | `product`, `pack`, `skill`; `related` hacia BO/STK/BCAP | problema u oportunidad, alcance, restricciones, supuestos, riesgos, preguntas abiertas, readiness |
| BO | `product`, `pack`, `skill`; `related` hacia BCP | objetivo, resultado esperado, KPI con línea base y meta, fuentes |
| STK | `product`, `pack`, `skill`; `related` hacia BCP/BCAP | rol, interés, responsabilidad, influencia, fuentes |
| BCAP | `product`, `pack`, `skill`; `related` hacia BO/STK | capacidad o proceso, actores, objetivos asociados, estado AS-IS, fuentes |
| BSN | `product`, `pack`, `skill`; `related` hacia BR/TRM/IMD/BCP | actor, capacidad, precondiciones, pasos con regla BR asociada, excepciones, resultado, términos TRM, fuentes, preguntas abiertas |
| PCH | `product`, `pack`, `skill`; `related` hacia BO/BCP | propósito, alcance y exclusiones, criterios de éxito, restricciones, partes interesadas, preguntas abiertas |
| RMP | `product`, `pack`, `skill`; `related` hacia PCH | hitos con criterio de salida, fases, dependencias, preguntas abiertas |
| SSP | `product`, `pack`, `skill`; `dsp_id`; `related` hacia DSP/RMP/US | Sprint Goal, alcance incluido y exclusiones, dependencias, riesgos, historias, compromiso, trazabilidad, control GitLab (Milestone) |
| STR | `product`, `pack`, `skill`; `related` hacia SSP/RSK | estado y criterio, avance, esfuerzo, KPI, riesgos y cambios abiertos, calidad de datos, decisiones requeridas |
| RSK | `product`, `pack`, `skill`; `related` hacia PCH | riesgos con dueño y respuesta, dependencias y bloqueos, escalas usadas |
| CHG | `product`, `pack`, `skill`; `related` hacia PCH/RSK | descripción, impacto, alternativas, decisión (quién y cuándo) |
| CLS | `product`, `pack`, `skill`; `related` hacia PCH/STR | resultado frente a criterios de éxito, desvíos, preparación de entrega, lecciones aprendidas |
| SOL | `product`, `pack`, `skill`; `ideation_stage`; `related` hacia SOL/BCP/BO | etapa, hipótesis y evidencia con su incertidumbre, alternativas, decisión humana de selección, preguntas abiertas |
| QAR | `pack`, `skill`; `related` hacia el snapshot auditado | alcance y snapshot (repositorio, rama, commit), hallazgos por dimensión, gates y evidencias, riesgos y excepciones |
| IDS | `product` si aplica, `pack`, `skill`; `related` hacia RCP/ASIS | alcance y modo, hechos observados, inferencias, incertidumbres y vacíos, fuentes y evidencia |
| IRQ | `product` si aplica, `pack`, `skill`; `related` hacia IDS/ASR/RCP | requisitos de infraestructura, requisitos no funcionales, restricciones, criterios de aceptación, trazabilidad |
| IBL | `product` si aplica, `pack`, `skill`; `related` hacia IDS | alcance y fecha de línea base, inventario de componentes, topología actual, nivel de confianza de la evidencia, brechas conocidas |
| IIA | `product` si aplica, `pack`, `skill`; `related` hacia IBL/IRQ | cambio evaluado, componentes y consumidores afectados, compatibilidad y migración, riesgos, mitigación y rollback |
| ITP | `product` si aplica, `pack`, `skill`; `related` hacia IRQ/IBL/ADR | alcance, topología lógica y física, redes y conectividad, zonas, alta disponibilidad y ubicación, decisiones y riesgos |
| ICP | `product` si aplica, `pack`, `skill`; `related` hacia IRQ/ITP | demanda y supuestos de carga, dimensionamiento por componente, margen y crecimiento, límites y cuellos de botella, método de cálculo |
| IFO | `product` si aplica, `pack`, `skill`; `related` hacia ICP/ITP | alcance de costos, modelo de costos, estimación por componente, escenarios y sensibilidad, palancas de optimización, supuestos y exclusiones |
| ISA | `product` si aplica, `pack`, `skill`; `related` hacia ITP/IRQ/ITA | alcance y activos, zonas y segmentación, identidad y acceso, protección de datos, monitoreo y respuesta, cumplimiento y decisiones |
| ICM | `product` si aplica, `pack`, `skill`; `related` hacia ISA/ITA | marco de referencia, controles, mapeo a requisitos y riesgos, brechas y excepciones, evidencia de implementación |
| ITA | `product` si aplica, `pack`, `skill`; `related` hacia ISA/ITP | alcance y activos, amenazas identificadas, valoración del riesgo, mitigaciones y controles, riesgo residual y aceptación |
| IOB | `product` si aplica, `pack`, `skill`; `related` hacia ITP/ISD | alcance y servicios, métricas, logs y trazas, alertas y umbrales, dashboards y retención, responsables y runbooks |
| IRL | `product` si aplica, `pack`, `skill`; `related` hacia ITP/ISD | objetivos de disponibilidad, modos de falla, redundancia y alta disponibilidad, degradación y tolerancia a fallos, pruebas de resiliencia |
| ISD | `product` si aplica, `pack`, `skill`; `related` hacia IRL/IRQ | sli y slo, presupuesto de error, rto y rpo, estrategia de recuperación, pruebas de dr y responsables |
| IAC | `product` si aplica, `pack`, `skill`; `related` hacia ITP/ICP/ISA | alcance y entornos, módulos y recursos, variables y secretos, estado y backend, validación y políticas |
| IDP | `product` si aplica, `pack`, `skill`; `related` hacia IAC/IRB | alcance y entornos, prerrequisitos y ventanas, pasos y orden, verificación posterior, criterios de go/no-go |
| IRB | `product` si aplica, `pack`, `skill`; `related` hacia IDP | disparadores, pasos de reversión, datos y estado, verificación, responsables y comunicación |
| IAR | `product` si aplica, `pack`, `skill`; `related` hacia ITP/ISA/IAC | alcance revisado, hallazgos, cumplimiento frente a requisitos, acciones correctivas, decisión de revisión |
| IHO | `product` si aplica, `pack`, `skill`; `related` hacia IAR/ADR | destinatarios y alcance, artefactos entregados, decisiones y adr, restricciones y pendientes, aceptación |
| IXP | `product` si aplica, `pack`, `skill`; `related` hacia IGR | iniciativa y modo, tareas y dependencias, gates, responsables, estado general |
| IXL | `product` si aplica, `pack`, `skill`; `related` hacia IXP | eventos, resultados por tarea, evidencias, errores y bloqueos |
| IGR | `product` si aplica, `pack`, `skill`; `related` hacia IXP | gates definidos, prerrequisitos, aprobaciones, excepciones |

No hacer `bounded_context_id` obligatorio para todos los `WEB`/`MOB`: una composición puede abarcar varios contextos. Cuando corresponda a múltiples BC, usar `related` y enlaces Markdown hacia cada `BC`/`CTX`; mantener `bounded_context_id` únicamente si hay un BC propietario inequívoco. Los IDs documentales deben ser únicos dentro de la KB y estables ante cambios de ruta.

### Ubicación y relación con el orchestrator

```text
.comsatel/<pack-name>/runs/<run-id>/  # planes, estado, gates y evidencias operativas
 design/ux-ui/<run-id>/               # UXR, FLW, SCR, CMP, TKN, HOF
 design/web/<run-id>/                 # WEB y artefactos técnicos reutilizados
 design/mobile/<run-id>/              # MOB y artefactos técnicos reutilizados
```

Las rutas son convenciones de trabajo, no IDs OKF ni garantías de publicación. Los entregables conceptuales se publican en las KB gobernadas por Merge Request; las referencias a Figma, Stitch o Claude Design se registran como recursos/procedencia, no como evidencia de aprobación automática.

### Compatibilidad y migración

1. Inventariar documentos existentes, detectar colisiones de siglas y distinguir tipos de etiquetas informales.
2. Las nuevas siglas y perfiles condicionales requieren aprobación y actualización coordinada del catálogo, validadores y templates.
3. Usar `v0.1.0-stable` como baseline normativa vigente y mantener compatibilidad de lectura para documentos existentes.
4. Permitir lectura de tipos desconocidos por consumidores OKF; exigir catálogo aprobado solo en pipelines de publicación COMSATEL.
5. No migrar automáticamente documentos históricos ni fabricar `verified`, `sources` o decisiones humanas.
6. Versionar cambios a `HOF` y comprobar impacto en handoffs consumidos por Web/Mobile.

## Catálogo corporativo vigente de `type`

| Sigla | Artefacto |
|---|---|
| STD | Estándar |
| ADR | Architecture Decision Record |
| ASR | Architecturally Significant Requirement |
| BC | Bounded Context |
| CTX | Context Map |
| AGG | Aggregate Specification |
| VO | Value Object Specification |
| EVT | Domain Event Specification |
| RCP | Requirements Context Pack |
| US | User Story |
| BR | Business Rule |
| LDM | Logical Data Model |
| PDM | Physical Data Model |
| DBM | Database Migration |
| DBR | Database Reconstruction |
| API | API Contract |
| EPS | Endpoint Specification |
| FDT | Ficha de Diseño Técnico de Funcionalidad |
| ERR | Error Catalog |
| C4 | C4 Architecture View |
| SEQ | Sequence Diagram |
| DSP | Development Scope Pack |
| QTS | QA Test Strategy |
| TC | Test Case |
| RUN | Runbook |

Este cuadro y las tablas complementarias forman conjuntamente el catálogo corporativo vigente. Las siglas adicionales existentes en las KB (por ejemplo, `HUC`) requieren registro y conciliación mediante control de cambios; no se renombran ni invalidan automáticamente los documentos históricos. El nombre de `DSP` se concilió como *Development Scope Pack* (paquete de alcance candidato a Sprint, derivado de un `RCP` y de historias aprobadas); el nombre anterior *Detailed Solution Proposal* se retira y la sigla no cambia. Las siglas que existen solo en las KB y no las produce ningún pack (por ejemplo `MCP`, `PI`, `EEP`, `UST`, `ECP`) siguen pendientes de registro. No crear tipos nuevos sin aprobación.

## Niveles de validación

1. **OKF:** YAML válido, `type` no vacío y reglas de `index.md`/`log.md`.
2. **Perfil COMSATEL:** campos requeridos, tipos, enumeraciones, IDs, actores, SemVer y fechas con zona.
3. **Publicación:** procedencia, enlaces, Mermaid renderizable, evidencia de revisión y gates aprobados.

El MCP debe continuar leyendo documentos mínimos OKF y extensiones desconocidas. Los requisitos corporativos estrictos aplican a productores y pipelines de publicación.

## Migración

Inventariar metadatos reales; mapear `artifact_type` a `type` sin sobrescribir valores incompatibles; separar estados operativos de los documentales; preservar claves desconocidas; no fabricar `verified` ni `sources`; publicar cambios por Merge Request con informe y rollback. `plan.yaml`, `plan-status.yaml` y `task-status.yaml` en `./.comsatel/[pack-name]/` no son documentos conceptuales OKF.

## Historial de versiones

| Version | Estado | Registro |
|---|---|---|
| 0.1.0 | stable | Inicio de la linea base vigente |

## Perfiles de arquitectura

Los perfiles de arquitectura forman parte del catalogo vigente y no cambian la semantica de los tipos preexistentes.

Se incorporan cuatro tipos documentales para los skills de `architecture-design` 0.1.0. Son aditivos: ningún tipo preexistente cambia de semántica.

| Tipo | Nombre | Unidad documental | Productor | Consumidor típico | Campos adicionales obligatorios |
|---|---|---|---|---|---|
| `ACP` | Architecture Context Pack | Contexto de arquitectura validado para un ciclo: alcance, fuentes, AS-IS, impacto, hechos separados de inferencias, supuestos y desconocidos | `architecture-context-and-evidence-designer` | Arquitectura, ASR y decisiones | `product`, `pack`, `skill`; `related` hacia RCP, C4, ASR |
| `CFR` | Conformance Report | Evaluación de reglas de conformidad, evidencia inspeccionada, fitness y drift | `architecture-conformance-assessor`, `ddd-domain-contract-validator` | Arquitectura, gestión | `product`, `pack`, `skill`; `related` hacia ADR, C4, ASR |
| `ADH` | Architecture Development Handoff | Decisiones de arquitectura transferidas a desarrollo, sin reabrirlas: restricciones, límites, interfaces y criterios de aceptación | `architecture-development-handoff` | Desarrollo, coding agents | `product`, `pack`, `skill`; `related` hacia ADR, ASR, C4, SVC |
| `GOV` | Architecture Governance Record | Señales de cambio, impacto, modelo de gobierno y curaduría de conocimiento de la arquitectura | `architecture-evolution-governor` | Arquitectura, gestión | `product`, `pack`, `skill`; `related` hacia ADR, CHG, IMP |

- **ACP:** ámbito, fuentes con procedencia, hechos, inferencias, supuestos y desconocidos separados, baseline As-Is, impacto, preguntas abiertas y validación humana en G1.
- **CFR:** reglas evaluadas, evidencia inspeccionada por regla, resultado por regla, fitness y drift, excepciones aprobadas y validación humana en G4.
- **ADH:** decisiones heredadas con referencia a su ADR, restricciones, límites de componente, interfaces, criterios de aceptación de arquitectura, pendientes y validación humana en G6.
- **GOV:** señales de cambio, impacto por componente, roles y cadencia de revisión, criterios de obsolescencia, curaduría de conocimiento y validación humana en G5.
- **Orquestador:** `architecture-design-orchestrator` no produce tipo OKF. Sus salidas (planes, estado, contratos de ruta y registros de gate) son operativas, según la sección *Migración*.

### Perfil de cuerpo ADR

Todo `ADR` debe incluir:

- **Escenarios de calidad afectados:** `QA-nn` de seis partes (fuente, estímulo, artefacto, entorno, respuesta, medida) y prioridad. Medida sin fuente: `[PENDIENTE: arquitecto]`.
- **Opciones consideradas:** al menos dos, incluida la de no hacer nada.
- **Representación visual:** al menos un diagrama Mermaid, o la línea `Visual: no aplica — <motivo>`. Cada elemento del diagrama tiene identificador `E-nn` y una fila en el catálogo de elementos con descripción y marca de punto de variación.
- **Puntos de variación:** cada `VP-nn` con dimensión, variantes, momento de vinculación (diseño, construcción, despliegue o ejecución) y responsable.
- **Evaluación ATAM ligera:** registros de sensibilidad, compromiso, riesgo y no-riesgo que referencian un `QA-nn` existente, o la justificación `Sin registros de tipo <X>: <motivo>`.

La conformidad se comprueba con `scripts/validate_adr_body.py` del plugin `architecture-design`. La validación Mermaid (`--render`) es local.

## Revision de diseno de datos

`DDR` (Data Design Review) lo produce `dm-data-design-validator`. Registra consistencia LDM/PDM/DBM, trazabilidad a ADR y FDT, tenancy, seguridad, evidencia, riesgos, incertidumbres y propuesta de gate. Registra hallazgos; no aprueba el diseno.

Se incorpora el tipo `DDR` (Data Design Review), que produce `dm-data-design-validator`. Es aditivo.

| Tipo | Nombre | Unidad documental | Productor | Consumidor típico | Campos adicionales obligatorios |
|---|---|---|---|---|---|
| `DDR` | Data Design Review | Revisión de diseño de datos: consistencia LDM/PDM/DBM, trazabilidad a ADR y FDT, tenancy, seguridad y evidencia, con riesgos, incertidumbres y propuesta de gate | `dm-data-design-validator` | Arquitectura, modelado de datos, gestión | `product`, `pack`, `skill`; `related` hacia LDM, PDM, DBM, ADR, FDT |

- Un `DDR` no aprueba el diseño: registra hallazgos y propone el gate. La aprobación es humana.

## Salidas de skills especialistas

Todo documento conceptual Markdown independiente producido por un skill especialista debe llevar `type` registrado y cumplir el perfil documental completo. Ninguna salida de un especialista queda exenta por llamarse auxiliar, informe, handoff o evidencia. Las salidas operativas de ejecución (planes, ledgers, registros de gate y resultados de tarea) son propiedad del orchestrator y no son documentos conceptuales OKF. Los archivos reservados `index.md` y `log.md` conservan sus reglas específicas. Si no existe un tipo semánticamente correcto, se integra el contenido en un documento con tipo aprobado o se solicita una decisión de gobierno; no se etiqueta con un tipo falso.

La matriz de ownership de datos forma parte del `LDM` que completa `dm-logical-model-designer`; no se publica como documento independiente sin tipo. Las revisiones de diseño de datos usan `DDR`.

## Salidas de skills especialistas

Todo documento conceptual Markdown independiente producido por un skill especialista debe llevar `type` registrado y cumplir el perfil documental completo. Ninguna salida de un especialista queda exenta por llamarse auxiliar, informe, handoff o evidencia. Las salidas operativas de ejecución (planes, ledgers, registros de gate y resultados de tarea) son propiedad del orchestrator y no son documentos conceptuales OKF. Los archivos reservados `index.md` y `log.md` conservan sus reglas específicas. Si no existe un tipo semánticamente correcto, se integra el contenido en un documento con tipo aprobado o se solicita una decisión de gobierno; no se etiqueta con un tipo falso.

La matriz de ownership de datos forma parte del `LDM` que completa `dm-logical-model-designer`; no se publica como documento independiente sin tipo. Las revisiones de diseño de datos usan `DDR`.

## Referencia

[Especificación canónica de Google OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md).

## Perfil documental DDD

- **AGG:** documentar Bounded Context propietario, Aggregate Root, Entities internas, invariantes, comandos, límites transaccionales y relaciones. `bounded_context_id` es obligatorio.
- **VO:** documentar Bounded Context propietario, atributos, restricciones, semántica de igualdad por valor e inmutabilidad. `bounded_context_id` es obligatorio.
- **EVT:** documentar Bounded Context productor, hecho de negocio en pasado, disparador, payload, versión, causalidad y consumidores conocidos o por definir. `bounded_context_id` es obligatorio. Un Domain Event no implica publicación como Integration Event.
- Para los tres tipos, `pack` y `skill` son obligatorios en los artefactos producidos por el DDD Domain Design Pack. `related` y enlaces Markdown vinculan BC/AGG/VO/EVT cuando corresponda.
- Las especificaciones son documentos conceptuales sujetos a los tres niveles de validación; los estados operativos del orchestrator permanecen separados.
- La fecha de esta revisión es una fecha de edición, no una verificación histórica.

## Perfil documental FDT

- `FDT` exige `service_id`, `bounded_context_id`, `pack` y `skill`.
- La ficha identifica capacidad, pre/postcondiciones, requisitos y reglas de negocio, operaciones OpenAPI/AsyncAPI y `operationId` cuando corresponda, datos de dominio y persistencia, interacciones inbound/outbound, diagramas de secuencia o referencias, seguridad, errores, consistencia, observabilidad, escenarios de prueba, impacto y handoff.
- Referenciar artefactos de QA y Data Design aprobados; lo no disponible se registra como dependencia o bloqueo, no se inventa.
- Las rutas de código se resuelven mediante ADR y repositorio; la FDT es especificación KB, no sustituto de `api.yaml`.

## Tipos de Business Intelligence

Los seis tipos de BI forman parte del catalogo vigente. Cada sigla conserva un unico significado en esta norma y en las copias de los packs.

Los seis tipos son normativos y cada sigla tiene un único significado en esta norma y en las copias de los packs.

El catálogo define seis tipos documentales para el pack `bi-analytics`, uno por etapa del flujo BI (G1 a G6):

| Sigla | Nombre | Unidad documental | Productor | Consumidor típico |
|---|---|---|---|---|
| `BIC` | BI Decision Context | Preguntas de negocio, decisiones soportadas, audiencias y alcance analítico de una iniciativa | `bi-decision-context-analyst` | Gestión, Analítica, Requisitos |
| `KPI` | KPI Definition | Definición formal de un indicador: fórmula, grano, dimensiones, owner, umbrales y trazabilidad a decisiones | `bi-kpi-definition-designer` | Analítica, Datos, Gestión |
| `DSM` | Data Source Map | Inventario de fuentes, sistemas origen, linaje, frecuencia, calidad esperada y matriz KPI-fuente | `bi-data-source-mapper` | Datos, Arquitectura |
| `DMD` | Dimensional Model Design | Modelo dimensional: procesos, grano, tablas de hechos, dimensiones, SCD y matriz KPI-medida-fuente | `bi-dimensional-model-designer` | Datos, Analítica |
| `DSH` | Dashboard and Report Specification | Especificación de pantallas e informes: audiencia, KPI mostrados, filtros, drill-down y control de acceso | `bi-dashboard-report-designer` | Analítica, UX/UI |
| `BIQ` | BI Quality and Governance Report | Trazabilidad KPI-DMD-DSH, huérfanos, calidad de datos, gobierno, veredictos y handoff | `bi-quality-governance-validator` | Gestión, Gobierno de datos |

Los tipos BI no incluyen `CTLG`, cuya definición se encuentra en la sección Catalogos.


## Catalogos

Este tipo forma parte del catálogo vigente.

El tipo `CTLG` (Catálogo) para documentos que indexan los documentos de un mismo tipo sin repetir sus definiciones: nombre oficial o título, identificador, estado, versión y enlace. Un catálogo nunca define un elemento; cada elemento se define en su propio documento.

| Sigla | Nombre | Unidad documental | Productor | Consumidor típico |
|---|---|---|---|---|
| `CTLG` | Catálogo | Índice ordenado de los documentos de un tipo, con ID, título, estado y enlace; un catálogo por tipo indexado y por ámbito | Generación desde el frontmatter de los documentos indexados (`bi-kpi-definition-designer` para KPI; generadores de cada pack para ADR y ASR) | Gobierno documental, Arquitectura, Analítica |

**Resolución de la discrepancia con BI:** el pack `bi-analytics` 0.1.0 usa `CTLG` para el catálogo de KPI. `CTLG` se mantiene como tipo general del catálogo, por lo que el pack queda cubierto. La ampliación de BI pendiente (`BIC`, `KPI`, `DSM`, `DMD`, `DSH`, `BIQ`) sigue sin aprobar y no incluye `CTLG`; su aprobación no depende de esta.

**Límite:** la aprobación normativa no publica el cambio en GitLab. Queda pendiente someter esta versión a Merge Request.

## Epicas

Este tipo forma parte del catálogo vigente.

El tipo `EPC` (Épica) para agrupar historias de usuario funcionalmente relacionadas que pertenecen a un mismo `RCP`, bajo un resultado de negocio común. Es aditivo: ningún tipo existente cambia.

| Sigla | Nombre | Unidad documental | Productor | Consumidor típico | Campos adicionales obligatorios |
|---|---|---|---|---|---|
| `EPC` | Épica | Agrupación de `US` del mismo `RCP` con criterio de agrupación, historias incluidas, criterios de aceptación de extremo a extremo, riesgos y definición de terminado | `af-user-story-designer` (plugin `requirements-engineering`) | Requisitos, QA, Gestión | `product`, `pack`, `skill`; `related` hacia US |

- Identidad: `RCP-NNN-EPC-NNN`, con numeración propia separada de las `US`. El `RCP` de origen se cita en `sources`.
- La épica declara sus historias en `related`. Una `US` pertenece como máximo a una `EPC`, y la `US` no lleva campo de épica. Una `US` sin épica es válida.
- El criterio de agrupación es obligatorio. Una `EPC` no introduce requisitos nuevos ni modifica sus historias: sus criterios de aceptación se trazan a criterios de las historias incluidas.
- Una `EPC` no asigna Sprint (eso lo hace el `SSP`) y no aprueba nada: la aprobación es humana.

## Escenarios de negocio

Este tipo forma parte del catálogo vigente y sus reglas se aplican a todas las copias del estándar.

El tipo `BSN` (Business Scenario) para describir un escenario de negocio: secuencia de reglas de negocio aplicada por un actor sobre una capacidad, con precondiciones, pasos, excepciones y resultado. Es aditivo: ningún tipo existente cambia. `BSN` agrupa reglas `BR` por referencia y no las duplica.

- Identidad: `BSN-NNN`, con numeración propia.
- Productor: skill `biz-scenario-modeler` (plugin `business-knowledge`).
- Cada paso referencia una `BR`; los términos se referencian por `TRM`.
- Un `BSN` no aprueba nada: la aprobación es humana.\n