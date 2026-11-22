---
type: IXP
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "execution-plan"]
generated:
  by: "infrastructure-orchestrator/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-orchestrator
related: []
---
# {{ title }}

## Iniciativa y modo
<!-- Iniciativa y modo de trabajo. -->
{{ initiative_mode }}

## Tareas y dependencias
<!-- Tarea, skill, dependencias y estado. -->
{{ tasks }}

## Gates
<!-- Gates requeridos por fase. -->
{{ gates }}

## Responsables
<!-- Dueño por tarea y gate. -->
{{ owners }}

## Estado general
<!-- Estado consolidado y siguiente paso. -->
{{ status }}
