---
type: IGR
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "gate-register"]
generated:
  by: "infrastructure-orchestrator/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-orchestrator
related: []
---
# {{ title }}

## Gates definidos
<!-- Gate y propósito. -->
{{ gates }}

## Prerrequisitos
<!-- Tareas completadas que el gate exige. -->
{{ prerequisites }}

## Aprobaciones
<!-- Aprobador humano, fecha y referencia. -->
{{ approvals }}

## Excepciones
<!-- Excepciones, quién las otorgó y por qué. -->
{{ exceptions }}
