---
type: IRQ
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "requirements"]
generated:
  by: "infrastructure-assessment/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-assessment
related: []
---
# {{ title }}

## Requisitos de infraestructura
<!-- Requisitos identificados e individualmente verificables. -->
{{ infra_requirements }}

## Requisitos no funcionales
<!-- Disponibilidad, rendimiento, seguridad y continuidad con valores medibles. -->
{{ nfr }}

## Restricciones
<!-- Técnicas, normativas, de presupuesto y de plazo. -->
{{ constraints }}

## Criterios de aceptación
<!-- Cómo se verifica cada requisito. -->
{{ acceptance }}

## Trazabilidad
<!-- Enlace de cada requisito a su origen (RCP, ASR, US). -->
{{ traceability }}
