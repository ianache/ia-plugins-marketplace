---
type: CMP
id: CMP-EXAMPLE-001
title: "Example component specification"
description: "Reusable component contract and verification requirements."
version: "0.1.0"
status: draft
owner: team:ux-design
classification: internal
pack: ux-design
skill: web-atomic-component-designer
tags: [ux-design, component]
generated:
  by: "web-atomic-component-designer/0.2.0"
  at: "<ISO-8601-CON-ZONA>"
sources:
  - id: source-001
    resource: "../DTC-104/technical-design-context.md"
readiness: REQUIRES_REVIEW
# Component Specification

## Identity

- Component ID: `CMP-...`
- Name and selector:
- Atomic level: atom | molecule | organism | template | page
- Purpose:
- Non-goals:
- Owner:
- Consumers:

## Composition

- Allowed children:
- Parent contexts:
- Dependency direction:
- Reuse rationale:
- Existing component search and decision:

## Angular contract

```ts
export interface ExampleComponentInputs {
  // stable public inputs
}

export type ExampleComponentEvent = {
  type: string;
  // public event payload
};
```

- Selector:
- Standalone or module strategy:
- Inputs and defaults:
- Outputs/events:
- Content projection slots:
- Signals/observables:
- Side effects and services:
- Public export path:

## Behavior and visual contract

| Dimension | Specification |
|---|---|
| Variants | |
| Sizes | |
| Loading | |
| Success | |
| Empty | |
| Error | |
| Disabled | |
| Offline/recovery | |
| Responsive breakpoints | |
| Localization | |
| Design tokens | |

## Accessibility and security

- WCAG target and applicable success criteria:
- Accessible name and role:
- Keyboard order and shortcuts:
- Focus management:
- Screen-reader behavior:
- Contrast and motion rules:
- Sensitive data and rendering constraints:
- Security findings or assumptions:

## Verification

- Unit tests:
- Interaction tests:
- Accessibility tests:
- Visual regression scenarios:
- Consumer contract tests:
- Performance budget:
- Acceptance criteria:

## Change and lifecycle

- Change classification: additive | compatible | breaking | unknown
- Semver impact:
- Deprecation or migration path:
- Open questions:
- Human review event: not set by agents

## Traceability

- User Story:
- ASR:
- ADR:
- DTC-104 page or journey:
- QA cases:
- Internal links:
