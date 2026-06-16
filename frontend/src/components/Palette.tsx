import { useState, useMemo } from 'react'
import type { Catalog, ElementDefinition } from '../types'

interface PaletteProps {
  catalog: Catalog
  onDragStart: (event: React.DragEvent, element: ElementDefinition) => void
}

export default function Palette({ catalog, onDragStart }: PaletteProps) {
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!search.trim()) return catalog
    const q = search.toLowerCase()
    const result: Catalog = {}
    for (const [cat, items] of Object.entries(catalog)) {
      const matched = items.filter(
        (el) =>
          el.label.toLowerCase().includes(q) ||
          el.type.toLowerCase().includes(q) ||
          el.description.toLowerCase().includes(q),
      )
      if (matched.length) result[cat] = matched
    }
    return result
  }, [catalog, search])

  return (
    <>
      <input
        className="palette-search"
        placeholder="Buscar componentes..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {Object.entries(filtered).map(([category, items]) => (
        <div key={category} className="palette-category">
          <div className="palette-category-title">{category}</div>
          {items.map((el) => (
            <div
              key={el.type}
              className="palette-item"
              draggable
              onDragStart={(e) => onDragStart(e, el)}
              title={el.description}
            >
              <span className="palette-item-icon">{el.icon}</span>
              <span className="palette-item-label">{el.label}</span>
            </div>
          ))}
        </div>
      ))}
    </>
  )
}
