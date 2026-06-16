from __future__ import annotations

import json
import re
from pathlib import Path

from sae.models.canvas import Canvas, Connection, NodeInstance
from sae.models.example import ArchitectureExample, ExampleSummary

EXAMPLES_DIR = Path(__file__).parent
_INVALID_DIR_CHARS = re.compile(r'[/\\:*?"<>|]')


class ExampleRegistry:
    def __init__(self) -> None:
        self._examples: dict[str, ArchitectureExample] = {}
        self._paths: dict[str, Path] = {}
        self._load_all()

    def _category_dir(self, category: str) -> str:
        name = category.strip()
        if not name:
            raise ValueError("La categoría no puede estar vacía")
        return _INVALID_DIR_CHARS.sub("-", name)

    def _path_for(self, example: ArchitectureExample) -> Path:
        return EXAMPLES_DIR / self._category_dir(example.category) / f"{example.id}.json"

    def _load_all(self) -> None:
        for path in sorted(EXAMPLES_DIR.rglob("*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            example = ArchitectureExample.model_validate(data)
            self._examples[example.id] = example
            self._paths[example.id] = path

    def list_all(self) -> list[ExampleSummary]:
        return [
            ExampleSummary(
                id=ex.id,
                title=ex.title,
                description=ex.description,
                category=ex.category,
                node_count=len(ex.nodes),
            )
            for ex in self._examples.values()
        ]

    def list_by_category(self) -> dict[str, list[ExampleSummary]]:
        grouped: dict[str, list[ExampleSummary]] = {}
        for summary in self.list_all():
            grouped.setdefault(summary.category, []).append(summary)
        return grouped

    def get(self, example_id: str) -> ArchitectureExample | None:
        return self._examples.get(example_id)

    def save(self, example: ArchitectureExample, old_id: str | None = None) -> None:
        lookup_id = old_id or example.id
        old_path = self._paths.get(lookup_id)

        if old_id and old_id != example.id:
            self._examples.pop(old_id, None)
            self._paths.pop(old_id, None)

        new_path = self._path_for(example)

        if old_path and old_path != new_path and old_path.exists():
            old_path.unlink()
            self._remove_empty_dirs(old_path.parent)

        new_path.parent.mkdir(parents=True, exist_ok=True)
        data = example.model_dump(mode="json")
        new_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        self._examples[example.id] = example
        self._paths[example.id] = new_path

    def delete(self, example_id: str) -> bool:
        if example_id not in self._examples:
            return False
        path = self._paths.get(example_id)
        if path and path.exists():
            path.unlink()
            self._remove_empty_dirs(path.parent)
        del self._examples[example_id]
        self._paths.pop(example_id, None)
        return True

    def _remove_empty_dirs(self, directory: Path) -> None:
        if directory == EXAMPLES_DIR:
            return
        try:
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()
                self._remove_empty_dirs(directory.parent)
        except OSError:
            pass

    def to_canvas(self, example: ArchitectureExample) -> Canvas:
        nodes = [
            NodeInstance(
                id=n.id,
                type=n.type,
                label=n.label,
                position=n.position,
                parameters=n.parameters,
            )
            for n in example.nodes
        ]

        connections: list[Connection] = []
        seen: set[str] = set()

        for node in example.nodes:
            for out_conn in node.connections.outgoing:
                conn_id = f"{node.id}->{out_conn.target}:{out_conn.source_handle}:{out_conn.target_handle}"
                if conn_id in seen:
                    continue
                seen.add(conn_id)
                connections.append(
                    Connection(
                        id=conn_id,
                        source=node.id,
                        source_handle=out_conn.source_handle,
                        target=out_conn.target,
                        target_handle=out_conn.target_handle,
                    )
                )

            for in_conn in node.connections.incoming:
                conn_id = f"{in_conn.source}->{node.id}:{in_conn.source_handle}:{in_conn.target_handle}"
                if conn_id in seen:
                    continue
                seen.add(conn_id)
                connections.append(
                    Connection(
                        id=conn_id,
                        source=in_conn.source,
                        source_handle=in_conn.source_handle,
                        target=node.id,
                        target_handle=in_conn.target_handle,
                    )
                )

        return Canvas(nodes=nodes, connections=connections)


example_registry = ExampleRegistry()
