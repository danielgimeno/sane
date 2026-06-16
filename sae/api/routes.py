from fastapi import APIRouter, HTTPException

from sae.catalog.registry import registry
from sae.examples.loader import example_registry
from sae.models.canvas import Canvas
from sae.models.example import ArchitectureExample

router = APIRouter(prefix="/api")


@router.get("/catalog")
def get_catalog():
    return registry.list_by_category()


@router.get("/catalog/{element_type}")
def get_element(element_type: str):
    el = registry.get(element_type)
    if not el:
        return {"error": "not found"}
    return el


@router.get("/examples")
def get_examples():
    return example_registry.list_by_category()


@router.get("/examples/{example_id}")
def get_example(example_id: str):
    example = example_registry.get(example_id)
    if not example:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    return example


@router.post("/examples")
def create_example(example: ArchitectureExample):
    if example_registry.get(example.id):
        raise HTTPException(status_code=409, detail="Ya existe un ejemplo con ese ID")
    example_registry.save(example)
    return example


@router.put("/examples/{example_id}")
def update_example(example_id: str, example: ArchitectureExample):
    if not example_registry.get(example_id):
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    example_registry.save(example, old_id=example_id)
    return example


@router.delete("/examples/{example_id}")
def delete_example(example_id: str):
    if not example_registry.delete(example_id):
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    return {"ok": True}


@router.get("/examples/{example_id}/canvas")
def get_example_canvas(example_id: str):
    example = example_registry.get(example_id)
    if not example:
        raise HTTPException(status_code=404, detail="Ejemplo no encontrado")
    return example_registry.to_canvas(example)


@router.post("/canvas/validate")
def validate_canvas(canvas: Canvas):
    errors = []
    node_ids = {n.id for n in canvas.nodes}
    for conn in canvas.connections:
        if conn.source not in node_ids:
            errors.append(f"Conexión {conn.id}: source {conn.source} no existe")
        if conn.target not in node_ids:
            errors.append(f"Conexión {conn.id}: target {conn.target} no existe")
    return {"valid": len(errors) == 0, "errors": errors}
