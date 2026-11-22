---
name: ui-design-quality-validator
description: Usar cuando se necesite revisar coherencia, usabilidad, accesibilidad y trazabilidad en el proceso UX/UI gobernado de COMSATEL; coordinar con el orchestrator y aprobación humana G5.
metadata:
  version: "0.1.0"
---
# ui-design-quality-validator

## Objetivo
Revisar coherencia, usabilidad, accesibilidad y trazabilidad. Ejecutar: evaluar diseño con checklist y evidencias de revisión, riesgos y correcciones. No implementar código de producción ni alterar decisiones de Web/Mobile.

## Recursos de este skill
- `references/contract.md` — entradas, salidas, bloqueos y consumidores.
- `references/technical-guidance.md` — procedimiento específico, reglas y anti-patterns.
- `references/gate-checklist.md` — criterios del gate G5.
- `templates/deliverable.md` — plantilla OKF conceptual, sujeta al catálogo aprobado.
- `templates/gate-evidence.json` — estructura de evaluación y solicitud de aprobación.
- `scripts/validate.py` — validador de frontmatter y perfil mínimo.
- `examples/README.md` — caso sintético de CL2.
- `assets/README.md` — convenciones de anexos y diagramas.

## Contrato
**Entradas:** UXR/FLW/SCR/CMP/TKN, prototipos y criterios de aceptación.

**Salidas:** quality/design-review.md; quality/accessibility-review.md; quality/coverage-matrix.md. Salvo los archivos operativos del orchestrator, guardar bajo `design/ux-ui/<run-id>/`.

## Ejecución
1. Leer `references/contract.md`, `references/technical-guidance.md` y las fuentes existentes.
2. Verificar alcance, escenario, versiones y aprobaciones previas; si faltan, registrar bloqueo.
3. Producir cada entregable con trazabilidad explícita, decisiones, supuestos y preguntas abiertas.
4. Aplicar `templates/deliverable.md` y validar cada Markdown con `scripts/validate.py`.
5. Evaluar `references/gate-checklist.md` y generar evidencia; solicitar revisión humana.
6. Informar al orchestrator rutas, cambios, riesgos, evidencias y dependencias posteriores.

## Restricciones
- Gestionar plan, gates, evidencias y estado exclusivamente en `.comsatel/ux-ui-design/runs/<run-id>/`.
- Producir documentos con STD-OKF-001 v0.1.0-stable; nunca inventar `verified`, fuentes, aprobación o acceso a Figma/Stitch/Claude Design.
- Tipos UXR/FLW/SCR/CMP/TKN/HOF están **aprobados** en STD-OKF-001 v0.1.0-stable.
- El diseño es multiplataforma; Web y Mobile realizan el mapeo técnico posterior.
- Si hay contradicción de fuentes o falta evidencia crítica, registrar pregunta abierta y bloquear gate.

## Gate
G5: hallazgos priorizados, WCAG aplicable, consistencia y evidencias reales. El skill propone; un humano autorizado aprueba y el orchestrator registra.
