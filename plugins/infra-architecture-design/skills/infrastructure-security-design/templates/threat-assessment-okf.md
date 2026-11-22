---
type: ITA
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "threat-assessment"]
generated:
  by: "infrastructure-security-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-security-design
related: []
---
# {{ title }}

## Alcance y activos
<!-- Superficie de ataque evaluada. -->
{{ scope_assets }}

## Amenazas identificadas
<!-- Amenaza, vector y activo afectado. -->
{{ threats }}

## Valoración del riesgo
<!-- Probabilidad, impacto y escala usada. -->
{{ risk_rating }}

## Mitigaciones y controles
<!-- Controles propuestos y su enlace a la matriz. -->
{{ mitigations }}

## Riesgo residual y aceptación
<!-- Riesgo restante; la aceptación es decisión humana. -->
{{ residual }}
