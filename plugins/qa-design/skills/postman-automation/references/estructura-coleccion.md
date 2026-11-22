# Estructura de la colección Postman

## 1. Jerarquía

```text
<colección>
├── RF01-<nombre de la funcionalidad del endpoint>      (descripción: método, ruta, rol requerido)
│   ├── <ID del TC> - <Nombre del TC>                    (descripción: Cubre <AC>, historia, TSN)
│   │   ├── <request 1>                                  (request.description: documentación)
│   │   └── <request 2>
│   └── <ID del TC> - <Nombre del TC>
└── RF02-<nombre de la funcionalidad>
    └── ...
```

Solo dos niveles de carpetas. Los requests van dentro de la carpeta del TC.

## 2. Reglas de nombre

| Nivel | Patrón | Ejemplo válido | Inválido |
|---|---|---|---|
| Funcionalidad | `^RF\d{2}-.+$` | `RF01-Consultar eventos de auditoría` | `Auditoría`, `RF1-...` |
| Caso de prueba | `^TC-[A-Z0-9-]+ - .+$` | `TC-PE-01 - Consulta válida devuelve una página` | `HU-05-04 AC-1 - ...` (un AC no es un ID de TC) |

- El separador del caso es exactamente ` - ` (espacio, guion, espacio).
- El título de una carpeta de caso no contiene `AC-`. La referencia va en la descripción.
- El ID del caso sale del TC. Si el TC no tiene ID oficial, usar `TC-<SIGLAS>-NN` y marcar `provisional` en la descripción.

## 3. Descripción de carpetas

Descripción de la funcionalidad (`RF##`): método y ruta del endpoint, rol o permiso requerido, y el `operationId` del contrato.

Descripción del caso (`TC`): una línea por trazabilidad.

```text
Cubre HU-05-04 AC-2, AC-8 (validación de rango; límite de 12 meses).
Historia: HU-05-04. TSN: TSN-PE-02. Estado del TC: READY.
```

Si el ID es provisional: añadir `ID provisional; pendiente de asignar por QA.`

Si el caso no tiene AC en la historia: `Sin criterio de aceptación en la historia: <motivo>.`

## 4. Documentación de cada request

`request.description` (la pestaña Documentation de Postman) usa esta plantilla:

```markdown
**Objetivo:** <una frase específica del request: qué verifica y con qué resultado>.

**Caso:** <ID> - <Nombre del TC>

**Criterios de aceptación:**

#### <HU> <AC> — <título del AC>

```gherkin
<bloque Gherkin copiado de la historia, sin cambios>
```
```

Reglas:
- El objetivo es propio del request, no una copia del nombre del TC.
- Los criterios se copian de la historia. Un criterio que no existe se declara como ausente.
- Si el caso no tiene criterios: `**Criterios de aceptación:** ninguno definido en las historias de usuario.` y una nota con el criterio técnico aplicado.
- Si el criterio solo tiene una referencia de trazabilidad y no un texto propio (por ejemplo, paginación), declararlo: `Nota de trazabilidad: ...`.

## 5. Extracción de criterios desde la historia

Las historias usan encabezados `### AC-n — <título>` seguidos de un bloque ` ```gherkin `. El AC termina en el siguiente `### AC-` o `## `.

Procedimiento (script, no transcripción manual):

```python
import re

def extraer_acs(texto):
    out = {}
    for m in re.finditer(r"^### (AC-\d+) — (.+)$", texto, re.M):
        resto = texto[m.end():]
        fin = re.search(r"^### AC-|^## ", resto, re.M)
        cuerpo = resto[:fin.start()] if fin else resto
        bloques = re.findall(r"```gherkin\n(.*?)```", cuerpo, re.S)
        out[m.group(1)] = (m.group(2).strip(), "\n".join(b.strip("\n") for b in bloques))
    return out
```

Una vez extraídos, el texto se inserta tal cual en la documentación del request.

## 6. Aserciones

Cada paso de `Resultado esperado (oracle)` se traduce en una aserción en la pestaña Tests:

| Oracle | Aserción |
|---|---|
| Código HTTP | `pm.response.to.have.status(<código>)` |
| Código de error del negocio | `pm.expect(pm.response.json().code).to.eql(<código>)` |
| Tipo de contenido de error | `pm.expect(pm.response.headers.get('Content-Type')).to.include('application/problem+json')` |
| Campos de la respuesta | `pm.expect(body).to.have.property('<campo>')` |
| Lista vacía | `pm.expect(body.items).to.be.an('array').that.is.empty` |

## 7. Variables y seguridad

- Variables de entorno de la colección: `baseUrl`, un token por rol (`tokenSinRol`, `tokenAuditQuery`, …) y las variables de encadenamiento (`nextCursor`).
- Los tokens se pasan por `--env-var` o por el entorno de CI. Nunca se escriben en el JSON.
- No guardar URLs con credenciales ni IPs de ambientes privados en la documentación.

## 8. Huecos

Un AC sin request se declara en `acs_sin_automatizar` del reporte con su motivo. Motivos habituales:
- decisión pendiente (una pregunta abierta en la spec);
- requiere un token o rol que aún no existe;
- requiere datos sembrados que no están en el ambiente;
- se cubre solo por pruebas de integración (se referencia, no se duplica).
