import { useState, type FormEvent } from 'react'
import { api } from '../api/client'
import type { AssessmentReport, ControlResult, ControlStatus } from '../api/types'
import { download, errorMessage } from '../lib/download'

const MAX_BYTES = 5 * 1024 * 1024
const ACCEPT = '.pdf,.docx,.md,.markdown,.txt'
const STATUS_LABEL: Record<ControlStatus, string> = { met: 'Met', partial: 'Partial', missing: 'Missing' }

export function AssessmentPage() {
  const [file, setFile] = useState<File | null>(null)
  const [report, setReport] = useState<AssessmentReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit(e: FormEvent) {
    e.preventDefault()
    if (!file) return
    if (file.size > MAX_BYTES) {
      setError('The file is larger than 5 MB.')
      return
    }
    setLoading(true)
    setError(null)
    try {
      setReport(await api.assessPlan(file))
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <aside>
        <form className="card form" onSubmit={submit}>
          <label>
            Incident response plan
            <input
              type="file"
              accept={ACCEPT}
              required
              onChange={(e) => {
                setFile(e.target.files?.[0] ?? null)
                setError(null)
              }}
            />
          </label>
          <p className="hint">
            PDF, DOCX or Markdown, up to 5 MB. The file is processed in memory and is not stored or logged.
          </p>
          <button type="submit" disabled={!file || loading}>
            {loading ? 'Assessing… (this can take a minute)' : 'Assess plan'}
          </button>
        </form>
      </aside>
      <main>
        {error && (
          <div className="card error" role="alert">
            {error}
          </div>
        )}
        {report ? (
          <>
            <div className="toolbar">
              <button
                type="button"
                className="secondary"
                onClick={() => download('ir-plan-assessment.json', JSON.stringify(report, null, 2), 'application/json')}
              >
                Export JSON
              </button>
            </div>
            <ReportView report={report} />
          </>
        ) : (
          !error && (
            <div className="card empty">
              <h2>No assessment yet</h2>
              <p>Upload an incident response plan to check it against NIST SP 800-61r3 and CSF 2.0.</p>
            </div>
          )
        )}
      </main>
    </>
  )
}

function ReportView({ report }: { report: AssessmentReport }) {
  const [filter, setFilter] = useState<ControlStatus | 'all'>('all')
  const s = report.score
  const v = report.validation
  const byId = new Map(report.results.map((r) => [r.control_id, r]))
  const shown = report.results.filter((r) => filter === 'all' || r.status === filter)

  return (
    <article className="assessment">
      <section className="scores" aria-label="Score">
        <div className="card stat">
          <span className="stat-value">{s.score}</span>
          <span className="stat-label">Readiness score</span>
        </div>
        <div className="card stat">
          <span className="stat-value">{s.coverage}%</span>
          <span className="stat-label">Coverage</span>
        </div>
        <div className="card stat">
          <span className="stat-value">
            <span className="status-text met">{s.met}</span> / <span className="status-text partial">{s.partial}</span> /{' '}
            <span className="status-text missing">{s.missing}</span>
          </span>
          <span className="stat-label">Met / partial / missing</span>
        </div>
      </section>
      <p className="muted small">
        {s.formula}. Checklist: {report.checklist}.
      </p>

      {(v.warnings.length > 0 || v.unknown_controls.length > 0 || v.not_assessed.length > 0) && (
        <section className="card validation attention">
          <strong>Validation</strong>
          <ul>
            {v.warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
            {v.not_assessed.length > 0 && <li>Not assessed by the model: {v.not_assessed.join(', ')}</li>}
            {v.unknown_controls.length > 0 && <li>Unknown control IDs ignored: {v.unknown_controls.join(', ')}</li>}
          </ul>
        </section>
      )}

      <section className="card">
        <h3>Summary</h3>
        <p>{report.summary}</p>
        {report.top_gaps.length > 0 && (
          <>
            <h4>Fix first</h4>
            <ol>
              {report.top_gaps.map((id) => {
                const r = byId.get(id)
                return (
                  <li key={id}>
                    <a href={`#${id}`}>
                      {id} {r?.title}
                    </a>{' '}
                    {r && <StatusBadge status={r.status} />}
                  </li>
                )
              })}
            </ol>
          </>
        )}
      </section>

      <div className="filters" role="group" aria-label="Filter controls by status">
        {(['all', 'missing', 'partial', 'met'] as const).map((f) => (
          <button
            key={f}
            type="button"
            className={filter === f ? '' : 'secondary'}
            aria-pressed={filter === f}
            onClick={() => setFilter(f)}
          >
            {f === 'all' ? `All (${report.results.length})` : `${STATUS_LABEL[f]} (${s[f]})`}
          </button>
        ))}
      </div>

      {shown.map((r) => (
        <ControlCard key={r.control_id} result={r} />
      ))}
    </article>
  )
}

function StatusBadge({ status }: { status: ControlStatus }) {
  return <span className={`status-badge ${status}`}>{STATUS_LABEL[status]}</span>
}

function ControlCard({ result: r }: { result: ControlResult }) {
  const downgraded = r.status !== r.model_status
  return (
    <section id={r.control_id} className={`card control status-border-${r.status}`}>
      <div className="control-head">
        <h4>
          <code>{r.control_id}</code> {r.title}
        </h4>
        <StatusBadge status={r.status} />
      </div>
      <p className="muted small">
        Priority: {r.priority} · Phase: {r.phase} · {r.sp800_61r3}
      </p>
      <p className="csf-list">
        {r.csf.map((c) => (
          <abbr key={c.id} title={c.text} className="csf">
            {c.id}
          </abbr>
        ))}
      </p>
      {r.evidence && (
        <blockquote className={r.evidence.verified ? 'quote verified' : 'quote unverified'}>
          “{r.evidence.quote}”
          <span className="quote-tag">{r.evidence.verified ? 'Verified in document' : 'UNVERIFIED: not found in document'}</span>
        </blockquote>
      )}
      {downgraded && (
        <p className="small warn-text">
          The model proposed “{STATUS_LABEL[r.model_status]}”; downgraded because its evidence could not be verified.
        </p>
      )}
      <p>{r.rationale}</p>
      {r.recommendation && (
        <p>
          <strong>Recommendation:</strong> {r.recommendation}
        </p>
      )}
    </section>
  )
}
