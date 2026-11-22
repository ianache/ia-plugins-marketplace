# ux-design — Diseño UX/UI gobernado

**Versión:** 3.0.0 (preparada; cambio mayor de contratos y rutas)
**Estándar documental:** STD-OKF-001 v1.11.0-stable
**Composición:** un orchestrator y nueve skills especializados.

El pack parte de requisitos/historias aprobados y coordina el diseño desde UXR hasta el handoff HOF, con exploración de herramientas, verificación de accesibilidad, diseño gobernado y trazabilidad por pantalla.

## Composición y justificación

`ux-ui-orchestrator` es el único orchestrator del pack. Los otros nueve skills son especialistas; `claude-design-orchestrator` es un especialista de herramienta y no coordina el pack. El máximo recomendado por defecto es seis especialistas. Este pack conserva nueve porque cada uno tiene contrato y salida independiente en distintas etapas: requisitos, flujos, especificación, biblioteca web Angular opcional, exploración Stitch, exploración Claude Design, auditoría de accesibilidad, validación Figma y handoff. Stitch y Claude Design son herramientas con efectos y evidencias diferentes; Accessibility y Figma también tienen criterios de aceptación independientes. `web-atomic-component-designer` solo se activa para una biblioteca Angular. El exceso está justificado por la cobertura de proceso y se puede revisar si se decide retirar integraciones específicas.

## Skills

| Etapa | Skill | Resultado |
|---|---|---|
| Orquestación | `ux-ui-orchestrator` | Plan, gates, run y resumen operativo |
| Requisitos | `ux-requirements-analyzer` | `UXR` |
| Flujos | `user-flow-designer` | `FLW` |
| Pantallas | `ui-spec-writer` | `SCR`, `CMP`, `TKN`; criterios de aceptación embebidos/referenciados |
| Web opcional | `web-atomic-component-designer` | `CMP` y catálogo `CTLG` de CMP |
| Exploración Stitch | `stitch-ui-generator` | Payloads operativos; referencias externas en DTM |
| Exploración de alternativas | `claude-design-orchestrator` | `ADR` en borrador tras decisión humana; brief/alternativas como payloads operativos |
| Accesibilidad | `accessibility-reviewer` | Informe `CFR` de accesibilidad |
| Diseño Figma | `figma-design-validator` | Informe `CFR` de conformidad y relación gobernada en DTM |
| Handoff | `ux-development-handoff` | `HOF`, preflight y gate técnico |

Los criterios `AC`, las prompts de generación, el proyecto externo Stitch, las agendas/alternativas y el resumen UXS no son tipos aprobados independientes en STD-OKF-001 v1.9.0: se conservan como secciones del artefacto adecuado, referencias del DTM o payloads operativos del run. No crear tipos libres como `GEN`, `STP`, `IB`, `DD` o `UXS`.

## Modos de operación

El pack registra por separado el **modo de ciclo de vida** y el **escenario de trabajo UX**. Los escenarios A–G descritos por `references/scenarios.md` son rutas/tareas, no sustituyen a Greenfield/Brownfield/Evolution.

- **Greenfield:** no hay baseline UX del alcance. Se crea desde RQS/US/AC; toda referencia de As-Is se marca N/A con motivo. No declarar `NO_CHANGE` sin inventario.
- **Brownfield:** hay diseño existente. Inventariarlo, comprobar fuentes/versión/estado, separar observado de inferido y listar preguntas y diferencias antes de editar.
- **Evolution:** existe una baseline identificada y aprobada. Registrar referencia, versión y aprobación; evaluar impacto por UXR/FLW/SCR/DTM, modificar lo afectado y mantener intactos los no afectados como `NO_CHANGE`. Actualizar compatibilidad y HOF cuando el cambio afecte el contrato a desarrollo.

Brownfield/Evolution requieren `--baseline` al iniciar el run. Si falta una línea base verificable, bloquear G0 o registrar una decisión humana para reconstruirla; no tratar una captura Figma o una rama como baseline aprobada sin evidencia.

## Rutas y gobierno

- Documentos OKF: rutas de `assets/pathmap.json` dentro de la knowledge base del producto.
- Todos los archivos de gestión del orchestrator y los payloads operativos de herramientas: `.comsatel/ux-design/runs/<run-id>/`.
- Especialistas no escriben plan, estado, registro de gates, autorización ni historial del run.
- Ningún gate READY equivale a aprobación humana; ningún script asigna `verified`.
- El pack no publica en Figma/Stitch ni crea proyectos externos sin autorización explícita.

Consulta `assets/pathmap.md`, `VALIDATION.md` y la copia de `standards/STD-OKF-001-v1.11.0-stable.md`.
