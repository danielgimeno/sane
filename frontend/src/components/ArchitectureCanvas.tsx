import { useCallback, useRef, useState, useEffect } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  type Connection,
  type Edge,
  type Node,
  type ReactFlowInstance,
  BackgroundVariant,
  MarkerType,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'

import ArchNode from './ArchNode'
import ContextMenu from './ContextMenu'
import EdgeTooltip from './EdgeTooltip'
import type { ArchitectureExample, ElementDefinition, ArchNodeData, SimulationMetrics } from '../types'
import { exampleToFlow } from '../utils/exampleToFlow'

const nodeTypes = { archNode: ArchNode }

let nodeIdCounter = 0
function nextNodeId() {
  return `node_${++nodeIdCounter}`
}

interface ArchitectureCanvasProps {
  catalogFlat: ElementDefinition[]
  simMetrics: SimulationMetrics | null
  running: boolean
  loadExampleId: string | null
  diagramTitle?: string | null
  onExampleLoaded: (example?: ArchitectureExample) => void
  onClear?: () => void
  onSaveScenario?: () => void
  onNodesChange: (nodes: Node[]) => void
  onEdgesChange: (edges: Edge[]) => void
}

export default function ArchitectureCanvas({
  catalogFlat,
  simMetrics,
  running,
  loadExampleId,
  diagramTitle,
  onExampleLoaded,
  onClear,
  onSaveScenario,
  onNodesChange,
  onEdgesChange,
}: ArchitectureCanvasProps) {
  const reactFlowWrapper = useRef<HTMLDivElement>(null)
  const [reactFlowInstance, setReactFlowInstance] = useState<ReactFlowInstance | null>(null)
  const [nodes, setNodes, onNodesChangeInternal] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChangeInternal] = useEdgesState<Edge>([])

  const [contextMenu, setContextMenu] = useState<{
    x: number
    y: number
    nodeId: string
    element: ElementDefinition
    parameters: Record<string, unknown>
  } | null>(null)

  const [edgeMenu, setEdgeMenu] = useState<{
    x: number
    y: number
    edgeId: string
    label: string
  } | null>(null)

  useEffect(() => {
    onNodesChange(nodes)
  }, [nodes, onNodesChange])

  useEffect(() => {
    onEdgesChange(edges)
  }, [edges, onEdgesChange])

  useEffect(() => {
    if (!simMetrics) return
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: {
          ...n.data,
          metrics: simMetrics.nodes[n.id] ?? undefined,
        },
      })),
    )
  }, [simMetrics, setNodes])

  useEffect(() => {
    if (!loadExampleId || catalogFlat.length === 0) return

    let cancelled = false
    fetch(`/api/examples/${loadExampleId}`)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((example) => {
        if (cancelled) return
        const { nodes: newNodes, edges: newEdges } = exampleToFlow(example, catalogFlat)
        setNodes(newNodes)
        setEdges(newEdges)
        onExampleLoaded(example)
        setTimeout(() => reactFlowInstance?.fitView({ padding: 0.2 }), 50)
      })
      .catch(() => {
        if (!cancelled) onExampleLoaded()
      })

    return () => {
      cancelled = true
    }
  }, [loadExampleId, catalogFlat, setNodes, setEdges, onExampleLoaded, reactFlowInstance])

  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault()
    event.dataTransfer.dropEffect = 'move'
  }, [])

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault()
      const type = event.dataTransfer.getData('application/sae-element')
      if (!type || !reactFlowInstance || !reactFlowWrapper.current) return

      const element = catalogFlat.find((el) => el.type === type)
      if (!element) return

      const bounds = reactFlowWrapper.current.getBoundingClientRect()
      const position = reactFlowInstance.screenToFlowPosition({
        x: event.clientX - bounds.left,
        y: event.clientY - bounds.top,
      })

      const defaultParams: Record<string, unknown> = {}
      element.parameters.forEach((p) => {
        defaultParams[p.key] = p.default
      })

      const newNode: Node = {
        id: nextNodeId(),
        type: 'archNode',
        position,
        data: {
          label: element.label,
          elementType: element.type,
          icon: element.icon,
          color: element.color,
          parameters: defaultParams,
          definition: element,
        } satisfies ArchNodeData,
      }

      setNodes((nds) => [...nds, newNode])
    },
    [reactFlowInstance, catalogFlat, setNodes],
  )

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) =>
        addEdge(
          {
            ...connection,
            type: 'smoothstep',
            markerEnd: { type: MarkerType.ArrowClosed, width: 16, height: 16 },
            style: { stroke: '#6366f1' },
            interactionWidth: 20,
          },
          eds,
        ),
      )
    },
    [setEdges],
  )

  const onEdgeClick = useCallback(
    (event: React.MouseEvent, edge: Edge) => {
      setContextMenu(null)

      const sourceNode = nodes.find((n) => n.id === edge.source)
      const targetNode = nodes.find((n) => n.id === edge.target)
      const sourceLabel = (sourceNode?.data as ArchNodeData)?.label ?? edge.source
      const targetLabel = (targetNode?.data as ArchNodeData)?.label ?? edge.target

      setEdgeMenu({
        x: event.clientX,
        y: event.clientY,
        edgeId: edge.id,
        label: `${sourceLabel} → ${targetLabel}`,
      })
    },
    [nodes],
  )

  const onPaneClick = useCallback(() => {
    setEdgeMenu(null)
  }, [])

  const handleEdgeDelete = useCallback(() => {
    if (!edgeMenu) return
    setEdges((eds) => eds.filter((e) => e.id !== edgeMenu.edgeId))
    setEdgeMenu(null)
  }, [edgeMenu, setEdges])

  const onNodeContextMenu = useCallback(
    (event: React.MouseEvent, node: Node) => {
      event.preventDefault()
      setEdgeMenu(null)
      const data = node.data as ArchNodeData
      const element = catalogFlat.find((el) => el.type === data.elementType)
      if (!element) return

      setContextMenu({
        x: event.clientX,
        y: event.clientY,
        nodeId: node.id,
        element,
        parameters: { ...data.parameters },
      })
    },
    [catalogFlat],
  )

  const handleContextSave = useCallback(
    (params: Record<string, unknown>) => {
      if (!contextMenu) return
      setNodes((nds) =>
        nds.map((n) =>
          n.id === contextMenu.nodeId
            ? { ...n, data: { ...n.data, parameters: params } }
            : n,
        ),
      )
    },
    [contextMenu, setNodes],
  )

  const handleContextDelete = useCallback(() => {
    if (!contextMenu) return
    setNodes((nds) => nds.filter((n) => n.id !== contextMenu.nodeId))
    setEdges((eds) =>
      eds.filter((e) => e.source !== contextMenu.nodeId && e.target !== contextMenu.nodeId),
    )
    setContextMenu(null)
  }, [contextMenu, setNodes, setEdges])

  const handleClear = useCallback(() => {
    if (running) return
    setNodes([])
    setEdges([])
    setContextMenu(null)
    setEdgeMenu(null)
    onClear?.()
  }, [running, setNodes, setEdges, onClear])

  const hasContent = nodes.length > 0 || edges.length > 0

  return (
    <div
      className={`canvas-area${running ? ' canvas-area--simulating' : ''}`}
      ref={reactFlowWrapper}
    >
      {nodes.length === 0 && (
        <div className="empty-state">
          <div className="empty-state-icon">🏗️</div>
          <p>Arrastra componentes al lienzo</p>
          <small>Conecta salidas con entradas para definir el flujo</small>
        </div>
      )}
      {diagramTitle && (
        <div className="canvas-diagram-title" title={diagramTitle}>
          {diagramTitle}
        </div>
      )}
      {hasContent && (
        <div className="canvas-toolbar">
          <button
            type="button"
            className="btn btn-primary"
            onClick={onSaveScenario}
            disabled={running || !onSaveScenario}
            title={running ? 'Detén la simulación para guardar' : 'Guardar el lienzo como escenario'}
          >
            Guardar escenario
          </button>
          <button
            type="button"
            className="btn btn-ghost"
            onClick={handleClear}
            disabled={running}
            title={running ? 'Detén la simulación para limpiar' : 'Vaciar el lienzo'}
          >
            Limpiar
          </button>
        </div>
      )}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChangeInternal}
        onEdgesChange={onEdgesChangeInternal}
        onConnect={onConnect}
        onInit={setReactFlowInstance}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onNodeContextMenu={onNodeContextMenu}
        onEdgeClick={onEdgeClick}
        onPaneClick={onPaneClick}
        nodeTypes={nodeTypes}
        fitView
        deleteKeyCode={['Backspace', 'Delete']}
        defaultEdgeOptions={{
          type: 'smoothstep',
          markerEnd: { type: MarkerType.ArrowClosed },
          interactionWidth: 20,
        }}
      >
        <Background variant={BackgroundVariant.Dots} gap={24} size={1} color="#2d3748" />
        <Controls />
        <MiniMap
          nodeColor={(n) => (n.data as ArchNodeData).color ?? '#6366f1'}
          maskColor="rgba(15, 17, 23, 0.8)"
        />
      </ReactFlow>

      {contextMenu && (
        <ContextMenu
          x={contextMenu.x}
          y={contextMenu.y}
          element={contextMenu.element}
          parameters={contextMenu.parameters}
          onSave={handleContextSave}
          onDelete={handleContextDelete}
          onClose={() => setContextMenu(null)}
        />
      )}

      {edgeMenu && (
        <EdgeTooltip
          x={edgeMenu.x}
          y={edgeMenu.y}
          label={edgeMenu.label}
          onDelete={handleEdgeDelete}
          onClose={() => setEdgeMenu(null)}
        />
      )}
    </div>
  )
}
