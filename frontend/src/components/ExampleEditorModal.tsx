import { useCallback, useEffect, useState } from 'react'
import type { ArchitectureExample, ExampleNode } from '../types'

interface ExampleEditorModalProps {
  exampleId: string
  onClose: () => void
  onSaved: () => void
  onDeleted: () => void
}

export default function ExampleEditorModal({
  exampleId,
  onClose,
  onSaved,
  onDeleted,
}: ExampleEditorModalProps) {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [originalId, setOriginalId] = useState(exampleId)
  const [id, setId] = useState('')
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [category, setCategory] = useState('')
  const [nodesJson, setNodesJson] = useState('')

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetch(`/api/examples/${exampleId}`)
      .then((r) => {
        if (!r.ok) throw new Error('No se pudo cargar el ejemplo')
        return r.json() as Promise<ArchitectureExample>
      })
      .then((example) => {
        if (cancelled) return
        setOriginalId(example.id)
        setId(example.id)
        setTitle(example.title)
        setDescription(example.description)
        setCategory(example.category)
        setNodesJson(JSON.stringify(example.nodes, null, 2))
        setLoading(false)
      })
      .catch((err: Error) => {
        if (cancelled) return
        setError(err.message)
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [exampleId])

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  const handleSave = useCallback(async () => {
    setError(null)

    let nodes: ExampleNode[]
    try {
      nodes = JSON.parse(nodesJson)
      if (!Array.isArray(nodes)) throw new Error('Los nodos deben ser un array')
    } catch {
      setError('JSON de nodos inválido')
      return
    }

    if (!id.trim() || !title.trim() || !category.trim()) {
      setError('ID, título y categoría son obligatorios')
      return
    }

    const payload: ArchitectureExample = {
      id: id.trim(),
      title: title.trim(),
      description: description.trim(),
      category: category.trim(),
      nodes,
    }

    setSaving(true)
    try {
      const res = await fetch(`/api/examples/${originalId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => null)
        throw new Error(body?.detail ?? 'Error al guardar')
      }
      onSaved()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setSaving(false)
    }
  }, [id, title, description, category, nodesJson, originalId, onSaved, onClose])

  const handleDelete = useCallback(async () => {
    if (!window.confirm(`¿Eliminar el ejemplo "${title || originalId}"?`)) return

    setSaving(true)
    setError(null)
    try {
      const res = await fetch(`/api/examples/${originalId}`, { method: 'DELETE' })
      if (!res.ok) throw new Error('Error al eliminar')
      onDeleted()
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al eliminar')
    } finally {
      setSaving(false)
    }
  }, [originalId, title, onDeleted, onClose])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal example-editor-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="example-editor-title"
      >
        <div className="modal-header">
          <h2 id="example-editor-title">Editar ejemplo</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
            ×
          </button>
        </div>

        {loading ? (
          <div className="modal-body">
            <p className="example-editor-loading">Cargando…</p>
          </div>
        ) : (
          <>
            <div className="modal-body">
              {error && <p className="example-editor-error">{error}</p>}

              <div className="example-editor-grid">
                <div className="param-field">
                  <label htmlFor="ex-id">ID</label>
                  <input
                    id="ex-id"
                    value={id}
                    onChange={(e) => setId(e.target.value)}
                    spellCheck={false}
                  />
                </div>
                <div className="param-field">
                  <label htmlFor="ex-category">Categoría</label>
                  <input
                    id="ex-category"
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                  />
                </div>
              </div>

              <div className="param-field">
                <label htmlFor="ex-title">Título</label>
                <input
                  id="ex-title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div className="param-field">
                <label htmlFor="ex-description">Descripción</label>
                <textarea
                  id="ex-description"
                  className="example-editor-textarea"
                  rows={2}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div className="param-field">
                <label htmlFor="ex-nodes">Nodos (JSON)</label>
                <textarea
                  id="ex-nodes"
                  className="example-editor-textarea example-editor-nodes"
                  value={nodesJson}
                  onChange={(e) => setNodesJson(e.target.value)}
                  spellCheck={false}
                />
              </div>
            </div>

            <div className="modal-footer">
              <button
                type="button"
                className="btn btn-danger"
                onClick={handleDelete}
                disabled={saving}
              >
                Eliminar
              </button>
              <div className="modal-footer-spacer" />
              <button type="button" className="btn btn-ghost" onClick={onClose} disabled={saving}>
                Cancelar
              </button>
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? 'Guardando…' : 'Guardar'}
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
