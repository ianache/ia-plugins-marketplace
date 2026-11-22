---
type: IBL
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "baseline"]
generated:
  by: "infrastructure-assessment/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-assessment
related: []
---
# {{ title }}

## Alcance y fecha de línea base
<!-- Entorno, fecha y fuente de la fotografía. -->
{{ scope_date }}

## Inventario de componentes
<!-- Componentes, versiones, ubicación y responsables. -->
{{ inventory }}

## Topología actual
<!-- Conectividad y dependencias observadas. -->
{{ current_topology }}

## Nivel de confianza de la evidencia
<!-- Por sección: verificado, inferido o supuesto. -->
{{ confidence }}

## Brechas conocidas
<!-- Deuda técnica, riesgos y datos no obtenidos. -->
{{ known_gaps }}
