## Tabla de contenido
- [Scope](#scope)
- [Acceptance Criteria](#acceptance-criteria)
- [Condition of Done](#condition-of-done)

## Scope
Coordinar el desarrollo completo de la User Story {{story_ref}} ({{hu_id}}, `{{hu_local}}`) en modo Cowork entre una persona de desarrollo y un agente de IA con el harness Claude Code, usando Superpowers (diseño previo, plan de implementación, desarrollo guiado por pruebas y verificación antes de dar el trabajo por terminado). La historia se implementa completa, como una unidad de trabajo, sin dividirla en tareas. La persona dirige y revisa; el agente ejecuta. El alcance es el de la historia dentro del DSP `{{dsp_id}}`: no se amplía.

## Acceptance Criteria
- Cada criterio de aceptación de la historia, tal como está en `{{hu_local}}`, está implementado y verificado con pruebas que pasan.
- La implementación respeta las reglas de negocio y las restricciones que citan la historia y el DSP `{{dsp_id}}`, y no incluye nada fuera de su alcance.
- La persona de desarrollo revisó el trabajo del agente y las desviaciones quedaron documentadas.

De forma resumida se debe cubrir lo siguiente:

- [ ] Brainstorming Completado con Superpowers
- [ ] ReqSpec validado
- [ ] Plan de Implementación aprobado
- [ ] Iteración Inicial (1era Corrida - Plan Execution)
- [ ] Refinamiento de la implamentación (Debugging)
- [ ] Resultado final construido validado
- [ ] Base de código integrada en rama `fecture` con pipeline CI/CD exitoso
- [ ] Base de código integrada en rama `develop` con pipeline CI/CD exitoso


## Condition of Done
- Se cumple la Definition of Done de la historia definida en `{{hu_local}}`.
- El trabajo está integrado y listo para que Calidad lo reciba (ver la tarea de Aseguramiento de Calidad de {{story_ref}}).
- Las preguntas abiertas o los cambios de alcance se elevaron como solicitud de cambio; no se resolvieron por suposición.

<!--
Plantilla del issue de tipo «Task» para el rol Dev. La renderiza `scripts/gitlab_issues.py`; los comentarios HTML no se publican.
- Título: `US<iid>: Coordinación del desarrollo con Superpowers`. Labels: `Task` y `Dev`. Mismo Milestone que la User Story.
- La descripción lleva una tabla de contenido y tres secciones: Scope (la tarea según el rol), Acceptance Criteria y Condition of Done.
- No copiar aquí la historia, sus criterios ni su Definition of Done: se leen en el archivo de la historia.
-->
