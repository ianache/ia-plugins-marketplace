# Especificaciones de las evaluaciones del curso RED-201 (contenido verificado en los laboratorios)
CURSO = "RED-201 — Redis Avanzado: Arquitectura, Alta Disponibilidad y Rendimiento"

COMUN_RUBRICA = [
    ("Precisión conceptual",
     "Explica causas y conceptos con términos correctos y sin errores.",
     "Explica con errores menores que no cambian la conclusión.",
     "Explicación parcial o imprecisa.",
     "No identifica el concepto o lo explica de forma incorrecta."),
    ("Solución propuesta",
     "Propone una solución completa, viable y coherente con el caso.",
     "Propone una solución viable pero incompleta.",
     "La solución es parcial o poco justificada.",
     "No propone solución o es inviable."),
    ("Uso de comandos y parámetros",
     "Usa los comandos y parámetros correctos con la sintaxis adecuada.",
     "Usa los comandos correctos con errores menores de sintaxis.",
     "Menciona comandos relevantes pero con errores importantes.",
     "No usa comandos o son incorrectos."),
    ("Claridad y justificación",
     "Redacta de forma clara y justifica cada decisión.",
     "Redacta con claridad pero justifica solo parte de las decisiones.",
     "Redacción confusa o con poca justificación.",
     "No se entiende o no justifica."),
]
RUBRICA_FINAL = [COMUN_RUBRICA[0], COMUN_RUBRICA[1], COMUN_RUBRICA[3]]


def S(q, opts, ok, bloom, o):
    return dict(q=q, opts=opts, ok=ok, bloom=bloom, o=o)


def VF(q, ans, just, bloom, o):
    return dict(q=q, ans=ans, just=just, bloom=bloom, o=o)


def C(q, ans, bloom, o, alt=None):
    return dict(q=q, ans=ans, bloom=bloom, o=o, alt=alt or [])


def M(q, opts, oks, bloom, o, pts=3):
    return dict(q=q, opts=opts, oks=oks, bloom=bloom, o=o, pts=pts)


SPECS = {}

