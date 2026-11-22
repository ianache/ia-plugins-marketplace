# Contrato local de qa-quality-intelligence

**Rol:** specialist

**Entradas:** QTE y QER aprobados, ejecuciones, evidencia, defectos, CI/CD, observabilidad e historia.

**Salidas:** QQI: cobertura, confianza, recomendación (READY, READY_WITH_RISK, NOT_READY, INSUFFICIENT_EVIDENCE) y checks de gate_proposal. La decisión de calidad es humana.

**Gates:** QUALITY_INTELLIGENCE_GATE. El especialista entrega `gate_proposal`; solo el orquestador decide.

Vocabulario y reglas comunes: `resources/contracts/common-contract.yaml`.
