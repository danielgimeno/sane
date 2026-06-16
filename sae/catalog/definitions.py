from sae.models.elements import ElementDefinition, ParameterDef, PortDef

# ── Fuentes / Clientes ──────────────────────────────────────────────────────

USER = ElementDefinition(
    type="user",
    label="Usuario",
    category="Fuentes",
    icon="👤",
    color="#22c55e",
    description="Genera peticiones HTTP simuladas hacia la arquitectura",
    outputs=[PortDef(id="requests", label="Peticiones", type="output")],
    parameters=[
        ParameterDef(key="requests_per_second", label="Peticiones/seg", type="number", default=10, min=0.1, max=10000, step=0.1),
        ParameterDef(key="burst_size", label="Ráfaga máxima", type="integer", default=50, min=1, max=10000),
        ParameterDef(key="think_time_ms", label="Tiempo entre peticiones", type="number", default=0, min=0, max=60000, unit="ms"),
    ],
)

CRON_JOB = ElementDefinition(
    type="cron_job",
    label="Cron Job",
    category="Fuentes",
    icon="⏰",
    color="#84cc16",
    description="Tarea programada que dispara eventos periódicamente",
    outputs=[PortDef(id="trigger", label="Trigger", type="output")],
    parameters=[
        ParameterDef(key="interval_seconds", label="Intervalo", type="number", default=60, min=1, max=86400, unit="s"),
        ParameterDef(key="jitter_ms", label="Jitter", type="number", default=0, min=0, max=5000, unit="ms"),
    ],
)

WEBHOOK = ElementDefinition(
    type="webhook",
    label="Webhook",
    category="Fuentes",
    icon="🔗",
    color="#a3e635",
    description="Punto de entrada externo que recibe callbacks",
    outputs=[PortDef(id="events", label="Eventos", type="output")],
    parameters=[
        ParameterDef(key="rate_limit_rps", label="Rate limit", type="number", default=100, min=1, max=10000),
        ParameterDef(key="timeout_ms", label="Timeout", type="number", default=5000, min=100, max=60000, unit="ms"),
    ],
)

# ── Red / Balanceo ──────────────────────────────────────────────────────────

LOAD_BALANCER = ElementDefinition(
    type="load_balancer",
    label="Balanceador",
    category="Red",
    icon="⚖️",
    color="#3b82f6",
    description="Distribuye peticiones entre backends según algoritmo",
    inputs=[PortDef(id="in", label="Entrada", type="input")],
    outputs=[PortDef(id="out", label="Salida", type="output")],
    parameters=[
        ParameterDef(
            key="algorithm",
            label="Algoritmo",
            type="select",
            default="round_robin",
            options=["round_robin", "least_connections", "weighted", "random", "ip_hash"],
        ),
        ParameterDef(key="health_check_ms", label="Health check", type="number", default=5000, min=500, max=60000, unit="ms"),
        ParameterDef(key="connection_timeout_ms", label="Timeout conexión", type="number", default=3000, min=100, max=30000, unit="ms"),
    ],
)

API_GATEWAY = ElementDefinition(
    type="api_gateway",
    label="API Gateway",
    category="Red",
    icon="🚪",
    color="#2563eb",
    description="Punto de entrada unificado con rate limiting y routing",
    inputs=[PortDef(id="in", label="Entrada", type="input")],
    outputs=[PortDef(id="out", label="Salida", type="output")],
    parameters=[
        ParameterDef(key="rate_limit_rps", label="Rate limit global", type="number", default=1000, min=1, max=100000),
        ParameterDef(key="auth_overhead_ms", label="Overhead auth", type="number", default=5, min=0, max=1000, unit="ms"),
        ParameterDef(key="routing_overhead_ms", label="Overhead routing", type="number", default=2, min=0, max=500, unit="ms"),
    ],
)

