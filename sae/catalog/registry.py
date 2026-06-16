from sae.catalog.definitions import ALL_ELEMENTS
from sae.models.elements import ElementDefinition


class ElementRegistry:
    def __init__(self) -> None:
        self._elements: dict[str, ElementDefinition] = {
            el.type: el for el in ALL_ELEMENTS
        }

    def list_all(self) -> list[ElementDefinition]:
        return list(self._elements.values())

    def list_by_category(self) -> dict[str, list[ElementDefinition]]:
        grouped: dict[str, list[ElementDefinition]] = {}
        for el in self._elements.values():
            grouped.setdefault(el.category, []).append(el)
        return grouped

    def get(self, element_type: str) -> ElementDefinition | None:
        return self._elements.get(element_type)

    def default_parameters(self, element_type: str) -> dict:
        el = self.get(element_type)
        if not el:
            return {}
        return {p.key: p.default for p in el.parameters}


registry = ElementRegistry()