# ---------------------------------------------------------------- L1
SPECS["L1"] = dict(
    code="RED-201-L1-EV", folder="RED-201-L1", leccion="Lección 1 de 5 — Estructuras de datos avanzadas: Streams, HyperLogLog, Bitmaps y Geo",
    titulo="Evaluación de la Lección 1: Estructuras de datos avanzadas", tipo="Formativa", minutos=30, recursos="Con apuntes (guía de laboratorio y presentación)",
    obj=[("1", "Implementar un flujo productor/consumidor con Streams y grupos de consumidores (XADD, XREADGROUP, XACK)."),
         ("2", "Aplicar HyperLogLog y Bitmaps para conteo aproximado y análisis de actividad de usuarios."),
         ("3", "Implementar búsquedas por proximidad con Geo (GEOADD, GEOSEARCH)."),
         ("4", "Analizar las restricciones de multi-clave en Redis Cluster (CROSSSLOT) y resolverlas con hash tags.")],
    simple=[
        S("¿Qué comando agrega un mensaje a un Stream?", ["XADD", "XPUSH", "LPUSH", "XSEND"], 0, "Recordar", ["1"]),
        S("En un grupo de consumidores, ¿qué comando confirma que un mensaje fue procesado?", ["XDEL", "XACK", "XCLAIM", "XTRIM"], 1, "Recordar", ["1"]),
        S("¿Qué estructura cuenta elementos únicos de forma aproximada con memoria pequeña y fija?", ["Set", "Sorted set", "HyperLogLog", "List"], 2, "Comprender", ["2"]),
        S("¿Qué comando se recomienda hoy para buscar ubicaciones dentro de un radio, en lugar del deprecado GEORADIUS?", ["GEODIST", "GEOSEARCH", "GEOPOS", "GEOHASH"], 1, "Recordar", ["3"]),
        S("¿Cuántos slots tiene Redis Cluster?", ["1024", "4096", "16384", "65536"], 2, "Recordar", ["4"]),
    ],
    vf=[
        VF("Un nodo de Redis Cluster responde MOVED cuando la clave pertenece a un slot de otro nodo.", True, "Es la redirección que indica el nodo dueño del slot (en el laboratorio, clave:1 pertenece al slot 5557).", "Comprender", ["4"]),
        VF("PFMERGE entre claves de slots distintos funciona en Redis Cluster.", False, "Redis responde CROSSSLOT: todas las claves de un comando multi-clave deben estar en el mismo slot.", "Comprender", ["2", "4"]),
        VF("Con un hash tag entre llaves, solo el texto entre llaves se usa para calcular el slot.", True, "Así {visitas}:lun y {visitas}:mar caen en el mismo slot (6504 en el laboratorio).", "Comprender", ["4"]),
        VF("En un Bitmap se guarda un byte por cada usuario.", False, "Un Bitmap usa un bit por posición (por ejemplo, un bit por usuario).", "Recordar", ["2"]),
    ],
    comp=[
        C("El comando ________ agrega ubicaciones (longitud, latitud, nombre) a un conjunto geoespacial.", "GEOADD", "Recordar", ["3"]),
        C("XGROUP ________ pedidos grupo-a 0 crea un grupo de consumidores.", "CREATE", "Aplicar", ["1"]),
        C("El error ________ aparece cuando un comando multi-clave usa claves de slots distintos.", "CROSSSLOT", "Aplicar", ["4"]),
        C("En la clave {visitas}:lun, el texto que se usa para calcular el slot es ________.", "visitas", "Aplicar", ["4"], ["{visitas}"]),
    ],
    mult=M("Sobre Streams y grupos de consumidores:", ["Cada mensaje se entrega a un solo consumidor del grupo.",
           "Un mensaje entregado sigue pendiente hasta que se confirma con XACK.",
           "XREADGROUP con > devuelve mensajes ya entregados antes.",
           "XPENDING lista los mensajes entregados y no confirmados."], [0, 1, 3], "Analizar", ["1"]),
    casos=[dict(
        texto=("Una tienda en línea usa un Redis Cluster de 3 masters. Cuenta visitantes únicos por día con HyperLogLog "
               "(visitas:lun y visitas:mar) y publica los pedidos en un Stream para que 3 servicios los procesen sin duplicar "
               "trabajo. Al ejecutar PFMERGE visitas:total visitas:lun visitas:mar, el cluster responde CROSSSLOT."),
        preguntas=["Explique la causa del error y corrija los nombres de clave para que el comando funcione.",
                   "Describa el flujo con Streams (publicar, crear el grupo, consumir y confirmar) y qué ocurre con un mensaje que nunca se confirma."],
        esperados=["Las claves caen en slots distintos y un comando multi-clave exige el mismo slot (CROSSSLOT).",
                   "Usar un hash tag: {visitas}:lun, {visitas}:mar y {visitas}:total; así comparten slot.",
                   "Publicar con XADD; crear el grupo con XGROUP CREATE; consumir con XREADGROUP; confirmar con XACK.",
                   "Un mensaje entregado y no confirmado permanece pendiente (XPENDING) y puede reasignarse."],
        pts=4, rubrica=COMUN_RUBRICA, o=["1", "4"])],
)

