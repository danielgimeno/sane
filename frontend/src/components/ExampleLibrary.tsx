import { useState, useMemo } from 'react'

import type { ExampleSummary } from '../types'

interface ExampleLibraryProps {
  examples: Record<string, ExampleSummary[]>
  loading: boolean
  onLoad: (exampleId: string) => void
  onEdit: (exampleId: string) => void
}

export default function ExampleLibrary({ examples, loading, onLoad, onEdit }: ExampleLibraryProps) {
  const [search, setSearch] = useState('')

  const filtered = useMemo(() => {
    if (!search.trim()) return examples
    const q = search.toLowerCase()
    const result: Record<string, ExampleSummary[]> = {}
    for (const [cat, items] of Object.entries(examples)) {
      const matched = items.filter(
        (ex) =>
          ex.title.toLowerCase().includes(q) ||
          ex.description.toLowerCase().includes(q) ||
          ex.category.toLowerCase().includes(q),
      )
      if (matched.length) result[cat] = matched
    }
    return result
  }, [examples, search])

  const total = Object.values(examples).flat().length

  return (
    <div className="example-library">
      <input
        className="palette-search"
        placeholder="Buscar ejemplos..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {loading && total === 0 && (
        <p className="example-library-empty">Cargando ejemplos…</p>
      )}
      {!loading && total === 0 && (
        <p className="example-library-empty">No hay ejemplos disponibles</p>
      )}
      {Object.entries(filtered).map(([category, items]) => (
        <div key={category} className="palette-category">
          <div className="palette-category-title">{category}</div>
          {items.map((ex) => (
            <div key={ex.id} className="example-item-row">
              <button
                type="button"
                className="example-item"
                onClick={() => onLoad(ex.id)}
                title={ex.description}
              >
                <span className="example-item-icon">📐</span>
                <span className="example-item-body">
                  <span className="example-item-title">{ex.title}</span>
                  <span className="example-item-meta">{ex.node_count} nodos</span>
                </span>
              </button>
              <button
                type="button"
                className="example-item-edit"
                onClick={() => onEdit(ex.id)}
                title="Editar ejemplo"
                aria-label={`Editar ${ex.title}`}
              >
                ✏️
              </button>
            </div>
          ))}
        </div>
      ))}
    </div>
  )
}
