import { useState } from 'react'
import { api } from '../api/client'
import type { Health, TabletopExercise, TabletopOptions, TabletopRequest } from '../api/types'
import { ExerciseView } from '../components/ExerciseView'
import { TabletopForm } from '../components/TabletopForm'
import { download, errorMessage, slug } from '../lib/download'

interface Props {
  health: Health | null
  options: TabletopOptions
}

export function TabletopPage({ health, options }: Props) {
  const [exercise, setExercise] = useState<TabletopExercise | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function generate(request: TabletopRequest) {
    setLoading(true)
    setError(null)
    try {
      setExercise(await api.generateTabletop(request))
    } catch (e) {
      setError(errorMessage(e))
    } finally {
      setLoading(false)
    }
  }

  async function exportMarkdown() {
    if (!exercise) return
    try {
      download(`${slug(exercise.title)}.md`, await api.tabletopMarkdown(exercise), 'text/markdown')
    } catch (e) {
      setError(errorMessage(e, 'Export failed'))
    }
  }

  return (
    <>
      <aside>
        <TabletopForm options={options} loading={loading} demo={health?.llm_provider === 'demo'} onSubmit={generate} />
      </aside>
      <main>
        {error && (
          <div className="card error" role="alert">
            {error}
          </div>
        )}
        {exercise ? (
          <>
            <div className="toolbar">
              <button type="button" onClick={exportMarkdown}>
                Export Markdown
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() =>
                  download(`${slug(exercise.title)}.json`, JSON.stringify(exercise, null, 2), 'application/json')
                }
              >
                Export JSON
              </button>
            </div>
            <ExerciseView exercise={exercise} phases={options.phases} />
          </>
        ) : (
          !error && (
            <div className="card empty">
              <h2>No exercise yet</h2>
              <p>Pick a scenario and audience, then generate. The result appears here.</p>
            </div>
          )
        )}
      </main>
    </>
  )
}