# ---------------------------------------------------------------- L2
SPECS["L2"] = dict(
    code="RED-201-L2-EV", folder="RED-201-L2", leccion="Lección 2 de 5 — Persistencia y replicación con Sentinel",
    titulo="Evaluación de la Lección 2: Persistencia y replicación con Sentinel", tipo="Formativa", minutos=30, recursos="Con apuntes (guía de laboratorio y presentación)",
    obj=[("1", "Configurar la persistencia RDB y AOF, comparando durabilidad y rendimiento."),
         ("2", "Configurar la replicación master–réplica y verificar su estado con INFO replication."),
         ("3", "Implementar Redis Sentinel (3 sentinels, quórum 2) y provocar un failover."),
         ("4", "Evaluar una estrategia de recuperación según el RPO y el RTO, justificando la elección.")],
    simple=[
        S("¿Qué archivo genera el comando BGSAVE?", ["appendonly.aof", "dump.rdb", "nodes.conf", "sentinel.conf"], 1, "Recordar", ["1"]),
        S("¿Cuál es el valor por defecto de appendfsync?", ["always", "everysec", "no", "rewrite"], 1, "Recordar", ["1"]),
        S("Con 3 sentinels y quórum 2, ¿cuántos sentinels deben coincidir para considerar al master objetivamente caído?", ["1", "2", "3", "4"], 1, "Comprender", ["3"]),
        S("¿Qué comando le pregunta a un sentinel la dirección del master actual?", ["SENTINEL get-master-addr-by-name", "INFO replication", "ROLE", "CLUSTER NODES"], 0, "Recordar", ["3"]),
        S("¿Qué consecuencia tiene que la replicación de Redis sea asíncrona?", ["Las réplicas siempre tienen exactamente los mismos datos que el master.",
          "Escrituras confirmadas pueden perderse si el master cae antes de replicarlas.", "Las réplicas aceptan escrituras por defecto.", "El master espera a todas las réplicas antes de responder."], 1, "Comprender", ["2", "4"]),
    ],
    vf=[
        VF("Un master que se reinicia en menos tiempo que down-after-milliseconds no provoca un failover.", True, "En el laboratorio el reinicio duró 1 s y Sentinel espera 5000 ms antes de marcarlo caído.", "Comprender", ["3"]),
        VF("Una réplica con la configuración por defecto acepta escrituras.", False, "Rechaza las escrituras con el error READONLY: las réplicas son de solo lectura.", "Recordar", ["2"]),
        VF("WAIT convierte la replicación en síncrona con consistencia fuerte, sin posibilidad de perder escrituras confirmadas.", False, "WAIT solo espera confirmaciones de N réplicas y reduce el riesgo; no ofrece consistencia fuerte.", "Comprender", ["2", "4"]),
        VF("Cuando el master caído vuelve a levantarse, Sentinel lo reconfigura como réplica del nuevo master.", True, "En el laboratorio redis-1 pasó a réplica unos 16 s después de volver.", "Comprender", ["3"]),
    ],
    comp=[
        C("El comando ________ hace que el master espere la confirmación de un número de réplicas.", "WAIT", "Recordar", ["2"]),
        C("appendfsync ________ fuerza el fsync en cada escritura: es lo más seguro y lo más lento.", "always", "Aplicar", ["1"]),
        C("SENTINEL ________ redis-master fuerza un failover manual.", "failover", "Aplicar", ["3"]),
        C("El RPO es la cantidad máxima de ________ que se acepta perder.", "datos", "Recordar", ["4"], ["escrituras", "información"]),
    ],
    mult=M("Seleccione los factores que influyen en el RPO ante la caída del master:", ["La política appendfsync.", "La replicación asíncrona.",
           "El parámetro min-replicas-to-write.", "El parámetro down-after-milliseconds."], [0, 1, 2], "Analizar", ["4"]),
    casos=[dict(
        texto=("Un servicio de pagos usa 1 master, 2 réplicas y 3 sentinels con quórum 2. Configuración: appendonly yes, "
               "appendfsync everysec, replicación asíncrona y down-after-milliseconds 60000. El negocio exige no perder "
               "escrituras confirmadas (RPO cercano a cero) y recuperarse en menos de 15 segundos tras la caída del master."),
        preguntas=["Estime el RTO y el RPO de esta configuración y explique de qué parámetros dependen.",
                   "Proponga los ajustes necesarios para cumplir lo que exige el negocio e indique el costo o riesgo de cada uno."],
        esperados=["RTO: al menos down-after-milliseconds (60 s) más el tiempo de elección y promoción: no cumple los 15 s.",
                   "RPO: hasta cerca de 1 s por appendfsync everysec, más lo no replicado por ser asíncrona.",
                   "Reducir down-after-milliseconds (en el laboratorio, 5000), con el riesgo de falsos positivos.",
                   "Usar WAIT en escrituras críticas y min-replicas-to-write/min-replicas-max-lag, a costa de latencia o de rechazar escrituras.",
                   "appendfsync always reduce el RPO local pero baja el rendimiento; aun así la replicación asíncrona no garantiza RPO cero."],
        pts=4, rubrica=COMUN_RUBRICA, o=["2", "3", "4"])],
)

