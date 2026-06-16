import type { SimulationMetrics } from '../types'
import type { Node } from '@xyflow/react'

interface SimulationPanelProps {
  running: boolean
  duration: number
  speed: number
  metrics: SimulationMetrics | null
  nodes: Node[]
  onDurationChange: (v: number) => void
  onSpeedChange: (v: number) => void
  onStart: () => void
  onStop: () => void
}

export default function SimulationPanel({
  running,
  duration,
  speed,
  metrics,
  nodes,
  onDurationChange,
  onSpeedChange,
  onStart,
  onStop,
}: SimulationPanelProps) {
  const nodeName = (id: string) => {
    const node = nodes.find((n) => n.id === id)
    return node ? String((node.data as { label?: string }).label ?? id) : id.slice(0, 8)
  }

  return (
    <aside className="sim-panel">
      <h2>Simulación</h2>

      <div className="sim-controls">
        <div className="sim-control-row">
          <label>Duración (segundos): {duration}</label>
          <input
            type="range"
            min={5}
            max={120}
            step={5}
            value={duration}
            disabled={running}
            onChange={(e) => onDurationChange(Number(e.target.value))}
          />
        </div>
        <div className="sim-control-row">
          <label>Velocidad: {speed}x</label>
          <input
            type="range"
            min={0.5}
            max={10}
            step={0.5}
            value={speed}
            disabled={running}
            onChange={(e) => onSpeedChange(Number(e.target.value))}
          />
        </div>
        <div className="sim-buttons">
          {!running ? (
            <button className="btn btn-primary" onClick={onStart}>
              ▶ Play
            </button>
          ) : (
            <button className="btn btn-danger" onClick={onStop}>
              ■ Stop
            </button>
          )}
        </div>
      </div>

      {metrics && (
        <>
          <h2>Métricas globales</h2>
          <div className="metrics-summary">
            <div className="metric-card">
              <div className="metric-card-value">{metrics.elapsed_seconds.toFixed(1)}s</div>
              <div className="metric-card-label">Tiempo</div>
            </div>
            <div className="metric-card">
              <div className="metric-card-value">{metrics.total_requests}</div>
              <div className="metric-card-label">Peticiones</div>
            </div>
            <div className="metric-card">
              <div className="metric-card-value">{metrics.completed_requests}</div>
              <div className="metric-card-label">Completadas</div>
            </div>
            <div className="metric-card">
              <div className="metric-card-value" style={{ color: metrics.failed_requests > 0 ? 'var(--danger)' : undefined }}>
                {metrics.failed_requests}
              </div>
              <div className="metric-card-label">Fallidas</div>
            </div>
          </div>

          {Object.keys(metrics.nodes).length > 0 && (
            <>
              <h2>Por nodo</h2>
              <div className="node-metrics-list">
                {Object.entries(metrics.nodes)
                  .filter(([, m]) => m.requests_received > 0)
                  .map(([id, m]) => (
                    <div key={id} className="node-metric-item">
                      <div className="node-metric-item-header">
                        {nodeName(id)}
                      </div>
                      <div className="node-metric-row">
                        <span>Recibidas</span>
                        <span>{m.requests_received}</span>
                      </div>
                      <div className="node-metric-row">
                        <span>Procesadas</span>
                        <span>{m.requests_processed}</span>
                      </div>
                      {m.avg_latency_ms > 0 && (
                        <div className="node-metric-row">
                          <span>Latencia media</span>
                          <span>{m.avg_latency_ms.toFixed(1)} ms</span>
                        </div>
                      )}
                      {m.queue_depth > 0 && (
                        <div className="node-metric-row">
                          <span>Cola</span>
                          <span>{m.queue_depth}</span>
                        </div>
                      )}
                      {m.extra?.distribution ? (
                        <div className="distribution-bar">
                          {Object.entries(m.extra.distribution as Record<string, number>).map(
                            ([target, count]) => {
                              const total = Object.values(m.extra!.distribution as Record<string, number>).reduce(
                                (a, b) => a + b,
                                0,
                              )
                              const pct = total > 0 ? (count / total) * 100 : 0
                              return (
                                <div key={target} className="distribution-item">
                                  <span style={{ minWidth: 80 }}>{nodeName(target)}</span>
                                  <div style={{ flex: 1, background: 'var(--bg-primary)', borderRadius: 3, height: 6 }}>
                                    <div
                                      className="distribution-bar-fill"
                                      style={{ width: `${pct}%` }}
                                    />
                                  </div>
                                  <span>{count} ({pct.toFixed(0)}%)</span>
                                </div>
                              )
                            },
                          )}
                        </div>
                      ) : null}
                    </div>
                  ))}
              </div>
            </>
          )}
        </>
      )}
    </aside>
  )
}
