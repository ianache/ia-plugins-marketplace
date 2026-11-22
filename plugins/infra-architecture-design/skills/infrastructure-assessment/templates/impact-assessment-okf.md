---
type: IIA
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "impact-assessment"]
generated:
  by: "infrastructure-assessment/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-assessment
related: []
---
# {{ title }}

## Cambio evaluado
<!-- Descripción del cambio y su motivación. -->
{{ change }}

## Componentes y consumidores afectados
<!-- Impacto directo, indirecto y desconocido. -->
{{ affected }}

## Compatibilidad y migración
<!-- Rupturas, ventanas y pasos de migración. -->
{{ compatibility }}

## Riesgos
<!-- Riesgo, probabilidad, impacto y dueño. -->
{{ risks }}

## Mitigación y rollback
<!-- Medidas y condiciones de reversión. -->
{{ mitigation }}
