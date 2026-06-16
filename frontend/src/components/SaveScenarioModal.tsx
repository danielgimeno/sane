import { useCallback, useEffect, useState } from 'react'

import type { ArchitectureExample, ExampleNode } from '../types'

export interface ScenarioMetadata {
  id: string
  title: string
  description: string
  category: string
}

interface SaveScenarioModalProps {
  nodes: ExampleNode[]
  initialValues?: ScenarioMetadata | null
  originalId?: string | null
  onClose: () => void
  onSaved: (example: ScenarioMetadata) => void
}

export default function SaveScenarioModal({
  nodes,
  initialValues,
  originalId,
  onClose,
  onSaved,
}: SaveScenarioModalProps) {
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [id, setId] = useState(initialValues?.id ?? '')
  const [title, setTitle] = useState(initialValues?.title ?? '')
  const [description, setDescription] = useState(initialValues?.description ?? '')
  const [category, setCategory] = useState(initialValues?.category ?? 'Personalizado')

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handler)
    return () => document.removeEventListener('keydown', handler)
  }, [onClose])

  const handleSave = useCallback(async () => {
    setError(null)

    if (!id.trim() || !title.trim() || !category.trim()) {
      setError('ID, título y categoría son obligatorios')
      return
    }

    if (nodes.length === 0) {
      setError('El lienzo está vacío')
      return
    }

    const payload: ArchitectureExample = {
      id: id.trim(),
      title: title.trim(),
      description: description.trim(),
      category: category.trim(),
      nodes,
    }

    const isUpdate = Boolean(originalId)
    const url = isUpdate ? `/api/examples/${originalId}` : '/api/examples'
    const method = isUpdate ? 'PUT' : 'POST'

    setSaving(true)
    try {
      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => null)
        throw new Error(body?.detail ?? 'Error al guardar')
      }
      onSaved({
        id: payload.id,
        title: payload.title,
        description: payload.description,
        category: payload.category,
      })
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al guardar')
    } finally {
      setSaving(false)
    }
  }, [id, title, description, category, nodes, originalId, onSaved, onClose])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal example-editor-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="save-scenario-title"
      >
        <div className="modal-header">
          <h2 id="save-scenario-title">Guardar escenario</h2>
          <button type="button" className="modal-close" onClick={onClose} aria-label="Cerrar">
            ×
          </button>
        </div>

        <div className="modal-body">
          {error && <p className="example-editor-error">{error}</p>}

          <p className="save-scenario-hint">
            Se guardarán {nodes.length} nodo{nodes.length === 1 ? '' : 's'} del lienzo actual.
          </p>

          <div className="example-editor-grid">
            <div className="param-field">
              <label htmlFor="sc-id">ID</label>
              <input
                id="sc-id"
                value={id}
                onChange={(e) => setId(e.target.value)}
                placeholder="mi-escenario"
                spellCheck={false}
              />
            </div>
            <div className="param-field">
              <label htmlFor="sc-category">Categoría</label>
              <input
                id="sc-category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
              />
            </div>
          </div>

          <div className="param-field">
            <label htmlFor="sc-title">Título</label>
            <input
              id="sc-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Mi arquitectura"
            />
          </div>

          <div className="param-field">
            <label htmlFor="sc-description">Descripción</label>
            <textarea
              id="sc-description"
              className="example-editor-textarea"
              rows={2}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Breve descripción del escenario"
            />
          </div>
        </div>

        <div className="modal-footer">
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
      </div>
    </div>
  )
}
