# Contrato local de qa-test-design-reviewer

**Rol:** specialist

**Entradas:** QTD completo y el QFA que lo originó. El revisor no puede ser el autor del diseño.

**Salidas:** QTR: hallazgos, acciones correctivas, human_review_required y checks de gate_proposal.

**Gates:** TEST_DESIGN_REVIEW_GATE. El especialista entrega `gate_proposal`; solo el orquestador decide.

Vocabulario y reglas comunes: `resources/contracts/common-contract.yaml`.
