---
type: ICM
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "control-matrix"]
generated:
  by: "infrastructure-security-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-security-design
related: []
---
# {{ title }}

## Marco de referencia
<!-- Norma o marco y versión usados. -->
{{ framework }}

## Controles
<!-- Control, responsable, estado y frecuencia. -->
{{ controls }}

## Mapeo a requisitos y riesgos
<!-- Control frente a requisito o amenaza. -->
{{ mapping }}

## Brechas y excepciones
<!-- Controles no implementados y excepciones aprobadas. -->
{{ gaps }}

## Evidencia de implementación
<!-- Enlace o referencia verificable por control. -->
{{ evidence }}
