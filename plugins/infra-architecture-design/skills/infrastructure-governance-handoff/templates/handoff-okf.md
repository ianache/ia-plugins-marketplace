---
type: IHO
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "handoff"]
generated:
  by: "infrastructure-governance-handoff/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-governance-handoff
related: []
---
# {{ title }}

## Destinatarios y alcance
<!-- Quién recibe qué. -->
{{ recipients }}

## Artefactos entregados
<!-- Artefactos con versión y hash. -->
{{ deliverables }}

## Decisiones y ADR
<!-- Decisiones vigentes y ADR que las respaldan. -->
{{ decisions }}

## Restricciones y pendientes
<!-- Restricciones y trabajo no cerrado. -->
{{ pending }}

## Aceptación
<!-- Evidencia de aceptación del destinatario. -->
{{ acceptance }}
