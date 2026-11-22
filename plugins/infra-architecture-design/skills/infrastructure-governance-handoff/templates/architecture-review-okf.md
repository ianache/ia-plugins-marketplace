---
type: IAR
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "architecture-review"]
generated:
  by: "infrastructure-governance-handoff/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-governance-handoff
related: []
---
# {{ title }}

## Alcance revisado
<!-- Artefactos y versiones revisados. -->
{{ reviewed_scope }}

## Hallazgos
<!-- Hallazgo, severidad y evidencia. -->
{{ findings }}

## Cumplimiento frente a requisitos
<!-- Requisito frente a diseño. -->
{{ compliance }}

## Acciones correctivas
<!-- Acción, dueño y plazo. -->
{{ actions }}

## Decisión de revisión
<!-- Decisión humana y quién la tomó. -->
{{ decision }}