CDN = ElementDefinition(
    type="cdn",
    label="CDN",
    category="Red",
    icon="🌐",
    color="#0ea5e9",
    description="Cache edge que sirve contenido estático con hit ratio configurable",
    inputs=[PortDef(id="in", label="Origen", type="input")],
    outputs=[PortDef(id="out", label="Edge", type="output")],
    parameters=[
        ParameterDef(key="hit_ratio", label="Hit ratio", type="number", default=0.85, min=0, max=1, step=0.01),
        ParameterDef(key="edge_latency_ms", label="Latencia edge", type="number", default=10, min=1, max=500, unit="ms"),
        ParameterDef(key="origin_latency_ms", label="Latencia origen", type="number", default=80, min=1, max=2000, unit="ms"),
    ],
)

REVERSE_PROXY = ElementDefinition(
    type="reverse_proxy",
    label="Reverse Proxy",
    category="Red",
    icon="🔀",
    color="#0284c7",
    description="Nginx/Traefik — termina TLS y reenvía",
    inputs=[PortDef(id="in", label="Entrada", type="input")],
    outputs=[PortDef(id="out", label="Backend", type="output")],
    parameters=[
        ParameterDef(key="tls_overhead_ms", label="Overhead TLS", type="number", default=3, min=0, max=100, unit="ms"),
        ParameterDef(key="max_connections", label="Conexiones máx", type="integer", default=1000, min=10, max=100000),
        ParameterDef(key="keepalive_timeout_s", label="Keep-alive", type="number", default=65, min=1, max=300, unit="s"),
    ],
)

WAF = ElementDefinition(
    type="waf",
    label="WAF",
    category="Red",
    icon="🛡️",
    color="#dc2626",
    description="Web Application Firewall — filtra tráfico malicioso",
    inputs=[PortDef(id="in", label="Entrada", type="input")],
    outputs=[PortDef(id="out", label="Salida", type="output")],
    parameters=[
        ParameterDef(key="block_rate", label="Tasa de bloqueo", type="number", default=0.02, min=0, max=1, step=0.001),
        ParameterDef(key="inspection_ms", label="Inspección", type="number", default=2, min=0, max=100, unit="ms"),
    ],
)

# ── Aplicación ──────────────────────────────────────────────────────────────

WEB_SERVER = ElementDefinition(
    type="web_server",
    label="Servidor Web",
    category="Aplicación",
    icon="🖥️",
    color="#8b5cf6",
    description="Servidor HTTP (Gunicorn/uWSGI) que procesa peticiones",
    inputs=[PortDef(id="in", label="HTTP", type="input")],
    outputs=[PortDef(id="out", label="Respuesta", type="output")],
    parameters=[
        ParameterDef(key="workers", label="Workers", type="integer", default=4, min=1, max=128),
        ParameterDef(key="process_time_ms", label="Tiempo proceso", type="number", default=50, min=1, max=60000, unit="ms"),
        ParameterDef(key="max_queue", label="Cola máxima", type="integer", default=100, min=1, max=10000),
        ParameterDef(key="error_rate", label="Tasa de error", type="number", default=0.01, min=0, max=1, step=0.001),
    ],
)

MICROSERVICE = ElementDefinition(
    type="microservice",
    label="Microservicio",
    category="Aplicación",
    icon="🧩",
    color="#a855f7",
    description="Servicio independiente con latencia y dependencias",
    inputs=[PortDef(id="in", label="RPC/HTTP", type="input")],
    outputs=[PortDef(id="out", label="Respuesta", type="output")],
    parameters=[
        ParameterDef(key="instances", label="Réplicas", type="integer", default=2, min=1, max=50),
        ParameterDef(key="process_time_ms", label="Tiempo proceso", type="number", default=30, min=1, max=60000, unit="ms"),
        ParameterDef(key="cpu_limit", label="CPU limit", type="number", default=1.0, min=0.1, max=16, step=0.1, unit="cores"),
        ParameterDef(key="memory_mb", label="Memoria", type="integer", default=512, min=64, max=32768, unit="MB"),
    ],
)

