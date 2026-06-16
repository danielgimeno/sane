from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NodeInstance(BaseModel):
    id: str
    type: str
    label: str
    position: dict[str, float]
    parameters: dict[str, Any] = Field(default_factory=dict)


class Connection(BaseModel):
    id: str
    source: str
    source_handle: str
    target: str
    target_handle: str


class Canvas(BaseModel):
    nodes: list[NodeInstance] = Field(default_factory=list)
    connections: list[Connection] = Field(default_factory=list)
