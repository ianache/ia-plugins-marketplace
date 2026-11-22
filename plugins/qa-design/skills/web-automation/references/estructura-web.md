# Estructura de la suite web y del reporte

## Ubicación en el repositorio del AUT

```
<repositorio-del-AUT>/
└── test/
    └── functional/
        ├── playwright/          # framework PLAYWRIGHT (ruta que usa la plantilla playwright.yaml de ci-cd)
        │   ├── package.json
        │   ├── playwright.config.ts
        │   ├── tests/           # un archivo por funcionalidad, un test por TC
        │   ├── pages/           # page objects reutilizables
        │   └── fixtures/        # datos y sesiones; sin credenciales
        └── selenium/            # framework SELENIUM (la plantilla de CI aún no existe)
            ├── pom.xml o package.json
            ├── src/test/...     # un test por TC, page objects en pages/
            └── resources/config/
```

- Si el repositorio ya tiene una suite en esa ruta, se extiende; no se crea otra.
- Las rutas son relativas a la raíz del repositorio. No se usan rutas absolutas.

## Convención de nombres

- **Archivo:** `<funcionalidad>.spec.ts` (Playwright) o `<Funcionalidad>Test.java` (Selenium).
- **Test:** el nombre incluye el `TC-ID`, por ejemplo `TC-SHELL-012 - Cambio de unidad de medida`. La etiqueta `@TC-SHELL-012` también sirve y es la forma que el validador busca en el código.
- **Page object:** una clase por página o componente del Shell o de la aplicación.

## Datos y configuración

- Las URLs y los usuarios vienen de variables de entorno (`BASE_URL`, `TEST_USER_<ROL>`).
- Las credenciales van en secretos del pipeline. Nunca en el código ni en el reporte.
- Los datos de prueba vienen del `TDA` del run. Si un dato no existe, el test se marca como bloqueado; no se inventa.

## Reporte `web-automation-report.yaml`

```yaml
aut: "<ID del documento WEB en la KB>"
framework: PLAYWRIGHT           # o SELENIUM
rama: "feature/<nombre>"
commit: "<SHA de 40 caracteres>"
casos:
  - id: TC-SHELL-012
    estado: AUTOMATED           # AUTOMATED | PARTIAL | NOT_AUTOMATED
    archivos:
      - test/functional/playwright/tests/unidades.spec.ts
acs_sin_automatizar:
  - ac: "AC-03 del TC-SHELL-015"
    motivo: "Requiere datos sembrados que no existen en el ambiente QA"
ejecucion:
  estado: NOT_EXECUTED          # EXECUTED | NOT_EXECUTED
  razon: "El MR aún no ha disparado el pipeline"
```

Cuando el pipeline termina, el engineer actualiza el bloque así:

```yaml
ejecucion:
  estado: EXECUTED
  pipeline: "<ID o URL real del pipeline>"
  resultados: {total: 12, passed: 11, failed: 1}
```

## Qué comprueba el validador

`scripts/validar_reporte_web.py` revisa el reporte, no la suite:

1. Campos obligatorios: `aut`, `framework`, `casos` y `ejecucion`.
2. `framework` en `PLAYWRIGHT` o `SELENIUM`.
3. `casos[].id` con formato `TC-*`, sin duplicados.
4. `casos[].estado` dentro de su lista cerrada.
5. `ejecucion.estado` en `EXECUTED` o `NOT_EXECUTED`, con `pipeline` y `resultados` si es `EXECUTED`, y `razon` si es `NOT_EXECUTED`.
6. Ausencia de patrones de secreto: contraseñas, tokens o URLs con credenciales.

No revisa las aserciones ni el resultado real del pipeline. Eso exige revisión humana y la evidencia de la CI.
