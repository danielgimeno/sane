import { useState, useEffect, useCallback } from 'react'
import type { ElementDefinition, ParameterDef } from '../types'

interface ContextMenuProps {
  x: number
  y: number
  element: ElementDefinition
  parameters: Record<string, unknown>
  onSave: (params: Record<string, unknown>) => void
  onDelete: () => void
  onClose: () => void
}

function ParamField({
  param,
  value,
  onChange,
}: {
  param: ParameterDef
  value: unknown
  onChange: (key: string, val: unknown) => void
}) {
  const id = `param-${param.key}`

  if (param.type === 'select') {
    return (
      <div className="param-field">
        <label htmlFor={id}>{param.label}</label>
        <select
          id={id}
          value={String(value ?? param.default ?? '')}
          onChange={(e) => onChange(param.key, e.target.value)}
        >
          {param.options?.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>
      </div>
    )
  }

  if (param.type === 'boolean') {
    return (
      <div className="param-field">
        <label>
          <input
            type="checkbox"
            checked={Boolean(value ?? param.default)}
            onChange={(e) => onChange(param.key, e.target.checked)}
          />{' '}
          {param.label}
        </label>
      </div>
    )
  }

  return (
    <div className="param-field">
      <label htmlFor={id}>
        {param.label}
        {param.unit && <span className="param-unit">({param.unit})</span>}
      </label>
      <input
        id={id}
        type={param.type === 'integer' ? 'number' : 'number'}
        step={param.step ?? (param.type === 'integer' ? 1 : 0.1)}
        min={param.min}
        max={param.max}
        value={Number(value ?? param.default ?? 0)}
        onChange={(e) => {
          const v = param.type === 'integer' ? parseInt(e.target.value, 10) : parseFloat(e.target.value)
          onChange(param.key, v)
        }}
      />
    </div>
  )
}

export default function ContextMenu({
  x,
  y,
  element,
  parameters,
  onSave,
  onDelete,
  onClose,
}: ContextMenuProps) {
  const [localParams, setLocalParams] = useState(parameters)

  useEffect(() => {
    setLocalParams(parameters)
  }, [parameters])

  const handleChange = useCallback((key: string, val: unknown) => {
    setLocalParams((prev) => ({ ...prev, [key]: val }))
  }, [])

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('.context-menu')) onClose()
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [onClose])

  return (
    <div
      className="context-menu"
      style={{ left: x, top: y }}
      onContextMenu={(e) => e.preventDefault()}
    >
      <div className="context-menu-header">
        <span className="context-menu-header-icon">{element.icon}</span>
        <div className="context-menu-header-info">
          <h3>{element.label}</h3>
          <p>{element.description}</p>
        </div>
      </div>
      <div className="context-menu-body">
        {element.parameters.map((param) => (
          <ParamField
            key={param.key}
            param={param}
            value={localParams[param.key]}
            onChange={handleChange}
          />
        ))}
      </div>
      <div className="context-menu-footer">
        <button className="btn btn-ghost" onClick={onDelete}>
          Eliminar
        </button>
        <button
          className="btn btn-primary"
          onClick={() => {
            onSave(localParams)
            onClose()
          }}
        >
          Aplicar
        </button>
      </div>
    </div>
  )
}
