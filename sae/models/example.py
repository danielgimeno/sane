from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NodeConnectionRef(BaseModel):
    """Referencia a un nodo conectado y los puertos implicados."""

    target: str
    source_handle: str = "out"
    target_handle: str = "in"


class IncomingConnectionRef(BaseModel):
    """Conexión entrante: el nodo remoto es el origen."""

    source: str
    source_handle: str = "out"
    target_handle: str = "in"


class NodeConnections(BaseModel):
    outgoing: list[NodeConnectionRef] = Field(default_factory=list)
    incoming: list[IncomingConnectionRef] = Field(default_factory=list)


class ExampleNode(BaseModel):
    id: str
    type: str
    label: str
    position: dict[str, float]
    parameters: dict[str, Any] = Field(default_factory=dict)
    connections: NodeConnections = Field(default_factory=NodeConnections)


class ArchitectureExample(BaseModel):
    id: str
    title: str
    description: str
    category: str
    nodes: list[ExampleNode]


class ExampleSummary(BaseModel):
    id: str
    title: str
    description: str
    category: str
    node_count: int
