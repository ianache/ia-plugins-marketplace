## Tabla de contenido
- [Scope](#scope)
- [Acceptance Criteria](#acceptance-criteria)
- [Condition of Done](#condition-of-done)

## Scope
Coordinar el aseguramiento de calidad de la User Story {{story_ref}} ({{hu_id}}, `{{hu_local}}`): una persona analista de calidad, en modo Cowork con un agente de IA, diseña y ejecuta pruebas manuales o automatizadas sobre cada criterio de aceptación y sobre la Definition of Done de la historia, y registra la evidencia. Esta tarea comienza cuando el desarrollo de la historia se entrega a Calidad. El alcance es el de la historia dentro del DSP `{{dsp_id}}`: no se amplía.

## Acceptance Criteria
- Cada criterio de aceptación de la historia, tal como está en `{{hu_local}}`, tiene al menos un caso de prueba ejecutado y su evidencia.
- Cada defecto encontrado quedó registrado con el criterio incumplido.
- El resultado por criterio (cumple o no cumple) lo decide la persona de calidad, con el agente como apoyo.

## Condition of Done
- Se verificó la Definition of Done de la historia definida en `{{hu_local}}`.
- El resultado se comunicó: la historia se da por probada, o vuelve a desarrollo con el criterio incumplido.
- Las pruebas no cubiertas por falta de datos, de dependencias o de información quedaron declaradas, no omitidas.

De forma resumida se debe cubrir lo siguiente:

- [ ] Plan de Pruebas aprobado.
- [ ] Escenarios de Pruebas aprobados.
- [ ] Conjunto completo de Casos de Pruebas aprobados.
- [ ] Estrategias de Prueba aprobados.
- [ ] Automatización de casos de pruebas implementados y validados  
- [ ] Aseguramiento de calidad manual (cuando aplique)

<!--
Plantilla del issue de tipo «Task» para el rol QA. La renderiza `scripts/gitlab_issues.py`; los comentarios HTML no se publican.
- Título: `US<iid>: Coordinación del Aseguramiento de Calidad`. Labels: `Task` y `QA`. Mismo Milestone que la User Story.
- La descripción lleva una tabla de contenido y tres secciones: Scope (la tarea según el rol), Acceptance Criteria y Condition of Done.
- No copiar aquí la historia, sus criterios ni su Definition of Done: se leen en el archivo de la historia.
-->
