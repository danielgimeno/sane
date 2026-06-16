import { memo } from 'react'
import { Handle, Position, type NodeProps } from '@xyflow/react'
import type { ArchNodeData } from '../types'

function ArchNode({ data, selected }: NodeProps) {
  const d = data as ArchNodeData
  const metrics = d.metrics
  const loadPercent = metrics ? Math.round(metrics.current_load * 100) : 0

  return (
    <div
      className={`arch-node ${selected ? 'selected' : ''} ${metrics && metrics.requests_received > 0 ? 'simulating' : ''}`}
      style={{ borderTopColor: d.color, borderTopWidth: 3 }}
    >
      {d.definition?.inputs.map((port, i) => (
        <Handle
          key={port.id}
          type="target"
          position={Position.Left}
          id={port.id}
          style={{
            top: `${((i + 1) / (d.definition!.inputs.length + 1)) * 100}%`,
            background: d.color,
          }}
          title={port.label}
        />
      ))}

      <div className="arch-node-header">
        <span className="arch-node-icon">{d.icon}</span>
        <div>
          <div className="arch-node-title">{d.label}</div>
          <div className="arch-node-type">{d.elementType}</div>
        </div>
      </div>

      {metrics && metrics.requests_received > 0 && (
        <div className="arch-node-body">
          <div className="arch-node-metrics">
            <span className="arch-node-metric">↓ {metrics.requests_received}</span>
            <span className="arch-node-metric">✓ {metrics.requests_processed}</span>
            {metrics.requests_failed > 0 && (
              <span className="arch-node-metric" style={{ color: 'var(--danger)' }}>
                ✗ {metrics.requests_failed}
              </span>
            )}
            {metrics.avg_latency_ms > 0 && (
              <span className="arch-node-metric">{metrics.avg_latency_ms.toFixed(1)}ms</span>
            )}
          </div>
          {loadPercent > 0 && (
            <div className="load-bar">
              <div
                className="load-bar-fill"
                style={{
                  width: `${Math.min(loadPercent, 100)}%`,
                  background: loadPercent > 80 ? 'var(--danger)' : loadPercent > 50 ? 'var(--warning)' : 'var(--success)',
                }}
              />
            </div>
          )}
        </div>
      )}

      {d.definition?.outputs.map((port, i) => (
        <Handle
          key={port.id}
          type="source"
          position={Position.Right}
          id={port.id}
          style={{
            top: `${((i + 1) / (d.definition!.outputs.length + 1)) * 100}%`,
            background: d.color,
          }}
          title={port.label}
        />
      ))}
    </div>
  )
}

export default memo(ArchNode)
