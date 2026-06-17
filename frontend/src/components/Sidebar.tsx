import { useState } from 'react'

import type { Catalog, ElementDefinition } from '../types'
import ExampleLibrary from './ExampleLibrary'
import Palette from './Palette'

interface SidebarProps {
  catalog: Catalog
  examples: Record<string, import('../types').ExampleSummary[]>
  examplesLoading: boolean
  onDragStart: (event: React.DragEvent, element: ElementDefinition) => void
  onLoadExample: (exampleId: string) => void
  onEditExample: (exampleId: string) => void
}

type SidebarTab = 'components' | 'examples'

export default function Sidebar({
  catalog,
  examples,
  examplesLoading,
  onDragStart,
  onLoadExample,
  onEditExample,
}: SidebarProps) {
  const [tab, setTab] = useState<SidebarTab>('components')

  return (
    <aside className="palette">
      <div className="sidebar-tabs">
        <button
          type="button"
          className={`sidebar-tab ${tab === 'components' ? 'active' : ''}`}
          onClick={() => setTab('components')}
        >
          Componentes
        </button>
        <button
          type="button"
          className={`sidebar-tab ${tab === 'examples' ? 'active' : ''}`}
          onClick={() => setTab('examples')}
        >
          Diagramas
        </button>
      </div>
      {tab === 'components' ? (
        <Palette catalog={catalog} onDragStart={onDragStart} />
      ) : (
        <ExampleLibrary
          examples={examples}
          loading={examplesLoading}
          onLoad={onLoadExample}
          onEdit={onEditExample}
        />
      )}
    </aside>
  )
}
