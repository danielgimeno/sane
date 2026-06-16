import type { MarkerType } from '@xyflow/react'
import type { Edge, Node } from '@xyflow/react'

import type { ArchitectureExample, ElementDefinition, ArchNodeData } from '../types'

export function exampleToFlow(
  example: ArchitectureExample,
  catalogFlat: ElementDefinition[],
): { nodes: Node[]; edges: Edge[] } {
  const nodes: Node[] = []
  const edges: Edge[] = []
  const seenEdges = new Set<string>()

  for (const nodeDef of example.nodes) {
    const element = catalogFlat.find((el) => el.type === nodeDef.type)
    if (!element) continue

    const defaultParams: Record<string, unknown> = {}
    element.parameters.forEach((p) => {
      defaultParams[p.key] = p.default
    })

    nodes.push({
      id: nodeDef.id,
      type: 'archNode',
      position: nodeDef.position,
      data: {
        label: nodeDef.label,
        elementType: nodeDef.type,
        icon: element.icon,
        color: element.color,
        parameters: { ...defaultParams, ...nodeDef.parameters },
        definition: element,
      } satisfies ArchNodeData,
    })

    for (const outConn of nodeDef.connections.outgoing) {
      const edgeId = `${nodeDef.id}->${outConn.target}:${outConn.source_handle}:${outConn.target_handle}`
      if (seenEdges.has(edgeId)) continue
      seenEdges.add(edgeId)
      edges.push(makeEdge(edgeId, nodeDef.id, outConn.target, outConn.source_handle, outConn.target_handle))
    }

    for (const inConn of nodeDef.connections.incoming) {
      const edgeId = `${inConn.source}->${nodeDef.id}:${inConn.source_handle}:${inConn.target_handle}`
      if (seenEdges.has(edgeId)) continue
      seenEdges.add(edgeId)
      edges.push(makeEdge(edgeId, inConn.source, nodeDef.id, inConn.source_handle, inConn.target_handle))
    }
  }

  return { nodes, edges }
}

function makeEdge(
  id: string,
  source: string,
  target: string,
  sourceHandle: string,
  targetHandle: string,
): Edge {
  return {
    id,
    source,
    target,
    sourceHandle,
    targetHandle,
    type: 'smoothstep',
    markerEnd: { type: 'arrowclosed' as MarkerType, width: 16, height: 16 },
    style: { stroke: '#6366f1' },
  }
}
