---
type: IOB
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "observability"]
generated:
  by: "infrastructure-operations-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-operations-design
related: []
---
# {{ title }}

## Alcance y servicios
<!-- Servicios y componentes observados. -->
{{ scope }}

## Métricas, logs y trazas
<!-- Señales, fuentes, etiquetas y muestreo. -->
{{ signals }}

## Alertas y umbrales
<!-- Alerta, umbral, severidad y destinatario. -->
{{ alerts }}

## Dashboards y retención
<!-- Vistas, audiencia y períodos de retención. -->
{{ dashboards }}

## Responsables y runbooks
<!-- Dueños y referencias a RUN. -->
{{ owners }}
