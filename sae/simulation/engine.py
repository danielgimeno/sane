from __future__ import annotations

import heapq
import random
import uuid
from dataclasses import dataclass, field
from typing import Any

from sae.models.canvas import Canvas, Connection
from sae.models.simulation import NodeMetrics, SimulationMetrics


@dataclass(order=True)
class SimEvent:
    time: float
    priority: int
    event_type: str = field(compare=False)
    request_id: str = field(compare=False, default="")
    node_id: str = field(compare=False, default="")
    target_id: str = field(compare=False, default="")
    payload: dict[str, Any] = field(compare=False, default_factory=dict)


@dataclass
class SimRequest:
    id: str
    created_at: float
    path: list[str] = field(default_factory=list)
    latency_ms: float = 0.0
    status: str = "pending"  # pending, completed, failed


class SimulationEngine:
    """Motor de simulación por eventos discretos."""

    def __init__(self, canvas: Canvas) -> None:
        self.canvas = canvas
        self.clock: float = 0.0
        self.event_queue: list[SimEvent] = []
        self.metrics = SimulationMetrics()
        self.requests: dict[str, SimRequest] = {}
        self._running = False
        self._speed = 1.0
        self._duration = 30.0

        self._adjacency: dict[str, list[tuple[str, str, str]]] = {}
        self._reverse_adjacency: dict[str, list[tuple[str, str, str]]] = {}
        self._node_map: dict[str, dict] = {}
        self._lb_state: dict[str, int] = {}
        self._lb_connections: dict[str, int] = {}
        self._server_busy: dict[str, int] = {}
        self._server_queues: dict[str, list[str]] = {}

        self._build_graph()

    def _build_graph(self) -> None:
        self._adjacency.clear()
        self._reverse_adjacency.clear()
        self._node_map = {n.id: n.model_dump() for n in self.canvas.nodes}

        for conn in self.canvas.connections:
            self._adjacency.setdefault(conn.source, []).append(
                (conn.target, conn.source_handle, conn.target_handle)
            )
            self._reverse_adjacency.setdefault(conn.target, []).append(
                (conn.source, conn.source_handle, conn.target_handle)
            )

        for node in self.canvas.nodes:
            self._lb_state[node.id] = 0
            self._lb_connections[node.id] = 0
            self._server_busy[node.id] = 0
            self._server_queues[node.id] = []

            if node.type not in self.metrics.nodes:
                self.metrics.nodes[node.id] = NodeMetrics(node_id=node.id)

    def _param(self, node_id: str, key: str, default: Any = None) -> Any:
        node = self._node_map.get(node_id, {})
        return node.get("parameters", {}).get(key, default)

    def _node_type(self, node_id: str) -> str:
        return self._node_map.get(node_id, {}).get("type", "")

    def _schedule(self, time: float, event_type: str, **kwargs: Any) -> None:
        heapq.heappush(
            self.event_queue,
            SimEvent(time=time, priority=0, event_type=event_type, **kwargs),
        )

    def start(self, duration: float = 30.0, speed: float = 1.0) -> None:
        self._running = True
        self._duration = duration
        self._speed = speed
        self.clock = 0.0
        self.event_queue.clear()
        self.requests.clear()
        self.metrics = SimulationMetrics()
        self._build_graph()

        for node in self.canvas.nodes:
            if node.type == "user":
                rps = float(self._param(node.id, "requests_per_second", 10))
                if rps > 0:
                    interval = 1.0 / rps
                    self._schedule(0.0, "generate_request", node_id=node.id, payload={"interval": interval})

            elif node.type == "cron_job":
                interval = float(self._param(node.id, "interval_seconds", 60))
                self._schedule(0.0, "cron_trigger", node_id=node.id, payload={"interval": interval})

    def stop(self) -> None:
        self._running = False

    def step(self, dt: float = 0.1) -> SimulationMetrics:
        if not self._running:
            return self.metrics

        target_time = min(self.clock + dt * self._speed, self._duration)
        while self.event_queue and self.event_queue[0].time <= target_time:
            event = heapq.heappop(self.event_queue)
            self.clock = event.time
            self._process_event(event)

        self.clock = target_time
        self.metrics.elapsed_seconds = self.clock

        if self.clock >= self._duration:
            self._running = False
            self.event_queue.clear()

        return self.metrics

    def _process_event(self, event: SimEvent) -> None:
        handlers = {
            "generate_request": self._handle_generate,
            "cron_trigger": self._handle_cron,
            "arrive": self._handle_arrive,
            "process_complete": self._handle_process_complete,
        }
        handler = handlers.get(event.event_type)
        if handler:
            handler(event)

    def _handle_generate(self, event: SimEvent) -> None:
        if not self._running or self.clock >= self._duration:
            return
        node_id = event.node_id
        interval = event.payload.get("interval", 0.1)

        req_id = str(uuid.uuid4())[:8]
        req = SimRequest(id=req_id, created_at=self.clock)
        self.requests[req_id] = req
        self.metrics.total_requests += 1

        nm = self.metrics.nodes[node_id]
        nm.requests_received += 1
        nm.extra["generated"] = nm.extra.get("generated", 0) + 1

        for target_id, _, _ in self._adjacency.get(node_id, []):
            self._schedule(
                self.clock,
                "arrive",
                request_id=req_id,
                node_id=target_id,
                payload={"from": node_id},
            )

        if self.clock + interval <= self._duration:
            self._schedule(
                self.clock + interval,
                "generate_request",
                node_id=node_id,
                payload={"interval": interval},
            )

    def _handle_cron(self, event: SimEvent) -> None:
        if not self._running or self.clock >= self._duration:
            return
        node_id = event.node_id
        interval = event.payload.get("interval", 60)
        jitter = float(self._param(node_id, "jitter_ms", 0)) / 1000.0

        req_id = str(uuid.uuid4())[:8]
        req = SimRequest(id=req_id, created_at=self.clock)
        self.requests[req_id] = req
        self.metrics.total_requests += 1

        for target_id, _, _ in self._adjacency.get(node_id, []):
            self._schedule(self.clock, "arrive", request_id=req_id, node_id=target_id)

        next_interval = interval + random.uniform(0, jitter)
        if self.clock + next_interval <= self._duration:
            self._schedule(
                self.clock + next_interval,
                "cron_trigger",
                node_id=node_id,
                payload={"interval": interval},
            )

    def _handle_arrive(self, event: SimEvent) -> None:
        req_id = event.request_id
        node_id = event.node_id
        req = self.requests.get(req_id)
        if not req:
            return

        req.path.append(node_id)
        node_type = self._node_type(node_id)
        nm = self.metrics.nodes.setdefault(node_id, NodeMetrics(node_id=node_id))
        nm.requests_received += 1

        process_time_ms = self._compute_process_time(node_id, node_type, req)
        req.latency_ms += process_time_ms

        if process_time_ms < 0:
            nm.requests_failed += 1
            self.metrics.failed_requests += 1
            req.status = "failed"
            return

        process_time_s = process_time_ms / 1000.0
        self._schedule(
            self.clock + process_time_s,
            "process_complete",
            request_id=req_id,
            node_id=node_id,
            payload={"process_time_ms": process_time_ms},
        )

    def _compute_process_time(self, node_id: str, node_type: str, req: SimRequest) -> float:
        if node_type == "load_balancer":
            return self._process_load_balancer(node_id)

        if node_type == "web_server":
            return self._process_web_server(node_id)

        if node_type == "database":
            return float(self._param(node_id, "query_time_ms", 10))

        if node_type == "redis":
            hit = random.random() < float(self._param(node_id, "hit_ratio", 0.9))
            return float(self._param(node_id, "get_time_ms" if hit else "set_time_ms", 0.5))

        if node_type == "celery_queue":
            enqueue = float(self._param(node_id, "enqueue_time_ms", 2))
            workers = int(self._param(node_id, "workers", 4))
            queue_len = len(self._server_queues.get(node_id, []))
            task_time = float(self._param(node_id, "task_time_ms", 100))
            wait = (queue_len / max(workers, 1)) * (task_time / 1000.0) * 1000
            self._server_queues.setdefault(node_id, []).append(req.id)
            nm = self.metrics.nodes[node_id]
            nm.queue_depth = len(self._server_queues[node_id])
            return enqueue + wait + task_time

        if node_type == "api_gateway":
            auth = float(self._param(node_id, "auth_overhead_ms", 5))
            routing = float(self._param(node_id, "routing_overhead_ms", 2))
            return auth + routing

        if node_type == "cdn":
            hit = random.random() < float(self._param(node_id, "hit_ratio", 0.85))
            if hit:
                return float(self._param(node_id, "edge_latency_ms", 10))
            return float(self._param(node_id, "origin_latency_ms", 80))

        if node_type == "waf":
            if random.random() < float(self._param(node_id, "block_rate", 0.02)):
                return -1
            return float(self._param(node_id, "inspection_ms", 2))

        if node_type == "microservice":
            return float(self._param(node_id, "process_time_ms", 30))

        if node_type == "serverless":
            warm_pool = int(self._param(node_id, "warm_pool", 5))
            busy = self._server_busy.get(node_id, 0)
            if busy >= warm_pool:
                return float(self._param(node_id, "cold_start_ms", 200)) + float(
                    self._param(node_id, "warm_process_ms", 20)
                )
            self._server_busy[node_id] = busy + 1
            return float(self._param(node_id, "warm_process_ms", 20))

        if node_type in ("rabbitmq", "kafka", "sqs"):
            return float(self._param(node_id, "persist_overhead_ms", 1) if node_type == "rabbitmq" else 2)

        if node_type == "mongodb":
            return float(self._param(node_id, "find_time_ms", 15))

        if node_type == "elasticsearch":
            return float(self._param(node_id, "search_time_ms", 25))

        if node_type == "s3":
            return float(self._param(node_id, "get_latency_ms", 50))

        if node_type == "reverse_proxy":
            return float(self._param(node_id, "tls_overhead_ms", 3))

        if node_type == "graphql":
            return float(self._param(node_id, "resolver_time_ms", 15))

        if node_type == "docker":
            return float(self._param(node_id, "startup_ms", 0) * 0.01) + 5

        if node_type in ("prometheus", "log_aggregator", "kubernetes"):
            return 1.0

        return 5.0

    def _process_load_balancer(self, node_id: str) -> float:
        algorithm = self._param(node_id, "algorithm", "round_robin")
        targets = [t for t, _, _ in self._adjacency.get(node_id, [])]

        if not targets:
            return 0.5

        if algorithm == "round_robin":
            idx = self._lb_state[node_id] % len(targets)
            self._lb_state[node_id] += 1
            chosen = targets[idx]
        elif algorithm == "least_connections":
            chosen = min(targets, key=lambda t: self._lb_connections.get(t, 0))
            self._lb_connections[chosen] = self._lb_connections.get(chosen, 0) + 1
        elif algorithm == "random":
            chosen = random.choice(targets)
        elif algorithm == "weighted":
            idx = self._lb_state[node_id] % len(targets)
            self._lb_state[node_id] += 1
            chosen = targets[idx]
        else:
            chosen = targets[0]

        nm = self.metrics.nodes[node_id]
        nm.extra.setdefault("distribution", {})
        dist = nm.extra["distribution"]
        dist[chosen] = dist.get(chosen, 0) + 1

        return float(self._param(node_id, "connection_timeout_ms", 3))

    def _process_web_server(self, node_id: str) -> float:
        workers = int(self._param(node_id, "workers", 4))
        process_ms = float(self._param(node_id, "process_time_ms", 50))
        max_queue = int(self._param(node_id, "max_queue", 100))
        error_rate = float(self._param(node_id, "error_rate", 0.01))

        busy = self._server_busy.get(node_id, 0)
        queue = self._server_queues.setdefault(node_id, [])

        if busy >= workers and len(queue) >= max_queue:
            return -1

        if busy >= workers:
            queue.append("waiting")
            wait_ms = (len(queue) / workers) * process_ms
            nm = self.metrics.nodes[node_id]
            nm.queue_depth = len(queue)
            return wait_ms + process_ms

        self._server_busy[node_id] = busy + 1
        nm = self.metrics.nodes[node_id]
        nm.current_load = self._server_busy[node_id] / workers

        if random.random() < error_rate:
            self._server_busy[node_id] -= 1
            return -1

        return process_ms

    def _handle_process_complete(self, event: SimEvent) -> None:
        req_id = event.request_id
        node_id = event.node_id
        req = self.requests.get(req_id)
        if not req:
            return

        node_type = self._node_type(node_id)
        nm = self.metrics.nodes.setdefault(node_id, NodeMetrics(node_id=node_id))
        nm.requests_processed += 1

        process_ms = event.payload.get("process_time_ms", 0)
        count = nm.requests_processed
        nm.avg_latency_ms = ((nm.avg_latency_ms * (count - 1)) + process_ms) / count

        if node_type == "web_server":
            self._server_busy[node_id] = max(0, self._server_busy.get(node_id, 1) - 1)
            queue = self._server_queues.get(node_id, [])
            if queue:
                queue.pop(0)
                nm.queue_depth = len(queue)
            workers = int(self._param(node_id, "workers", 4))
            nm.current_load = self._server_busy.get(node_id, 0) / workers

        if node_type == "celery_queue":
            q = self._server_queues.get(node_id, [])
            if q and req_id in q:
                q.remove(req_id)
            nm.queue_depth = len(q)

        if node_type == "serverless":
            self._server_busy[node_id] = max(0, self._server_busy.get(node_id, 1) - 1)

        if node_type == "load_balancer":
            algorithm = self._param(node_id, "algorithm", "round_robin")
            targets = [t for t, _, _ in self._adjacency.get(node_id, [])]
            if targets:
                if algorithm == "round_robin":
                    idx = (self._lb_state.get(node_id, 1) - 1) % len(targets)
                    target = targets[idx]
                elif algorithm == "least_connections":
                    target = min(targets, key=lambda t: self._lb_connections.get(t, 0))
                else:
                    target = targets[0]

                self._schedule(
                    self.clock,
                    "arrive",
                    request_id=req_id,
                    node_id=target,
                    payload={"from": node_id},
                )
                return

        downstream = self._adjacency.get(node_id, [])
        if downstream:
            for target_id, _, _ in downstream:
                self._schedule(
                    self.clock,
                    "arrive",
                    request_id=req_id,
                    node_id=target_id,
                    payload={"from": node_id},
                )
        else:
            req.status = "completed"
            self.metrics.completed_requests += 1

    @property
    def is_running(self) -> bool:
        return self._running
