---
type: ISD
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "slo-dr-plan"]
generated:
  by: "infrastructure-operations-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-operations-design
related: []
---
# {{ title }}

## SLI y SLO
<!-- Indicador, objetivo y ventana de medición. -->
{{ slo }}

## Presupuesto de error
<!-- Cálculo y política al agotarse. -->
{{ error_budget }}

## RTO y RPO
<!-- Valores por servicio y su justificación. -->
{{ rto_rpo }}

## Estrategia de recuperación
<!-- Pasos, sitios y dependencias. -->
{{ recovery }}

## Pruebas de DR y responsables
<!-- Frecuencia, alcance y dueños. -->
{{ dr_tests }}
