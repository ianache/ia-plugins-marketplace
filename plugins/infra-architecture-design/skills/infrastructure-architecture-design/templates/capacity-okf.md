---
type: ICP
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "capacity"]
generated:
  by: "infrastructure-architecture-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-architecture-design
related: []
---
# {{ title }}

## Demanda y supuestos de carga
<!-- Volumetría, picos y supuestos. -->
{{ demand }}

## Dimensionamiento por componente
<!-- CPU, memoria, almacenamiento y red con su cálculo. -->
{{ sizing }}

## Margen y crecimiento
<!-- Holgura, proyección y disparadores de escalado. -->
{{ headroom }}

## Límites y cuellos de botella
<!-- Cuotas y límites que condicionan el diseño. -->
{{ limits }}

## Método de cálculo
<!-- Fórmulas, fuentes y validación. -->
{{ method }}