# ---------------------------------------------------------------- L3
SPECS["L3"] = dict(
    code="RED-201-L3-EV", folder="RED-201-L3", leccion="Lección 3 de 5 — Redis Cluster: sharding y reconfiguración en línea",
    titulo="Evaluación de la Lección 3: Redis Cluster", tipo="Formativa", minutos=30, recursos="Con apuntes (guía de laboratorio y presentación)",
    obj=[("1", "Diseñar la distribución de slots, shards y réplicas de un Redis Cluster."),
         ("2", "Agregar nodos al cluster y redistribuir slots (resharding) en línea, sin perder servicio."),
         ("3", "Retirar un nodo migrando sus slots y verificar la integridad con redis-cli --cluster check."),
         ("4", "Analizar el comportamiento del cluster ante la caída de un master.")],
    simple=[
        S("¿Cuántos slots tiene un master recién agregado con add-node, antes del resharding?", ["0", "4096", "5461", "16384"], 0, "Comprender", ["2"]),
        S("¿Qué respuesta indica que un slot cambió de dueño de forma permanente?", ["ASK", "MOVED", "CROSSSLOT", "READONLY"], 1, "Recordar", ["4"]),
        S("¿Qué comando verifica que los 16384 slots estén cubiertos y consistentes?", ["redis-cli --cluster check", "CLUSTER KEYSLOT", "INFO cluster", "CLUSTER RESET"], 0, "Recordar", ["3"]),
        S("¿Qué debe hacerse antes de retirar un master con del-node?", ["Reiniciarlo.", "Vaciarlo de slots (reshard o rebalance).", "Borrar su archivo nodes.conf.", "Cambiarle la dirección IP."], 1, "Comprender", ["3"]),
        S("¿Qué ocurre con un master caído que vuelve a levantarse tras un failover?", ["Recupera su rol de master automáticamente.", "Se reincorpora como réplica del master promovido.",
          "Es expulsado definitivamente del cluster.", "Se queda sin rol hasta que se reinicie el cluster."], 1, "Comprender", ["4"]),
    ],
    vf=[
        VF("ASK modifica el mapa de slots que mantiene el cliente.", False, "ASK es temporal (durante una migración) y el mapa no cambia; MOVED sí lo actualiza.", "Comprender", ["2", "4"]),
        VF("Agregar réplicas aumenta la capacidad de memoria total del cluster.", False, "Las réplicas aportan disponibilidad, no capacidad; la capacidad la aportan los masters.", "Comprender", ["1"]),
        VF("Con redis-cli -c, el cliente sigue las redirecciones MOVED y ASK.", True, "La opción -c activa el modo cluster y sigue las redirecciones.", "Recordar", ["4"]),
        VF("En el laboratorio, tras la caída de un master, los datos de su shard siguieron accesibles porque su réplica fue promovida.", True, "El failover tardó entre 8 y 10 s y las consultas y escrituras volvieron a funcionar.", "Comprender", ["4"]),
    ],
    comp=[
        C("redis-cli --cluster ________ mueve slots entre masters con las opciones --cluster-from y --cluster-to.", "reshard", "Aplicar", ["2"]),
        C("CLUSTER ________ clave:1 devuelve el slot de una clave.", "KEYSLOT", "Aplicar", ["1"]),
        C("Para retirar un nodo del cluster se usa redis-cli --cluster ________-node.", "del", "Aplicar", ["3"]),
        C("En el laboratorio, cluster-node-timeout vale ________ milisegundos.", "5000", "Recordar", ["4"]),
    ],
    mult=M("Seleccione las diferencias correctas entre Redis Cluster y Sentinel:", ["Cluster reparte los datos en shards.", "Cluster escala memoria y escrituras.",
           "Sentinel reparte los datos en 16384 slots.", "En Sentinel el failover lo decide un quórum de sentinels."], [0, 1, 3], "Analizar", ["1", "4"]),
    casos=[dict(
        texto=("Una empresa opera un Redis Cluster de 3 masters con una réplica cada uno. Por crecimiento de datos, necesita pasar a 4 "
               "masters sin detener el servicio. Más tarde, uno de los masters falla durante la noche. El cluster usa cluster-node-timeout de 5000."),
        preguntas=["Describa, con los comandos de redis-cli, cómo agregaría un master y su réplica y redistribuiría los slots.",
                   "Explique qué ocurre cuando cae un master (cuánto tarda aproximadamente) y qué pasa cuando ese nodo vuelve."],
        esperados=["add-node para el master nuevo y obtener su identificador con CLUSTER MYID.",
                   "add-node con --cluster-slave y --cluster-master-id para la réplica.",
                   "reshard con --cluster-from all, --cluster-to <id> y --cluster-slots 4096; verificar con --cluster check.",
                   "El resharding es en línea; los clientes se adaptan con MOVED y ASK.",
                   "Failover: la réplica es promovida en unos 8–10 s; el nodo caído vuelve como réplica."],
        pts=4, rubrica=COMUN_RUBRICA, o=["2", "3", "4"])],
)

