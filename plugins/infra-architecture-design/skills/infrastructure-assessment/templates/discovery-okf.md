---
type: IDS
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "discovery"]
generated:
  by: "infrastructure-assessment/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-assessment
related: []
---
# {{ title }}

## Alcance y modo
<!-- Iniciativa, modo (greenfield, brownfield o evolution) y límites del descubrimiento. -->
{{ scope_mode }}

## Hechos observados
<!-- Solo lo evidenciado, cada hecho con su fuente. -->
{{ observed_facts }}

## Inferencias
<!-- Deducciones marcadas como inferencia, con su base. -->
{{ inferences }}

## Incertidumbres y vacíos
<!-- Datos faltantes, conflictos y preguntas abiertas. -->
{{ unknowns }}

## Fuentes y evidencia
<!-- Rutas, commits o documentos con nivel de confianza. -->
{{ source_evidence }}
