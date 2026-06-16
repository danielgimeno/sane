import { useEffect } from 'react'

interface EdgeTooltipProps {
  x: number
  y: number
  label: string
  onDelete: () => void
  onClose: () => void
}

export default function EdgeTooltip({ x, y, label, onDelete, onClose }: EdgeTooltipProps) {
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      const target = e.target as HTMLElement
      if (!target.closest('.edge-tooltip')) onClose()
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [onClose])

  return (
    <div className="edge-tooltip" style={{ left: x, top: y }}>
      <span className="edge-tooltip-label">{label}</span>
      <button
        className="btn btn-danger edge-tooltip-delete"
        onClick={() => {
          onDelete()
          onClose()
        }}
      >
        Eliminar conexión
      </button>
    </div>
  )
}
