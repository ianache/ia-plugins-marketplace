---
type: IRB
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "rollback-plan"]
generated:
  by: "infrastructure-delivery-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-delivery-design
related: []
---
# {{ title }}

## Disparadores
<!-- Condiciones que activan la reversión. -->
{{ triggers }}

## Pasos de reversión
<!-- Secuencia, responsable y tiempo estimado. -->
{{ steps }}

## Datos y estado
<!-- Tratamiento de datos y estado al revertir. -->
{{ data_state }}

## Verificación
<!-- Cómo se confirma el retorno al estado previo. -->
{{ verification }}

## Responsables y comunicación
<!-- Dueños y canal de escalamiento. -->
{{ owners }}
