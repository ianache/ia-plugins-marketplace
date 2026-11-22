---
type: IXL
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "execution-log"]
generated:
  by: "infrastructure-orchestrator/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-orchestrator
related: []
---
# {{ title }}

## Eventos
<!-- Eventos ordenados cronológicamente. -->
{{ events }}

## Resultados por tarea
<!-- Resultado y estado de cada tarea. -->
{{ results }}

## Evidencias
<!-- Ruta y sha256 de cada evidencia. -->
{{ evidence }}

## Errores y bloqueos
<!-- Errores, causa y acción tomada. -->
{{ errors }}
