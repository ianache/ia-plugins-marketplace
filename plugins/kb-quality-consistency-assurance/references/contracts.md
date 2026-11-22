# Contratos de interoperabilidad

## `source_manifest.yaml`
```yaml
schema_version: '1.0'
source_id: kb-cl2
repository: https://git.example.invalid/group/kb-cl2
branch: develop
commit_sha: '<full-commit-sha>'
okf_version: '0.2'
profile: 'STD-OKF-001@1.0.0'
paths: [business/, requirements/, architecture/]
index_generation: null
publication_generation: null
```
Valores de ejemplo no son referencias reales. El perfil vigente es `STD-OKF-001@1.3.0-stable`.

## `finding` normalizado
```yaml
id: KBQ-0001
category: structural  # structural|referential|semantic|cross_artifact|impact|publication
severity: high         # critical|high|medium|low|info
status: suspected      # suspected|confirmed|unverified|resolved|accepted_risk
confidence: 0.85
source:
  source_id: kb-cl2
  commit_sha: '<full-commit-sha>'
  path: requirements/US-001.md
  location: 'section:2'
  excerpt: 'Texto literal mínimo necesario'
related_artifacts: []
rule_id: KBQ-STRUCT-001
explanation: 'Motivo verificable'
recommendation: 'Corrección propuesta; no aplicada'
reviewer: null
```

## `gate-report.yaml`
```yaml
gate_id: G1
status: blocked  # passed|failed|blocked|pending_approval
producer_tasks: [T01]
required_outputs: [structure-findings.yaml]
evidence: []
blocking_findings: []
reviewed_by: null
```

## `run-plan.yaml`
```yaml
run_id: KBQ-2026-001
mode: audit
nodes:
  - id: T01
    kind: task
    depends_on: []
  - id: G1
    kind: gate
    depends_on: [T01]
    evaluates: [T01]
  - id: T02
    kind: task
    depends_on: []
  - id: G2
    kind: gate
    depends_on: [T02]
    evaluates: [T02]
```
El validador rechaza dependencias circulares y gates que anteceden a sus propios productores.
