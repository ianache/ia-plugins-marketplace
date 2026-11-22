# Guía técnica — biz-scenario-modeler

Objetivo: modelar escenarios de negocio (BSN) como secuencias de reglas BR con precondiciones, pasos, excepciones y resultado, trazados a BR, TRM, BCAP y BO.

No duplicar reglas: cada paso referencia una `BR` existente. Si un paso necesita una regla que no existe, registrarla como pregunta abierta y dejar el escenario en CONDITIONAL o NOT_READY. Distinguir un escenario de negocio del modo de run del orchestrator (`greenfield`, `brownfield`, `evolution`, `incremental`), que usa la misma palabra.
