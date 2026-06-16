from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NodeMetrics(BaseModel):
    node_id: str
    requests_received: int = 0
    requests_processed: int = 0
    requests_failed: int = 0
    queue_depth: int = 0
    avg_latency_ms: float = 0.0
    current_load: float = 0.0
    extra: dict[str, Any] = Field(default_factory=dict)


class SimulationMetrics(BaseModel):
    elapsed_seconds: float = 0.0
    total_requests: int = 0
    completed_requests: int = 0
    failed_requests: int = 0
    nodes: dict[str, NodeMetrics] = Field(default_factory=dict)


class SimulationState(BaseModel):
    running: bool = False
    speed: float = 1.0
    duration_seconds: float = 30.0
    metrics: SimulationMetrics = Field(default_factory=SimulationMetrics)
