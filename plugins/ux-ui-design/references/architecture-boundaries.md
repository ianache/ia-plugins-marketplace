# Separación de responsabilidades

| Capa | Owner | Artefactos |
|---|---|---|
| Business/Requirements | AF | US, BR, RCP |
| DDD | Arquitectura | BC, CTX, AGG |
| UX/UI | Este plugin | UXR, FLW, SCR, CMP, TKN, prototipos, HOF |
| Web | Web Platform Design | Shell, MicroUIs, BFF, composición técnica |
| Mobile | Mobile Application Design | Features Flutter, estado, offline, integración |

Los handoffs UX/UI→Web y UX/UI→Mobile son independientes y versionados. Cambios de diseño requieren Change Request, no modificaciones silenciosas desde los plugins consumidores.
