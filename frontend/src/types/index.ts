export interface ParameterDef {
  key: string
  label: string
  type: 'number' | 'integer' | 'string' | 'boolean' | 'select'
  default: unknown
  min?: number
  max?: number
  step?: number
  options?: string[]
  unit?: string
  description?: string
}

export interface PortDef {
  id: string
  label: string
  type: 'input' | 'output'
}

export interface ElementDefinition {
  type: string
  label: string
  category: string
  icon: string
  color: string
  description: string
  inputs: PortDef[]
  outputs: PortDef[]
  parameters: ParameterDef[]
  simulatable: boolean
}

export type Catalog = Record<string, ElementDefinition[]>

export interface NodeMetrics {
  node_id: string
  requests_received: number
  requests_processed: number
  requests_failed: number
  queue_depth: number
  avg_latency_ms: number
  current_load: number
  extra: Record<string, unknown>
}

export interface SimulationMetrics {
  elapsed_seconds: number
  total_requests: number
  completed_requests: number
  failed_requests: number
  nodes: Record<string, NodeMetrics>
}

export interface ArchNodeData {
  label: string
  elementType: string
  icon: string
  color: string
  parameters: Record<string, unknown>
  definition?: ElementDefinition
  metrics?: NodeMetrics
  [key: string]: unknown
}

export interface NodeConnectionRef {
  target: string
  source_handle: string
  target_handle: string
}

export interface IncomingConnectionRef {
  source: string
  source_handle: string
  target_handle: string
}

export interface NodeConnections {
  outgoing: NodeConnectionRef[]
  incoming: IncomingConnectionRef[]
}

export interface ExampleNode {
  id: string
  type: string
  label: string
  position: { x: number; y: number }
  parameters: Record<string, unknown>
  connections: NodeConnections
}

export interface ArchitectureExample {
  id: string
  title: string
  description: string
  category: string
  nodes: ExampleNode[]
}

export interface ExampleSummary {
  id: string
  title: string
  description: string
  category: string
  node_count: number
}
