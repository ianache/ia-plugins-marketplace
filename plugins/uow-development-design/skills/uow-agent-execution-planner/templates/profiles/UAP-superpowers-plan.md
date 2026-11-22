# <UOW-ID> — <título> Implementation Plan

> Para agentes: usar `superpowers:subagent-driven-development` (recomendado) o `superpowers:executing-plans` para ejecutar este plan tarea por tarea. Los pasos usan casillas (`- [ ]`).
> Fuente de verdad: la UOW `<UOW-ID>`, su UCB y su UCM. Este plan no amplía alcance ni cambia contratos.

**Goal:** <objetivo de la UOW en una frase>

**Architecture:** <enfoque en 2-3 frases, según los ADR de `adr_refs`>

**Tech Stack:** <lenguaje, framework, base de datos y herramientas del repositorio>

**Repositorio:** `<project>` · rama `<target_branch>` · commit base `<source_commit>`
**Límites:** solo se escribe en `allowed_paths`; nunca en `forbidden_paths`. Si hace falta salir de ellos, detenerse y escalar a `<escalate_to>`.

---

### Task 1: <nombre>

**Files:**
- Create: `<ruta exacta dentro de allowed_paths>`
- Modify: `<ruta exacta>:<líneas>`
- Test: `<ruta exacta de la prueba>`

- [ ] **Step 1: Escribir la prueba que falla**
```<lenguaje>
<código de la prueba>
```
- [ ] **Step 2: Ejecutar y confirmar que falla**
Run: `<comando>` · Expected: FAIL con `<mensaje>`
- [ ] **Step 3: Implementación mínima**
```<lenguaje>
<código>
```
- [ ] **Step 4: Ejecutar y confirmar que pasa**
Run: `<comando>` · Expected: PASS
- [ ] **Step 5: Commit**
`git add <rutas> && git commit -m "<tipo>(<ámbito>): <mensaje> [<UOW-ID>]"`

---

## Verificación final
- [ ] <criterio de terminado 1> — `<comando de verificación>`
- [ ] <criterio de terminado 2> — `<comando de verificación>`

## Condiciones de parada
- <condición> → detener, registrar la desviación y escalar a `<escalate_to>`.
