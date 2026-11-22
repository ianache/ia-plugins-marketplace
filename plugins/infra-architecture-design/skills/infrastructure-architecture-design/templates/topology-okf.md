---
type: ITP
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "topology"]
generated:
  by: "infrastructure-architecture-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-architecture-design
related: []
---
# {{ title }}

## Alcance
<!-- Entornos y servicios cubiertos. -->
{{ scope }}

## Topología lógica y física
<!-- Componentes, relaciones y diagrama (C4 o Mermaid). -->
{{ topology }}

## Redes y conectividad
<!-- Segmentos, rutas, balanceo, DNS y puntos de entrada. -->
{{ networking }}

## Zonas, alta disponibilidad y ubicación
<!-- Reparto por zona o región y puntos únicos de falla. -->
{{ zones_ha }}

## Decisiones y riesgos
<!-- ADR relacionados, supuestos y riesgos. -->
{{ decisions_risks }}
