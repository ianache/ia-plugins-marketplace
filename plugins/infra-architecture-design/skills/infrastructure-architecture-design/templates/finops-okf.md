---
type: IFO
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "finops"]
generated:
  by: "infrastructure-architecture-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-architecture-design
related: []
---
# {{ title }}

## Alcance de costos
<!-- Qué se incluye y qué no. -->
{{ cost_scope }}

## Modelo de costos
<!-- Unidades, tarifas y fuente de precios con fecha. -->
{{ cost_model }}

## Estimación por componente
<!-- Costo mensual y anual por componente. -->
{{ estimate }}

## Escenarios y sensibilidad
<!-- Variación frente a la demanda y a los supuestos. -->
{{ scenarios }}

## Palancas de optimización
<!-- Reservas, ajuste de tamaño y apagado. -->
{{ optimization }}

## Supuestos y exclusiones
<!-- Todo supuesto que cambie el costo. -->
{{ assumptions }}