SERVERLESS = ElementDefinition(
    type="serverless",
    label="Lambda / Serverless",
    category="Aplicación",
    icon="⚡",
    color="#d946ef",
    description="Función serverless con cold start y concurrencia",
    inputs=[PortDef(id="in", label="Invoke", type="input")],
    outputs=[PortDef(id="out", label="Result", type="output")],
    parameters=[
        ParameterDef(key="cold_start_ms", label="Cold start", type="number", default=200, min=0, max=10000, unit="ms"),
        ParameterDef(key="warm_process_ms", label="Proceso warm", type="number", default=20, min=1, max=60000, unit="ms"),
        ParameterDef(key="max_concurrency", label="Concurrencia máx", type="integer", default=100, min=1, max=10000),
        ParameterDef(key="warm_pool", label="Instancias warm", type="integer", default=5, min=0, max=1000),
    ],
)

GRAPHQL = ElementDefinition(
    type="graphql",
    label="GraphQL API",
    category="Aplicación",
    icon="◈",
    color="#c026d3",
    description="API GraphQL con resolvers y N+1 configurable",
    inputs=[PortDef(id="in", label="Query", type="input")],
    outputs=[PortDef(id="out", label="Data", type="output")],
    parameters=[
        ParameterDef(key="resolver_time_ms", label="Tiempo resolver", type="number", default=15, min=1, max=5000, unit="ms"),
        ParameterDef(key="max_depth", label="Profundidad máx", type="integer", default=10, min=1, max=50),
        ParameterDef(key="complexity_limit", label="Límite complejidad", type="integer", default=1000, min=10, max=100000),
    ],
)

# ── Colas / Mensajería ──────────────────────────────────────────────────────

CELERY_QUEUE = ElementDefinition(
    type="celery_queue",
    label="Cola Celery",
    category="Mensajería",
    icon="🥬",
    color="#f59e0b",
    description="Cola de tareas asíncronas con workers Celery",
    inputs=[PortDef(id="in", label="Encolar", type="input")],
    outputs=[PortDef(id="out", label="Resultado", type="output")],
    parameters=[
        ParameterDef(key="workers", label="Workers", type="integer", default=4, min=1, max=128),
        ParameterDef(key="enqueue_time_ms", label="Tiempo encolado", type="number", default=2, min=0, max=1000, unit="ms"),
        ParameterDef(key="task_time_ms", label="Tiempo tarea", type="number", default=100, min=1, max=600000, unit="ms"),
        ParameterDef(key="max_retries", label="Reintentos máx", type="integer", default=3, min=0, max=20),
        ParameterDef(key="prefetch", label="Prefetch", type="integer", default=4, min=1, max=100),
    ],
)

RABBITMQ = ElementDefinition(
    type="rabbitmq",
    label="RabbitMQ",
    category="Mensajería",
    icon="🐰",
    color="#f97316",
    description="Message broker AMQP con exchanges y colas",
    inputs=[PortDef(id="in", label="Publish", type="input")],
    outputs=[PortDef(id="out", label="Consume", type="output")],
    parameters=[
        ParameterDef(key="throughput_rps", label="Throughput máx", type="number", default=5000, min=10, max=1000000),
        ParameterDef(key="persist_overhead_ms", label="Overhead persist", type="number", default=1, min=0, max=100, unit="ms"),
        ParameterDef(key="queue_max", label="Cola máxima", type="integer", default=10000, min=100, max=1000000),
    ],
)

KAFKA = ElementDefinition(
    type="kafka",
    label="Kafka",
    category="Mensajería",
    icon="📨",
    color="#ea580c",
    description="Event streaming con particiones y consumer groups",
    inputs=[PortDef(id="in", label="Produce", type="input")],
    outputs=[PortDef(id="out", label="Consume", type="output")],
    parameters=[
        ParameterDef(key="partitions", label="Particiones", type="integer", default=6, min=1, max=1000),
        ParameterDef(key="replication_factor", label="Factor replicación", type="integer", default=3, min=1, max=10),
        ParameterDef(key="batch_size", label="Batch size", type="integer", default=100, min=1, max=10000),
        ParameterDef(key="linger_ms", label="Linger", type="number", default=5, min=0, max=1000, unit="ms"),
    ],
)