# ---------------------------------------------------------------- L4
SPECS["L4"] = dict(
    code="RED-201-L4-EV", folder="RED-201-L4", leccion="Lección 4 de 5 — Lua y Redis Functions: lógica atómica del lado del servidor",
    titulo="Evaluación de la Lección 4: Lua y Redis Functions", tipo="Formativa", minutos=30, recursos="Con apuntes (guía de laboratorio y presentación)",
    obj=[("1", "Implementar scripts Lua con EVAL (KEYS, ARGV, redis.call) para operaciones atómicas."),
         ("2", "Desarrollar una librería de Redis Functions con FUNCTION LOAD y FCALL."),
         ("3", "Validar la atomicidad bajo concurrencia, comparando comandos separados frente a un script."),
         ("4", "Aplicar buenas prácticas de scripting en Redis Cluster.")],
    simple=[
        S("¿Por qué falla la secuencia GET + DECR bajo concurrencia?", ["Porque Redis es multihilo.", "Porque otros clientes intercalan comandos entre el GET y el DECR.",
          "Porque DECR no es atómico.", "Porque GET bloquea la clave."], 1, "Comprender", ["3"]),
        S("¿Qué tabla de Lua contiene los argumentos que no son claves en un EVAL?", ["KEYS", "ARGV", "ARGS", "PARAMS"], 1, "Recordar", ["1"]),
        S("¿Qué error devuelve EVALSHA si el script no está en la caché?", ["NOSCRIPT", "CROSSSLOT", "BUSY", "READONLY"], 0, "Recordar", ["1"]),
        S("¿Qué comando invoca una función de una librería de Redis Functions?", ["EVAL", "EVALSHA", "FCALL", "FUNCTION CALL"], 2, "Recordar", ["2"]),
        S("Además de SHUTDOWN NOSAVE, ¿qué comando acepta Redis mientras un script lo bloquea?", ["PING", "SCRIPT KILL", "FLUSHALL", "CONFIG SET"], 1, "Recordar", ["4"]),
    ],
    vf=[
        VF("Un script Lua se ejecuta de forma atómica: ningún otro comando se intercala mientras corre.", True, "Redis ejecuta el script completo como si fuera un solo comando.", "Comprender", ["1", "3"]),
        VF("Las Functions se pierden al reiniciar el servidor, igual que la caché de scripts.", False, "Las Functions persisten (en el laboratorio la librería siguió cargada); la caché de EVAL se pierde.", "Comprender", ["2"]),
        VF("En Redis Cluster, la librería de Functions debe cargarse en cada nodo.", True, "No se propaga entre masters; sin ella, el nodo responde Function not found.", "Comprender", ["4"]),
        VF("redis.pcall detiene el script y devuelve el error al cliente igual que redis.call.", False, "redis.pcall devuelve el error al propio script para que lo maneje; redis.call aborta el script.", "Comprender", ["1"]),
    ],
    comp=[
        C("En redis-cli --eval, una ________ separa las claves de los argumentos.", "coma", "Recordar", ["1"], [","]),
        C("FCALL_RO solo acepta funciones registradas con la bandera ________.", "no-writes", "Recordar", ["2"]),
        C("Para que las claves de un script caigan en el mismo slot se usa un ________.", "hash tag", "Aplicar", ["4"], ["hashtag"]),
        C("Un script largo que bloquea Redis hace que los demás clientes reciban el error ________.", "BUSY", "Recordar", ["4"]),
    ],
    mult=M("Seleccione las buenas prácticas de scripting en Redis Cluster:", ["Declarar todas las claves en KEYS.", "Usar hash tags para claves relacionadas.",
           "Construir nombres de clave dentro del script según datos leídos.", "Mantener los scripts cortos."], [0, 1, 3], "Analizar", ["4"]),
    casos=[dict(
        texto=("Una tienda tiene 100 unidades de un producto. La aplicación descuenta el stock con GET y, si es mayor que 0, DECR. "
               "En una promoción con muchos compradores a la vez se registraron 108 ventas y el stock quedó en -8. La tienda planea "
               "migrar a Redis Cluster."),
        preguntas=["Explique por qué ocurrió la sobreventa.",
                   "Proponga una solución con un script o una Function (qué hace, con qué claves y argumentos) e indique qué cuidados debe tener al usarla en Cluster."],
        esperados=["Condición de carrera: otros clientes intercalan comandos entre el GET y el DECR.",
                   "Un script o Function atómico lee el stock, compara, descuenta (DECRBY) y registra la venta en una sola operación.",
                   "Las claves (stock y ventas) se pasan en KEYS y la cantidad en ARGV.",
                   "En Cluster, las claves deben compartir slot mediante un hash tag; con Functions, cargar la librería en cada nodo.",
                   "Scripts cortos para evitar el bloqueo BUSY; ventaja de Functions: persisten y tienen nombre."],
        pts=4, rubrica=COMUN_RUBRICA, o=["1", "2", "3", "4"])],
)

