# Gates y políticas de decisión

| Gate | Productores | Condición |
|---|---|---|
| G1 Structural Integrity | T01 | Estructura OKF y perfil aplicable válidos |
| G2 Referential Integrity | T02 | Relaciones/provenance resueltos o excepciones registradas |
| G3 Semantic Consistency | T03 | Sin contradicciones críticas confirmadas; sospechas pendientes de revisión |
| G4 Cross-Artifact Consistency | T04 | Contratos y trazabilidad coherentes para artefactos aplicables |
| G5 Change Impact | T05 | Impactos, obsolescencia y cambios de publicación evaluados |
| G6 Publication Readiness | T06 + G1–G5 | Evidencias consolidadas, políticas satisfechas y aprobación humana |

Los gates son nodos posteriores a sus productores. G6 es un gate de salida; no habilita retroactivamente T01–T06. Un hallazgo semántico `suspected` exige revisión, no fallo automático irreversible. Una excepción debe registrar responsable, justificación, alcance y caducidad.
