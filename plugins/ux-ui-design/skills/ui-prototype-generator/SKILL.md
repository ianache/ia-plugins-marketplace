---
name: ui-prototype-generator
description: Usar cuando se necesite coordinar prototipado con claude design, google stitch y figma en el proceso UX/UI gobernado de COMSATEL; coordinar con el orchestrator y aprobación humana G4.
---
# ui-prototype-generator

## Objetivo
Coordinar prototipado con Claude Design, Google Stitch y Figma. Ejecutar: preparar briefs, prompts, manifiesto y evidencias verificables de prototipos. No implementar código de producción ni alterar decisiones de Web/Mobile.

## Recursos de este skill
- `references/contract.md` — entradas, salidas, bloqueos y consumidores.
- `references/technical-guidance.md` — procedimiento específico, reglas y anti-patterns.
- `references/gate-checklist.md` — criterios del gate G4.
- `templates/deliverable.md` — plantilla OKF conceptual, sujeta al catálogo aprobado.
- `templates/gate-evidence.json` — estructura de evaluación y solicitud de aprobación.
- `scripts/validate.py` — validador de frontmatter y perfil mínimo.
- `examples/README.md` — caso sintético de CL2.
- `assets/README.md` — convenciones de anexos y diagramas.

## Contrato
**Entradas:** SCR/CMP/TKN, decisiones de herramienta, accesos reales a herramientas.

**Salidas:** prototypes/prototype-brief.md; prototypes/tool-manifest.md; prototypes/review-log.md. Salvo los archivos operativos del orchestrator, guardar bajo `design/ux-ui/<run-id>/`.

## Ejecución
1. Leer `references/contract.md`, `references/technical-guidance.md` y las fuentes existentes.
2. Verificar alcance, escenario, versiones y aprobaciones previas; si faltan, registrar bloqueo.
3. Producir cada entregable con trazabilidad explícita, decisiones, supuestos y preguntas abiertas.
4. Aplicar `templates/deliverable.md` y validar cada Markdown con `scripts/validate.py`.
5. Evaluar `references/gate-checklist.md` y generar evidencia; solicitar revisión humana.
6. Informar al orchestrator rutas, cambios, riesgos, evidencias y dependencias posteriores.

## Restricciones
- Gestionar plan, gates, evidencias y estado exclusivamente en `.comsatel/ux-ui-design/runs/<run-id>/`.
- Producir documentos con STD-OKF-001 v1.8.0-stable; nunca inventar `verified`, fuentes, aprobación o acceso a Figma/Stitch/Claude Design.
- Tipos UXR/FLW/SCR/CMP/TKN/HOF están **aprobados** en STD-OKF-001 v1.8.0-stable.
- El diseño es multiplataforma; Web y Mobile realizan el mapeo técnico posterior.
- Si hay contradicción de fuentes o falta evidencia crítica, registrar pregunta abierta y bloquear gate.

## Gate
G4: enlaces/IDs reales si existen; sin simular generación o acceso; fidelidad con SCR. El skill propone; un humano autorizado aprueba y el orchestrator registra.
