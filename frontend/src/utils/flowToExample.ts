import type { Edge, Node } from '@xyflow/react'

import type { ArchNodeData, ExampleNode } from '../types'

export function flowToExampleNodes(nodes: Node[], edges: Edge[]): ExampleNode[] {
  return nodes.map((n) => {
    const data = n.data as ArchNodeData
    const outgoing = edges
      .filter((e) => e.source === n.id)
      .map((e) => ({
        target: e.target,
        source_handle: e.sourceHandle ?? 'out',
        target_handle: e.targetHandle ?? 'in',
      }))
    const incoming = edges
      .filter((e) => e.target === n.id)
      .map((e) => ({
        source: e.source,
        source_handle: e.sourceHandle ?? 'out',
        target_handle: e.targetHandle ?? 'in',
      }))
    return {
      id: n.id,
      type: data.elementType,
      label: data.label,
      position: { x: n.position.x, y: n.position.y },
      parameters: data.parameters,
      connections: { outgoing, incoming },
    }
  })
}
