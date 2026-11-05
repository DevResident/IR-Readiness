import { useEffect, useState } from 'react'
import { api } from './api/client'
import type { Health, TabletopOptions } from './api/types'
import { AARPage } from './pages/AARPage'
import { AssessmentPage } from './pages/AssessmentPage'
import { TabletopPage } from './pages/TabletopPage'

type Tab = 'tabletop' | 'assessment' | 'aar'

const TABS: { id: Tab; label: string }[] = [
  { id: 'tabletop', label: 'Tabletop exercise' },
  { id: 'assessment', label: 'Plan assessment' },
  { id: 'aar', label: 'After-action report' },
]

function initialTab(): Tab {
  const hash = window.location.hash.slice(1)
  return TABS.some((t) => t.id === hash) ? (hash as Tab) : 'tabletop'
}

export default function App() {
  const [health, setHealth] = useState<Health | null>(null)
  const [options, setOptions] = useState<TabletopOptions | null>(null)
  const [tab, setTab] = useState<Tab>(initialTab)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    Promise.all([api.health(), api.tabletopOptions()])
      .then(([h, o]) => {
        setHealth(h)
        setOptions(o)
      })
      .catch(() => setError('Cannot reach the backend. Is it running on port 8000?'))
  }, [])

  function select(next: Tab) {
    setTab(next)
    history.replaceState(null, '', `#${next}`)
  }

  return (
    <div className="layout">
      <header className="no-print">
        <h1>IR Readiness Copilot</h1>
        <p className="muted">
          Incident response readiness checks, tabletop exercises and after-action reports mapped to NIST SP 800-61r3 and CSF 2.0, with every
          framework reference verified.
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
        <nav className="tabs" role="tablist" aria-label="Modules">
          {TABS.map((t) => (
            <button
              key={t.id}
              type="button"
              role="tab"
              aria-selected={tab === t.id}
              className={tab === t.id ? 'tab active' : 'tab'}
              onClick={() => select(t.id)}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>

      {error && (
        <main>
          <div className="card error" role="alert">
            {error}
          </div>
        </main>
      )}
      {!error && tab === 'tabletop' && options && <TabletopPage health={health} options={options} />}
      {!error && tab === 'assessment' && <AssessmentPage />}
      {!error && tab === 'aar' && <AARPage />}
    </div>
  )
}
