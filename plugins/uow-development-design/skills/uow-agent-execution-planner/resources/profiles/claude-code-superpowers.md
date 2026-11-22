# Perfil de ejecución: Claude Code con Superpowers

Perfil opcional del `UAP`. El contenido de la UOW es neutral: cualquier agente puede seguirlo. Este perfil añade cómo se entrega a Claude Code.

| Elemento | Dónde |
|---|---|
| Plan de ejecución en formato `writing-plans` | `templates/profiles/UAP-superpowers-plan.md` |
| Instrucciones para `CLAUDE.md` o el prompt inicial | `templates/profiles/claude-code-brief.md` |

## Cómo se usa
1. El developer abre el repositorio en la rama base del UCM y copia el plan a `docs/plans/<UOW-ID>.md` (o la ruta que defina el repositorio).
2. Lanza `superpowers:subagent-driven-development` (o `executing-plans`) apuntando a ese plan.
3. El agente se limita a `allowed_paths`, trabaja con prueba primero y se detiene ante cualquier condición de parada.

## Reglas
- El plan se deriva del UAP, no lo sustituye: el UAP sigue siendo el documento OKF trazable.
- Los comandos de verificación y los criterios de terminado son los mismos del UAP.
- Si Superpowers no está instalado, el perfil `neutral` sigue siendo válido.