SQS = ElementDefinition(
    type="sqs",
    label="AWS SQS",
    category="Mensajería",
    icon="📬",
    color="#fb923c",
    description="Cola managed de AWS con visibility timeout",
    inputs=[PortDef(id="in", label="Send", type="input")],
    outputs=[PortDef(id="out", label="Receive", type="output")],
    parameters=[
        ParameterDef(key="visibility_timeout_s", label="Visibility timeout", type="number", default=30, min=0, max=43200, unit="s"),
        ParameterDef(key="delay_seconds", label="Delay", type="number", default=0, min=0, max=900, unit="s"),
        ParameterDef(key="max_messages", label="Mensajes máx", type="integer", default=120000, min=1000, max=1000000),
    ],
)

# ── Datos ───────────────────────────────────────────────────────────────────

DATABASE = ElementDefinition(
    type="database",
    label="Base de Datos",
    category="Datos",
    icon="🗄️",
    color="#ef4444",
    description="Base de datos relacional (PostgreSQL/MySQL)",
    inputs=[PortDef(id="in", label="Query", type="input")],
    outputs=[PortDef(id="out", label="Result", type="output")],
    parameters=[
        ParameterDef(key="query_time_ms", label="Tiempo query", type="number", default=10, min=0.1, max=60000, unit="ms"),
        ParameterDef(key="max_connections", label="Conexiones máx", type="integer", default=100, min=1, max=10000),
        ParameterDef(key="connection_pool", label="Pool size", type="integer", default=20, min=1, max=1000),
        ParameterDef(key="slow_query_threshold_ms", label="Umbral slow query", type="number", default=1000, min=10, max=60000, unit="ms"),
        ParameterDef(key="replication_lag_ms", label="Lag replicación", type="number", default=0, min=0, max=60000, unit="ms"),
    ],
)

REDIS = ElementDefinition(
    type="redis",
    label="Redis",
    category="Datos",
    icon="🔴",
    color="#dc2626",
    description="Cache in-memory con TTL y eviction",
    inputs=[PortDef(id="in", label="Command", type="input")],
    outputs=[PortDef(id="out", label="Response", type="output")],
    parameters=[
        ParameterDef(key="get_time_ms", label="Tiempo GET", type="number", default=0.5, min=0.01, max=100, unit="ms"),
        ParameterDef(key="set_time_ms", label="Tiempo SET", type="number", default=0.8, min=0.01, max=100, unit="ms"),
        ParameterDef(key="hit_ratio", label="Hit ratio", type="number", default=0.9, min=0, max=1, step=0.01),
        ParameterDef(key="max_memory_mb", label="Memoria máx", type="integer", default=256, min=16, max=65536, unit="MB"),
        ParameterDef(key="eviction_policy", label="Eviction", type="select", default="allkeys-lru", options=["allkeys-lru", "volatile-lru", "noeviction"]),
    ],
)

MONGODB = ElementDefinition(
    type="mongodb",
    label="MongoDB",
    category="Datos",
    icon="🍃",
    color="#16a34a",
    description="Base de datos documental NoSQL",
    inputs=[PortDef(id="in", label="Query", type="input")],
    outputs=[PortDef(id="out", label="Result", type="output")],
    parameters=[
        ParameterDef(key="find_time_ms", label="Tiempo find", type="number", default=15, min=0.1, max=60000, unit="ms"),
        ParameterDef(key="write_concern", label="Write concern", type="select", default="majority", options=["1", "majority", "all"]),
        ParameterDef(key="shards", label="Shards", type="integer", default=1, min=1, max=100),
    ],
)

ELASTICSEARCH = ElementDefinition(
    type="elasticsearch",
    label="Elasticsearch",
    category="Datos",
    icon="🔍",
    color="#ca8a04",
    description="Motor de búsqueda y analítica",
    inputs=[PortDef(id="in", label="Search", type="input")],
    outputs=[PortDef(id="out", label="Hits", type="output")],
    parameters=[
        ParameterDef(key="search_time_ms", label="Tiempo búsqueda", type="number", default=25, min=1, max=60000, unit="ms"),
        ParameterDef(key="index_shards", label="Shards índice", type="integer", default=3, min=1, max=100),
        ParameterDef(key="replicas", label="Réplicas", type="integer", default=1, min=0, max=10),
    ],
)

