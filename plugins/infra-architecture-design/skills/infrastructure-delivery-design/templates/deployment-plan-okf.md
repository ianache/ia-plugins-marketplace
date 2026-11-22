---
type: IDP
id: "{{ artifact_id }}"
title: "{{ title }}"
description: "{{ description }}"
version: "1.0.0"
status: draft
owner: "team:infrastructure"
classification: internal
tags: [infrastructure, "deployment-plan"]
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
<!-- Qué se despliega y dónde. -->
{{ scope_envs }}

## Prerrequisitos y ventanas
<!-- Condiciones previas y ventanas de cambio. -->
{{ prerequisites }}

## Pasos y orden
<!-- Secuencia con responsable por paso. -->
{{ steps }}

## Verificación posterior
<!-- Comprobaciones tras cada fase. -->
{{ verification }}

## Criterios de go/no-go
<!-- Criterios; la decisión es humana. -->
{{ go_no_go }}
