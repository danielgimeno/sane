from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ParameterType = Literal["number", "integer", "string", "boolean", "select"]


class ParameterDef(BaseModel):
    key: str
    label: str
    type: ParameterType = "number"
    default: Any = None
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: list[str] | None = None
    unit: str | None = None
    description: str | None = None


class PortDef(BaseModel):
    id: str
    label: str
    type: Literal["input", "output"]


class ElementDefinition(BaseModel):
    type: str
    label: str
    category: str
    icon: str
    color: str = "#6366f1"
    description: str = ""
    inputs: list[PortDef] = Field(default_factory=list)
    outputs: list[PortDef] = Field(default_factory=list)
    parameters: list[ParameterDef] = Field(default_factory=list)
    simulatable: bool = True
