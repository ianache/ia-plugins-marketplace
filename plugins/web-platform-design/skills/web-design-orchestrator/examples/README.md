# Ejemplo de ejecución de `web-design-orchestrator`

1. Confirmar `run_id`, escenario, fuentes y gate anterior.
2. Activar el skill desde Claude Code con fuentes versionadas.
3. Generar `..comsatel/web-platform-design/runs/<run-id>/execution-plan.yaml` con decisiones trazables.
4. Ejecutar `python skills/web-design-orchestrator/scripts/validate.py <archivo-md>` para el entregable Markdown correspondiente.
5. Registrar evidencia y solicitar evaluación humana de **G0-G6**.

Este ejemplo no representa una aprobación ni una ejecución real del agente.
