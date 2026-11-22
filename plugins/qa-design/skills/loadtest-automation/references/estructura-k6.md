# Estructura de la suite k6

## 1. Árbol

```text
codebase/<microservicio>/test/load/
├── k6.js                      archivo principal (lo ejecuta k6)
├── scenarios/
│   ├── TC-PE-01.js            un módulo por TC de carga
│   └── TC-PE-02.js
├── lib/
│   └── config.js              variables de entorno; sin secretos
├── data/
│   └── <dataset>.json         datos de entrada
├── loadtest-automation-report.yaml   (opcional en el repo; normalmente va al pack)
└── README.md
```

## 2. Primera línea de `k6.js`: criterio

```js
// criterio: BASELINE
```

o, con umbrales aprobados:

```js
// criterio: APROBADO DATA-04
```

El validador exige esta línea. En BASELINE no hay umbrales; la corrida registra la línea base.

## 3. `k6.js` (principal)

```js
// criterio: BASELINE
export { tc01 } from './scenarios/TC-PE-01.js';

export const options = {
  scenarios: {
    'TC-PE-01': {
      executor: 'constant-vus',
      vus: 5,               // perfil del TC: usuarios virtuales
      duration: '30s',      // perfil del TC: duración
      exec: 'tc01',         // debe coincidir con un export de este archivo
      tags: { tc: 'TC-PE-01' },
    },
  },
  // thresholds: solo con criterio APROBADO y una línea
  //   // umbral-fuente: DATA-04
  //   http_req_duration{tc:TC-PE-01}: ['p(95)<1000'],
};

export function handleSummary(data) {
  // BASELINE: guardar el resumen como línea base, sin veredicto de aprobado o fallido
  return { 'baseline-summary.json': JSON.stringify(data, null, 2) };
}
```

Reglas:
- Un escenario por TC. El nombre del escenario es el ID del TC.
- `exec` referencia un export de `k6.js`, que re-exporta la función del módulo.
- Los umbrales usan la etiqueta `tc:<ID>` para aislar cada caso.

## 4. Módulo por TC (`scenarios/TC-PE-01.js`)

```js
import http from 'k6/http';
import { check } from 'k6';
import { config } from '../lib/config.js';

export function tc01() {
  const res = http.get(`${config.apiUrl}/${config.deployment}/actuator/health`, {
    tags: { tc: 'TC-PE-01' },
  });
  check(res, { 'status 200': (r) => r.status === 200 });
}
```

Reglas:
- Ninguna URL literal: se construye con `config`.
- Las aserciones (`check`) reflejan el oracle del TC; un `check` que no sale del TC es un hallazgo de revisión.
- Las etiquetas `tags` permiten filtrar métricas por caso.

## 5. Configuración (`lib/config.js`)

```js
export const config = {
  apiUrl: __ENV.API_URL,
  deployment: __ENV.DEPLOYMENT_NAME,
  token: __ENV.ACCESS_TOKEN,   // nunca un valor por defecto
};
```

- Sin valores por defecto para `API_URL` ni `ACCESS_TOKEN`: si faltan, la corrida debe fallar con un mensaje claro.
- Las variables se documentan en el `README.md`.

## 6. Datos

```js
import { SharedArray } from 'k6/data';
const rows = new SharedArray('datos', () => JSON.parse(open('../data/entradas.json')));
```

- `open()` solo acepta rutas relativas al archivo que lo llama y solo funciona durante la fase de init, no dentro de la función de VU.
- Datos de personas: sintéticos o enmascarados. Datos reales solo con autorización.

## 7. Umbrales y fuentes

| Caso | Umbral | Fuente |
|---|---|---|
| Sin cifra aprobada | Ninguno | Criterio BASELINE |
| Cifra aprobada | `http_req_duration{tc:...}: ['p(95)<X']` | `// umbral-fuente: <DATA-xx o NFR-xx>` en la línea anterior |

Un umbral copiado de otro proyecto o de una suposición no tiene fuente y debe quitarse.

## 8. Ejecución

```bash
k6 run -e API_URL=<url-del-ambiente> -e DEPLOYMENT_NAME=<servicio> -e ACCESS_TOKEN=<token> test/load/k6.js
```

Con `k6 inspect test/load/k6.js` se comprueba la configuración sin ejecutar carga.
