---
type: IRL
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "reliability"]
generated:
  by: "infrastructure-operations-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-operations-design
related: []
---
# {{ title }}

## Objetivos de disponibilidad
<!-- Objetivo por servicio y su origen. -->
{{ availability }}

## Modos de falla
<!-- Falla, efecto, detección y mitigación. -->
{{ failure_modes }}

## Redundancia y alta disponibilidad
<!-- Mecanismos y puntos únicos de falla restantes. -->
{{ redundancy }}

## Degradación y tolerancia a fallos
<!-- Comportamiento ante falla parcial. -->
{{ degradation }}

## Pruebas de resiliencia
<!-- Pruebas previstas y criterios de éxito. -->
{{ resilience_tests }}
