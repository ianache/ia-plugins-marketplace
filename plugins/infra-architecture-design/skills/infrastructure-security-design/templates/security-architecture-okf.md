---
type: ISA
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "security-architecture"]
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
<!-- Activos a proteger y su clasificación. -->
{{ scope_assets }}

## Zonas y segmentación
<!-- Dominios de confianza y flujos permitidos. -->
{{ zones }}

## Identidad y acceso
<!-- Autenticación, autorización y gestión de secretos. -->
{{ identity }}

## Protección de datos
<!-- Cifrado en tránsito y en reposo, y respaldos. -->
{{ data_protection }}

## Monitoreo y respuesta
<!-- Detección y respuesta a incidentes. -->
{{ monitoring }}

## Cumplimiento y decisiones
<!-- Normas aplicables y ADR relacionados. -->
{{ compliance }}
