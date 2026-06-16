from sae.examples.loader import example_registry


def test_examples_load():
    examples = example_registry.list_all()
    assert len(examples) >= 5


def test_example_to_canvas():
    example = example_registry.get("load-balancer-basic")
    assert example is not None

    canvas = example_registry.to_canvas(example)
    assert len(canvas.nodes) == 4
    assert len(canvas.connections) == 3

    node_ids = {n.id for n in canvas.nodes}
    for conn in canvas.connections:
        assert conn.source in node_ids
        assert conn.target in node_ids


def test_examples_api(client):
    response = client.get("/api/examples")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0

    response = client.get("/api/examples/load-balancer-basic")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "load-balancer-basic"
    assert len(body["nodes"]) > 0
    assert "connections" in body["nodes"][0]

    response = client.get("/api/examples/load-balancer-basic/canvas")
    assert response.status_code == 200
    canvas = response.json()
    assert "nodes" in canvas
    assert "connections" in canvas

    response = client.get("/api/examples/nonexistent")
    assert response.status_code == 404


def test_examples_create_api(client):
    from sae.examples.loader import EXAMPLES_DIR, example_registry

    payload = {
        "id": "_test-create-me",
        "title": "Escenario de prueba",
        "description": "Creado en test",
        "category": "Test",
        "nodes": [],
    }
    expected_path = EXAMPLES_DIR / "Test" / "_test-create-me.json"

    try:
        response = client.post("/api/examples", json=payload)
        assert response.status_code == 200
        assert response.json()["id"] == "_test-create-me"
        assert expected_path.is_file()

        duplicate = client.post("/api/examples", json=payload)
        assert duplicate.status_code == 409
    finally:
        example_registry.delete("_test-create-me")


def test_examples_update_api(client):
    original = client.get("/api/examples/load-balancer-basic").json()
    updated = {**original, "title": "Título modificado en test"}

    response = client.put("/api/examples/load-balancer-basic", json=updated)
    assert response.status_code == 200
    assert response.json()["title"] == "Título modificado en test"

    restore = client.put("/api/examples/load-balancer-basic", json=original)
    assert restore.status_code == 200
    assert restore.json()["title"] == original["title"]


def test_examples_delete_api(client):
    from sae.examples.loader import example_registry
    from sae.models.example import ArchitectureExample

    temp = ArchitectureExample(
        id="_test-delete-me",
        title="Ejemplo temporal",
        description="Para pruebas",
        category="Test",
        nodes=[],
    )
    example_registry.save(temp)

    try:
        response = client.delete("/api/examples/_test-delete-me")
        assert response.status_code == 200
        assert client.get("/api/examples/_test-delete-me").status_code == 404
    finally:
        example_registry.delete("_test-delete-me")


def test_registry_save_and_delete(tmp_path, monkeypatch):
    import json

    from sae.examples.loader import ExampleRegistry

    sample = {
        "id": "registry-test",
        "title": "Registry Test",
        "description": "desc",
        "category": "Test",
        "nodes": [],
    }
    (tmp_path / "registry-test.json").write_text(json.dumps(sample), encoding="utf-8")
    monkeypatch.setattr("sae.examples.loader.EXAMPLES_DIR", tmp_path)

    reg = ExampleRegistry()
    assert reg.get("registry-test") is not None

    updated = reg.get("registry-test").model_copy(update={"title": "Updated"})
    reg.save(updated)
    assert reg.get("registry-test").title == "Updated"
    assert (tmp_path / "Test" / "registry-test.json").is_file()
    assert not (tmp_path / "registry-test.json").exists()

    moved = reg.get("registry-test").model_copy(update={"category": "Otros"})
    reg.save(moved)
    assert (tmp_path / "Otros" / "registry-test.json").is_file()
    assert not (tmp_path / "Test" / "registry-test.json").exists()

    assert reg.delete("registry-test") is True
    assert reg.get("registry-test") is None
    assert not (tmp_path / "Otros" / "registry-test.json").exists()