# ---------------------------------------------------------------- L5
SPECS["L5"] = dict(
    code="RED-201-L5-EV", folder="RED-201-L5", leccion="Lección 5 de 5 — Rendimiento y memoria: latencia, evicción y caché",
    titulo="Evaluación de la Lección 5: Rendimiento y memoria", tipo="Formativa", minutos=30, recursos="Con apuntes (guía de laboratorio y presentación)",
    obj=[("1", "Diagnosticar comandos lentos y picos de latencia con SLOWLOG, LATENCY y redis-cli --latency."),
         ("2", "Analizar el consumo de memoria con INFO memory, MEMORY USAGE, MEMORY STATS y --bigkeys."),
         ("3", "Configurar maxmemory y comparar políticas de evicción bajo carga."),
         ("4", "Evaluar y justificar una estrategia de caché (TTL, cache-aside y evicción).")],
    simple=[
        S("¿En qué unidad se expresa el umbral slowlog-log-slower-than?", ["Milisegundos", "Microsegundos", "Segundos", "Nanosegundos"], 1, "Recordar", ["1"]),
        S("¿Cuál es la política de evicción por defecto de Redis 8.0.3 sin configuración adicional?", ["allkeys-lru", "volatile-lru", "noeviction", "allkeys-lfu"], 2, "Recordar", ["3"]),
        S("¿Qué opción de redis-cli recorre el keyspace con SCAN para hallar las claves con más elementos?", ["--latency", "--bigkeys", "--stat", "--intrinsic-latency"], 1, "Recordar", ["2"]),
        S("Con maxmemory en 0, ¿qué puede ocurrir al llenar Redis dentro de un contenedor con límite de memoria?", ["Redis evicta claves automáticamente.", "Redis rechaza las escrituras con un error OOM.",
          "El contenedor puede morir por falta de memoria (OOMKilled).", "Redis comprime los datos."], 2, "Comprender", ["3"]),
        S("¿Cómo se calcula el hit ratio de una caché?", ["keyspace_misses / keyspace_hits", "keyspace_hits / (keyspace_hits + keyspace_misses)", "keyspace_hits − keyspace_misses", "evicted_keys / used_memory"], 1, "Comprender", ["4"]),
    ],
    vf=[
        VF("Las políticas volatile-* se comportan como noeviction cuando ninguna clave tiene TTL.", True, "No hay claves evictables y Redis rechaza las escrituras (se midió igual que noeviction).", "Comprender", ["3"]),
        VF("maxmemory debe fijarse exactamente igual al límite de memoria del contenedor.", False, "Con maxmemory de 250 MB en un contenedor de 256 MB, Redis murió por OOMKilled: hay que dejar margen.", "Comprender", ["3"]),
        VF("TTL devuelve -1 cuando la clave existe y no tiene TTL.", True, "-1 significa sin TTL; -2 significa que la clave no existe.", "Recordar", ["4"]),
        VF("Dentro de un script, redis.call('TIME') sirve para medir cuánto lleva ejecutándose.", False, "Dentro de un script el reloj está congelado; en el laboratorio se usó os.clock().", "Comprender", ["1"]),
    ],
    comp=[
        C("CONFIG SET latency-monitor-threshold 100 registra eventos de más de 100 ________.", "milisegundos", "Aplicar", ["1"], ["ms"]),
        C("MEMORY ________ zbig devuelve los bytes que ocupa una clave.", "USAGE", "Aplicar", ["2"]),
        C("Con maxmemory-policy ________ Redis evicta las claves menos usadas recientemente de todo el keyspace.", "allkeys-lru", "Recordar", ["3"]),
        C("SET sesion:1 datos ________ 30 guarda la clave con un TTL de 30 segundos.", "EX", "Aplicar", ["4"]),
    ],
    mult=M("Seleccione las causas típicas de latencia alta en Redis:", ["Comandos de orden lineal como KEYS sobre muchas claves.", "Scripts largos que bloquean el servidor.",
           "El fork de RDB y la reescritura del AOF.", "Usar TTL en las claves."], [0, 1, 2], "Analizar", ["1"]),
    casos=[dict(
        texto=("El Redis interno de una organización corre en Kubernetes con 3 pods (1 master y 2 réplicas con Sentinel). El contenedor tiene "
               "límite de memoria de 8 Gi, usa unos 1,8 Gi y no tiene maxmemory definido. La misma instancia guarda datos de caché y datos "
               "que no se pueden perder."),
        preguntas=["Explique el riesgo de esta configuración al crecer el volumen de datos.",
                   "Proponga un valor de maxmemory y una política de evicción, justificando la elección y qué haría con los datos que no se pueden perder."],
        esperados=["Sin maxmemory, Redis crece hasta el límite del pod y puede ser reiniciado por OOMKilled.",
                   "maxmemory debe dejar margen bajo el límite (buffers, fork y fragmentación); en el laboratorio se usó cerca del 60 %.",
                   "allkeys-lru puede evictar datos no recuperables; volatile-* solo evicta claves con TTL y sin TTL actúa como noeviction.",
                   "Conviene separar instancias: una caché con allkeys-lru y otra para datos que no se pueden perder (noeviction).",
                   "Monitorear used_memory, RSS, evicted_keys y el hit ratio."],
        pts=4, rubrica=COMUN_RUBRICA, o=["2", "3", "4"])],
)

