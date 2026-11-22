---
type: IAC
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "iac-specification"]
generated:
  by: "infrastructure-delivery-design/4.1.0"
  at: "{{ generated_at }}"
sources: []
pack: comsatel-infrastructure
skill: infrastructure-delivery-design
related: []
---
# {{ title }}

## Alcance y entornos
<!-- Entornos, cuentas y proveedores. -->
{{ scope_envs }}

## Módulos y recursos
<!-- Módulos, recursos y dependencias. -->
{{ modules }}

## Variables y secretos
<!-- Entradas por entorno; sin valores secretos. -->
{{ variables }}

## Estado y backend
<!-- Backend, bloqueo y control de acceso. -->
{{ state }}

## Validación y políticas
<!-- Linters, políticas y pruebas previas al aplicar. -->
{{ validation }}