S3 = ElementDefinition(
    type="s3",
    label="S3 / Object Storage",
    category="Datos",
    icon="🪣",
    color="#78716c",
    description="Almacenamiento de objetos con latencia por operación",
    inputs=[PortDef(id="in", label="Request", type="input")],
    outputs=[PortDef(id="out", label="Response", type="output")],
    parameters=[
        ParameterDef(key="get_latency_ms", label="Latencia GET", type="number", default=50, min=1, max=5000, unit="ms"),
        ParameterDef(key="put_latency_ms", label="Latencia PUT", type="number", default=80, min=1, max=5000, unit="ms"),
        ParameterDef(key="throughput_mbps", label="Throughput", type="number", default=100, min=1, max=10000, unit="Mbps"),
    ],
)

# ── Observabilidad ──────────────────────────────────────────────────────────

PROMETHEUS = ElementDefinition(
    type="prometheus",
    label="Prometheus",
    category="Observabilidad",
    icon="📊",
    color="#e11d48",
    description="Recolección de métricas con scrape interval",
    inputs=[PortDef(id="in", label="Metrics", type="input")],
    outputs=[PortDef(id="out", label="Alerts", type="output")],
    parameters=[
        ParameterDef(key="scrape_interval_s", label="Scrape interval", type="number", default=15, min=1, max=300, unit="s"),
        ParameterDef(key="retention_days", label="Retención", type="integer", default=15, min=1, max=365, unit="días"),
    ],
)

LOG_AGGREGATOR = ElementDefinition(
    type="log_aggregator",
    label="Log Aggregator",
    category="Observabilidad",
    icon="📋",
    color="#be123c",
    description="ELK/Loki — agregación centralizada de logs",
    inputs=[PortDef(id="in", label="Logs", type="input")],
    outputs=[PortDef(id="out", label="Query", type="output")],
    parameters=[
        ParameterDef(key="ingest_rate_eps", label="Eventos/seg ingest", type="number", default=10000, min=100, max=1000000),
        ParameterDef(key="index_time_ms", label="Tiempo indexado", type="number", default=5, min=1, max=1000, unit="ms"),
    ],
)

# ── Infraestructura ─────────────────────────────────────────────────────────

KUBERNETES = ElementDefinition(
    type="kubernetes",
    label="Kubernetes",
    category="Infraestructura",
    icon="☸️",
    color="#326ce5",
    description="Orquestador de contenedores con scheduling",
    inputs=[PortDef(id="in", label="Deploy", type="input")],
    outputs=[PortDef(id="out", label="Service", type="output")],
    parameters=[
        ParameterDef(key="nodes", label="Nodos", type="integer", default=3, min=1, max=1000),
        ParameterDef(key="pods_per_node", label="Pods/nodo", type="integer", default=30, min=1, max=500),
        ParameterDef(key="scheduling_ms", label="Scheduling", type="number", default=50, min=1, max=5000, unit="ms"),
    ],
)

DOCKER = ElementDefinition(
    type="docker",
    label="Docker Container",
    category="Infraestructura",
    icon="🐳",
    color="#2496ed",
    description="Contenedor Docker con recursos limitados",
    inputs=[PortDef(id="in", label="Traffic", type="input")],
    outputs=[PortDef(id="out", label="Response", type="output")],
    parameters=[
        ParameterDef(key="cpu_cores", label="CPU", type="number", default=1.0, min=0.1, max=32, step=0.1),
        ParameterDef(key="memory_mb", label="Memoria", type="integer", default=512, min=64, max=65536, unit="MB"),
        ParameterDef(key="startup_ms", label="Startup", type="number", default=500, min=0, max=60000, unit="ms"),
    ],
)

ALL_ELEMENTS = [
    USER, CRON_JOB, WEBHOOK,
    LOAD_BALANCER, API_GATEWAY, CDN, REVERSE_PROXY, WAF,
    WEB_SERVER, MICROSERVICE, SERVERLESS, GRAPHQL,
    CELERY_QUEUE, RABBITMQ, KAFKA, SQS,
    DATABASE, REDIS, MONGODB, ELASTICSEARCH, S3,
    PROMETHEUS, LOG_AGGREGATOR,
    KUBERNETES, DOCKER,
]
