# Guía técnica — af-user-story-designer

Objetivo: Refinar User Stories individuales, INVEST, backlog e identificación HU.

Capacidades originales preservadas: af-user-story-refiner.

No fusionar conceptos diferentes en una misma afirmación. Para cada salida declarar relaciones `produced_by`, `sources`, `related`, `status`, y control de cambios.

Historias trazadas sin inventar reglas, con ID `RCP-NNN-US-NNN` globalmente único. El ID es el `concept_id` que usa `gitlab-work-publisher` para enlazar la historia con su issue; no se renumera ni se reutiliza. Migración de historias existentes (p. ej. `CL2-US-014`): asignar un ID nuevo con `us_ids.py next --rcp RCP-NNN`, mover el anterior a `legacy_id`, renombrar el archivo y actualizar los `related` y enlaces que lo citan.