# ---------------------------------------------------------------- FINAL
SPECS["EF"] = dict(
    code="RED-201-EF", folder="RED-201-EF", leccion="Evaluación final — Lecciones 1 a 5",
    titulo="Evaluación final del curso RED-201", tipo="Sumativa", minutos=60, recursos="Solo apuntes, sin acceso a un Redis en ejecución",
    obj=[("L1", "Estructuras de datos avanzadas: Streams, HyperLogLog, Bitmaps y Geo."), ("L2", "Persistencia y replicación con Sentinel."),
         ("L3", "Redis Cluster: sharding y reconfiguración en línea."), ("L4", "Lua y Redis Functions."), ("L5", "Rendimiento y memoria: latencia, evicción y caché.")],
    simple=[
        S("¿Qué ocurre en Redis Cluster si un comando multi-clave usa claves de slots distintos?", ["Se ejecuta en el primer nodo consultado.", "Redis responde el error CROSSSLOT.", "Redis responde MOVED.", "Redis responde BUSY."], 1, "Comprender", ["L1", "L3"]),
        S("¿Qué parámetro de Sentinel define cuánto tiempo sin respuesta pasa antes de marcar al master como caído desde la vista de un sentinel?", ["quorum", "down-after-milliseconds", "failover-timeout", "parallel-syncs"], 1, "Recordar", ["L2"]),
        S("¿Cuál de estos elementos sobrevive al reinicio del servidor?", ["La caché de scripts de EVAL/EVALSHA.", "Una librería de Redis Functions.", "Ambos.", "Ninguno."], 1, "Comprender", ["L4"]),
        S("En una caché pura cuyas claves no tienen TTL, ¿qué política evita rechazar escrituras al llegar a maxmemory?", ["noeviction", "volatile-lru", "allkeys-lru", "volatile-ttl"], 2, "Aplicar", ["L5"]),
    ],
    vf=[
        VF("En un grupo de consumidores de Streams, cada mensaje se entrega a un solo consumidor del grupo.", True, "Los consumidores del grupo se reparten los mensajes.", "Comprender", ["L1"]),
        VF("La replicación de Redis es síncrona por defecto.", False, "Es asíncrona; WAIT permite esperar confirmaciones de réplicas pero no da consistencia fuerte.", "Recordar", ["L2"]),
        VF("El resharding en línea mueve slots y sus claves mientras el cluster sigue atendiendo consultas.", True, "Los clientes se adaptan con las redirecciones MOVED y ASK.", "Comprender", ["L3"]),
        VF("maxmemory debe ser igual al límite de memoria del contenedor.", False, "Hay que dejar margen para buffers, fork y fragmentación; de lo contrario el contenedor puede morir por OOMKilled.", "Comprender", ["L5"]),
    ],
    comp=[
        C("El error ________ indica un cambio temporal de slot durante una migración y exige enviar ASKING.", "ASK", "Aplicar", ["L3"]),
        C("El comando SLOWLOG ________ 5 muestra los últimos comandos lentos registrados.", "GET", "Aplicar", ["L5"]),
        C("El valor por defecto de appendfsync es ________.", "everysec", "Recordar", ["L2"]),
    ],
    mult=M("Seleccione las medidas que ayudan a reducir el riesgo de perder escrituras confirmadas ante la caída del master:", ["Configurar min-replicas-to-write.",
           "Usar WAIT en las escrituras críticas.", "Usar appendfsync always.", "Aumentar maxmemory."], [0, 1, 2], "Analizar", ["L2", "L5"]),
    casos=[dict(
        texto=("Una plataforma de mensajería usa 1 master, 2 réplicas y 3 sentinels. Sus datos se espera que crezcan tres veces y evalúan "
               "migrar a Redis Cluster."),
        preguntas=["Indique cuándo conviene pasar de Sentinel a Cluster y qué cambios exige en las claves multi-clave.",
                   "Compare qué ocurre al caer un master en cada arquitectura: quién decide el failover y qué parámetros influyen en el tiempo de recuperación."],
        esperados=["Cluster conviene cuando hace falta escalar memoria y escrituras repartiendo los datos en shards.",
                   "Las operaciones multi-clave exigen el mismo slot: hash tags para claves relacionadas.",
                   "Los clientes deben seguir redirecciones (MOVED/ASK).",
                   "Sentinel: un quórum de sentinels decide; influyen down-after-milliseconds y la elección.",
                   "Cluster: los propios masters votan; influye cluster-node-timeout. En ambos la replicación es asíncrona."],
        pts=3, rubrica=RUBRICA_FINAL, o=["L2", "L3"]),
        dict(
        texto=("En el Redis interno de una organización (Kubernetes, 3 pods con Sentinel, límite de 8 Gi y sin maxmemory) se guarda un contador "
               "de stock actualizado con GET y DECR y, además, datos de caché. En promociones aparecen ventas por encima del stock y, al crecer "
               "el volumen de datos, el pod se reinicia."),
        preguntas=["Diagnostique ambos problemas y su causa.",
                   "Proponga soluciones concretas (script o Function, y maxmemory con política) e indique cómo verificaría el resultado."],
        esperados=["Sobreventa: condición de carrera entre GET y DECR.",
                   "Reinicios: sin maxmemory, el uso llega al límite del pod y Kubernetes lo reinicia (OOMKilled).",
                   "Solución del stock: script o Function atómico (claves en KEYS).",
                   "Solución de memoria: maxmemory con margen y política adecuada; separar la caché (allkeys-lru) de los datos que no se pueden perder.",
                   "Verificación: prueba de concurrencia con stock final correcto, INFO memory, evicted_keys, hit ratio y SLOWLOG."],
        pts=3, rubrica=RUBRICA_FINAL, o=["L4", "L5"])],
)
