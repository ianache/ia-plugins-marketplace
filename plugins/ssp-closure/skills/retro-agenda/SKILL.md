---
name: retro-agenda
description: Enmarcar problemas y acciones de la Sprint Retrospective, separar hechos de hipótesis y preparar el CLS de cierre del SSP con resultados confirmados.
metadata:
  version: "1.0.0"
  author: "COMSATEL"
  type: "specialist"
---

# Retro Agenda and Sprint Closure

## Activación y alcance

Invocar para preparar la retrospectiva de un SSP y, una vez celebrada, documentar su cierre. No inventa causas, resultados ni acciones.

## Entradas

- SSP, periodo, issues/estados y payload de Review (`T1`) más aceptación registrada por el Product Owner.
- Hechos, problemas a tratar, resultados reales de la retrospectiva y acciones aprobadas por el equipo.
- Criterios de éxito/objetivo del SSP y evidencia de cierre.

## Procedimiento

1. Separar hechos observados, impacto e hipótesis de causa.
2. Producir agenda de discusión en `task-results/T3/retro-agenda.md`, sin frontmatter OKF.
3. Después de la sesión, registrar solo decisiones y lecciones confirmadas, con sus referencias; cada experimento debe incluir persona dueña, métrica y fecha.
4. Crear un único `CLS` con plantilla, resultado frente al objetivo del SSP, desviaciones, estado de entrega, lecciones y transferencia. Guardar como `management/closure/CLS-<ssp-id>.md`.
5. Validar el CLS y proponer `RETRO_AGENDA_GATE` con evidencia y vínculos a las salidas de Review.

## Salida y gate

Agenda es payload operativo. El cierre es documento OKF `CLS`, con metadatos STD-OKF-001 v1.9.0, destino definido en el pathmap. No hay tipo propio para agenda/acta de retro. Sin acta real o resultado confirmado, dejar el CLS en draft y bloquear el gate de cierre.

## Restricciones

No presentar hipótesis como hechos, no imponer soluciones ni registrar aceptación del Product Owner. No escribir gate-register ni plan. Usar `templates/agenda-payload.md` y `templates/closure-report.md`.
