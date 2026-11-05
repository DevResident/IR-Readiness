import { useEffect, useState } from 'react'
import { api } from './api/client'
import type { Health, TabletopExercise, TabletopOptions, TabletopRequest } from './api/types'
import { ExerciseView } from './components/ExerciseView'
import { TabletopForm } from './components/TabletopForm'

function slug(text: string): string {
  return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '').slice(0, 60) || 'tabletop'
}

function download(filename: string, content: string, type: string) {
  const url = URL.createObjectURL(new Blob([content], { type }))
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [options, setOptions] = useState<TabletopOptions | null>(null)
  const [exercise, setExercise] = useState<TabletopExercise | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.health(), api.tabletopOptions()])
      .then(([h, o]) => {
        setHealth(h)
        setOptions(o)
      })
      .catch(() => setError('Cannot reach the backend. Is it running on port 8000?'))
  }, [])

  async function generate(request: TabletopRequest) {
    setLoading(true)
    setError(null)
    try {
      setExercise(await api.generateTabletop(request))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  async function exportMarkdown() {
    if (!exercise) return
    try {
      download(`${slug(exercise.title)}.md`, await api.tabletopMarkdown(exercise), 'text/markdown')
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Export failed')
    }
  }

  return (
    <div className="layout">
      <header>
        <h1>IR Readiness Copilot</h1>
        <p className="muted">
          Tabletop exercises mapped to NIST SP 800-61r3 and CSF 2.0, with every MITRE ATT&CK reference verified.
        </p>
        {health && (
          <p className="status">
            ATT&CK v{health.attack_version} ({health.attack_techniques} techniques) ·{' '}
            {health.llm_provider === 'demo' ? (
              <span className="pill demo">Demo mode</span>
            ) : health.llm_configured ? (
              <span className="pill ok">Model connected</span>
            ) : (
              <span className="pill warn">No API key configured</span>
            )}
          </p>
        )}
      </header>

      <aside>
        {options && <TabletopForm
            options={options}
            loading={loading}
            demo={health?.llm_provider === 'demo'}
            onSubmit={generate}
          />}
      </aside>

      <main>
        {error && (
          <div className="card error" role="alert">
            {error}
          </div>
        )}
        {exercise && options ? (
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
    </div>
  )
}
