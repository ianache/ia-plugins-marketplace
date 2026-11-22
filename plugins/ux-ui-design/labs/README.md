# Laboratorio de validación CL2

**Caso sintético:** Administración de Distribuidores + Monitoreo de Flota. Derivar US→UXR→FLW→SCR→CMP/TKN→prototipo→HOF. Validar reutilización para Web Angular y Mobile Flutter sin derivar MicroUIs 1:1 desde Bounded Contexts.

1. Inicializar: `python scripts/workflow.py init --run-id cl2-ux-001 --workspace /ruta/workspace --scenario greenfield` (el modo anterior `workflow.py cl2-ux-001 ...` sigue funcionando).
2. Completar `sources` en `scope-manifest.yaml` con fuentes US/BR/RCP reales y aprobar G0 con `approve --gate G0 --actor human:<nombre> --evidence <ref>`.
3. Ejecutar los seis skills en secuencia; adjuntar evidencias por gate.
4. No inventar proyectos Stitch/Figma ni afirmar accesos externos.
5. Validar que el handoff enumera pantalla, componente, token, estado, permiso, plataforma, versión y pendientes.
6. Revisar catálogo de tipos UXR/FLW/SCR/CMP/TKN/HOF antes de publicar a KB.
