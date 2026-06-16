import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import type { Node, Edge } from '@xyflow/react'

import ArchitectureCanvas from './components/ArchitectureCanvas'
import ExampleEditorModal from './components/ExampleEditorModal'
import SaveScenarioModal, { type ScenarioMetadata } from './components/SaveScenarioModal'
import Sidebar from './components/Sidebar'
import SimulationPanel from './components/SimulationPanel'
import type { Catalog, ElementDefinition, ExampleSummary, SimulationMetrics } from './types'
import { flowToExampleNodes } from './utils/flowToExample'

export default function App() {
  const [catalog, setCatalog] = useState<Catalog>({})
  const [catalogError, setCatalogError] = useState(false)
  const [catalogLoading, setCatalogLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [duration, setDuration] = useState(30)
  const [speed, setSpeed] = useState(1)
  const [metrics, setMetrics] = useState<SimulationMetrics | null>(null)
  const [examples, setExamples] = useState<Record<string, ExampleSummary[]>>({})
  const [examplesLoading, setExamplesLoading] = useState(true)
  const [loadExampleId, setLoadExampleId] = useState<string | null>(null)
  const [editExampleId, setEditExampleId] = useState<string | null>(null)
  const [saveScenarioOpen, setSaveScenarioOpen] = useState(false)
  const [activeScenario, setActiveScenario] = useState<ScenarioMetadata | null>(null)

  const refreshExamples = useCallback(() => {
    fetch('/api/examples')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((data) => {
        setExamples(data)
        setExamplesLoading(false)
      })
      .catch(() => {
        setExamplesLoading(false)
      })
  }, [])

  const nodesRef = useRef<Node[]>([])
  const edgesRef = useRef<Edge[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    let cancelled = false
    let attempt = 0

    const loadCatalog = () => {
      fetch('/api/catalog')
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`)
          return r.json()
        })
        .then((data) => {
          if (cancelled) return
          setCatalog(data)
          setCatalogError(false)
          setCatalogLoading(false)
        })
        .catch(() => {
          if (cancelled) return
          setCatalogError(true)
          setCatalogLoading(false)
          attempt += 1
          const delay = Math.min(1000 * attempt, 5000)
          setTimeout(loadCatalog, delay)
        })
    }

    loadCatalog()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    refreshExamples()
  }, [refreshExamples])

  const catalogFlat = useMemo(
    () => Object.values(catalog).flat(),
    [catalog],
  )

  const onDragStart = useCallback(
    (event: React.DragEvent, element: ElementDefinition) => {
      event.dataTransfer.setData('application/sae-element', element.type)
      event.dataTransfer.effectAllowed = 'move'
    },
    [],
  )

  const buildCanvasPayload = useCallback(() => {
    return {
      nodes: nodesRef.current.map((n) => {
        const d = n.data as {
          label: string
          elementType: string
          parameters: Record<string, unknown>
        }
        return {
          id: n.id,
          type: d.elementType,
          label: d.label,
          position: { x: n.position.x, y: n.position.y },
          parameters: d.parameters,
        }
      }),
      connections: edgesRef.current.map((e) => ({
        id: e.id,
        source: e.source,
        source_handle: e.sourceHandle ?? 'out',
        target: e.target,
        target_handle: e.targetHandle ?? 'in',
      })),
    }
  }, [])

  const handleStart = useCallback(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = import.meta.env.DEV ? 'localhost:8000' : window.location.host
    const ws = new WebSocket(`${wsProtocol}//${wsHost}/ws/simulation`)
    wsRef.current = ws

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          action: 'start',
          canvas: buildCanvasPayload(),
          duration,
          speed,
        }),
      )
      setRunning(true)
      setMetrics(null)
    }

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data)
      if (msg.type === 'metrics' || msg.type === 'finished') {
        setMetrics(msg.data)
      }
      if (msg.type === 'finished' || msg.type === 'stopped') {
        setRunning(false)
      }
    }

    ws.onerror = () => {
      setRunning(false)
    }

    ws.onclose = () => {
      setRunning(false)
    }
  }, [buildCanvasPayload, duration, speed])

  const handleStop = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: 'stop' }))
    }
    wsRef.current?.close()
    setRunning(false)
  }, [])

  const handleClearCanvas = useCallback(() => {
    setMetrics(null)
    setActiveScenario(null)
  }, [])

  const handleSaveScenario = useCallback(() => {
    if (nodesRef.current.length === 0) return
    setSaveScenarioOpen(true)
  }, [])

  const scenarioNodes = useMemo(
    () => flowToExampleNodes(nodesRef.current, edgesRef.current),
    // Recalcular al abrir el modal
    [saveScenarioOpen],
  )

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>
          <span>SANE</span> [Software Architect Node Emulator]
        </h1>
        <div className="header-actions">
          <span className={`status-badge ${running ? 'running' : 'stopped'}`}>
            <span className="status-dot" />
            {running ? 'Simulando' : 'Detenido'}
          </span>
        </div>
      </header>

      <Sidebar
        catalog={catalog}
        examples={examples}
        examplesLoading={examplesLoading}
        onDragStart={onDragStart}
        onLoadExample={setLoadExampleId}
        onEditExample={setEditExampleId}
      />

      {catalogError && (
        <div className="backend-banner">
          Esperando al backend en <code>localhost:8000</code>…
          <br />
          <small>Ejecuta <code>poetry run sae</code> en otra terminal</small>
        </div>
      )}

      {catalogLoading && Object.keys(catalog).length === 0 && !catalogError && (
        <div className="backend-banner">Cargando catálogo…</div>
      )}

      <ArchitectureCanvas
        catalogFlat={catalogFlat}
        simMetrics={metrics}
        running={running}
        loadExampleId={loadExampleId}
        onExampleLoaded={(example) => {
          setLoadExampleId(null)
          if (example) {
            setActiveScenario({
              id: example.id,
              title: example.title,
              description: example.description,
              category: example.category,
            })
          }
        }}
        onClear={handleClearCanvas}
        onSaveScenario={handleSaveScenario}
        onNodesChange={(nodes) => {
          nodesRef.current = nodes
        }}
        onEdgesChange={(edges) => {
          edgesRef.current = edges
        }}
      />

      <SimulationPanel
        running={running}
        duration={duration}
        speed={speed}
        metrics={metrics}
        nodes={nodesRef.current}
        onDurationChange={setDuration}
        onSpeedChange={setSpeed}
        onStart={handleStart}
        onStop={handleStop}
      />

      {editExampleId && (
        <ExampleEditorModal
          exampleId={editExampleId}
          onClose={() => setEditExampleId(null)}
          onSaved={refreshExamples}
          onDeleted={refreshExamples}
        />
      )}

      {saveScenarioOpen && (
        <SaveScenarioModal
          nodes={scenarioNodes}
          initialValues={activeScenario}
          originalId={activeScenario?.id ?? null}
          onClose={() => setSaveScenarioOpen(false)}
          onSaved={(saved) => {
            setActiveScenario(saved)
            refreshExamples()
          }}
        />
      )}
    </div>
  )
}
