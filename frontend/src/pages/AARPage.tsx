import { useState, type FormEvent } from 'react'
import { api } from '../api/client'
import type { AARObservation, AARRequest, AfterActionReport } from '../api/types'
import { download, errorMessage, slug } from '../lib/download'

const MIN_CHARS = 50
const MAX_CHARS = 30_000

export function AARPage() {
  const [form, setForm] = useState<AARRequest>({ notes: '', exercise_title: '', event_type: 'tabletop', event_date: '' })
  const [report, setReport] = useState<AfterActionReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const chars = form.notes.trim().length

  async function submit(e: FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      setReport(
        await api.generateAAR({
          ...form,
          exercise_title: form.exercise_title?.trim() || null,
          event_date: form.event_date || null,
        }),
      )
    } catch (err) {
      setError(errorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  async function exportAs(kind: 'docx' | 'md') {
    if (!report) return
    try {
      const name = slug(report.title)
      if (kind === 'docx') {
        download(`${name}.docx`, await api.aarDocx(report), 'application/octet-stream')
      } else {
        download(`${name}.md`, await api.aarMarkdown(report), 'text/markdown')
      }
    } catch (err) {
      setError(errorMessage(err, 'Export failed'))
    }
  }

  return (
    <>
      <aside>
        <form className="card form" onSubmit={submit}>
          <label>
            Title (optional)
            <input
              type="text"
              maxLength={200}
              value={form.exercise_title ?? ''}
              onChange={(e) => setForm({ ...form, exercise_title: e.target.value })}
            />
          </label>
          <label>
            Event type
            <select
              value={form.event_type}
              onChange={(e) => setForm({ ...form, event_type: e.target.value as AARRequest['event_type'] })}
            >
              <option value="tabletop">Tabletop exercise</option>
              <option value="incident">Real incident</option>
            </select>
          </label>
          <label>
            Date (optional)
            <input
              type="date"
              value={form.event_date ?? ''}
              onChange={(e) => setForm({ ...form, event_date: e.target.value })}
            />
          </label>
          <label>
            Notes
            <textarea
              rows={14}
              required
              minLength={MIN_CHARS}
              maxLength={MAX_CHARS}
              placeholder="Paste the facilitator's or scribe's notes: what happened, decisions, disagreements, what went well."
              value={form.notes}
              onChange={(e) => setForm({ ...form, notes: e.target.value })}
            />
          </label>
          <p className="hint">
            {chars.toLocaleString()} / {MAX_CHARS.toLocaleString()} characters. Avoid real names and secrets: notes are
            sent to the AI model but are not stored or logged.
          </p>
          <button type="submit" disabled={loading || chars < MIN_CHARS}>
            {loading ? 'Writing report… (this can take a minute)' : 'Generate report'}
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
            <div className="toolbar no-print">
              <button type="button" onClick={() => exportAs('docx')}>
                Export DOCX
              </button>
              <button type="button" className="secondary" onClick={() => exportAs('md')}>
                Export Markdown
              </button>
              <button
                type="button"
                className="secondary"
                onClick={() =>
                  download(`${slug(report.title)}.json`, JSON.stringify(report, null, 2), 'application/json')
                }
              >
                Download JSON
              </button>
              <button type="button" className="secondary" onClick={() => window.print()}>
                Print / PDF
              </button>
            </div>
            <ReportView report={report} />
          </>
        ) : (
          !error && (
            <div className="card empty">
              <h2>No report yet</h2>
              <p>Paste exercise or incident notes to draft an After-Action Report with prioritized recommendations.</p>
            </div>
          )
        )}
      </main>
    </>
  )
}

function ReportView({ report }: { report: AfterActionReport }) {
  const v = report.validation
  const issues = [
    ...v.warnings,
    ...v.rejected_csf_categories.map((x) => `Unknown CSF category removed (${x})`),
    ...v.dropped_links.map((x) => `Link to a missing observation removed (${x})`),
  ]
  return (
    <article className="aar">
      {issues.length > 0 && (
        <section className="card validation attention">
          <strong>Review before sharing</strong>
          <ul>
            {issues.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </section>
      )}
      <h2>{report.title}</h2>
      <p className="muted small">
        {report.event_type === 'tabletop' ? 'Tabletop exercise' : 'Incident'}
        {report.event_date && ` · ${report.event_date}`}
      </p>
      <section className="card">
        <h3>Executive summary</h3>
        <p>{report.executive_summary}</p>
        <h4>Scope</h4>
        <p>{report.scope}</p>
      </section>

      <section>
        <h3>Recommendations</h3>
        <div className="table-wrap">
          <table className="recs">
            <thead>
              <tr>
                <th>#</th>
                <th>Recommendation</th>
                <th>Priority</th>
                <th>Timeframe</th>
                <th>Suggested owner</th>
                <th>Addresses</th>
              </tr>
            </thead>
            <tbody>
              {report.recommendations.map((r) => (
                <tr key={r.rank}>
                  <td>{r.rank}</td>
                  <td>
                    <strong>{r.title}</strong>
                    <br />
                    {r.action}
                    {r.csf_category && (
                      <abbr className="csf" title={r.csf_title ?? ''}>
                        {' '}
                        {r.csf_category}
                      </abbr>
                    )}
                  </td>
                  <td>
                    <span className={`prio ${r.priority}`}>{r.priority}</span>
                  </td>
                  <td>{r.timeframe}</td>
                  <td>{r.suggested_owner}</td>
                  <td>
                    {r.addresses.map((id) => (
                      <a key={id} href={`#obs-${id}`}>
                        {id}{' '}
                      </a>
                    ))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="card">
        <h3>Gaps</h3>
        <ul>
          {report.gaps.map((g, i) => (
            <li key={i}>{g}</li>
          ))}
        </ul>
      </section>

      <h3>Areas for improvement</h3>
      {report.areas_for_improvement.map((o) => (
        <ObservationCard key={o.id} o={o} />
      ))}
      <h3>Strengths</h3>
      {report.strengths.map((o) => (
        <ObservationCard key={o.id} o={o} />
      ))}
      <p className="muted small">Generated with IR Readiness Copilot. Review before distribution.</p>
    </article>
  )
}

function ObservationCard({ o }: { o: AARObservation }) {
  return (
    <section id={`obs-${o.id}`} className={`card observation ${o.kind}`}>
      <h4>
        <code>{o.id}</code> {o.title}
      </h4>
      <p className="muted small">
        Phase: {o.phase}
        {o.csf_category && (
          <>
            {' '}
            · CSF{' '}
            <abbr className="csf" title={o.csf_title ?? ''}>
              {o.csf_category}
            </abbr>
          </>
        )}
      </p>
      <p>{o.detail}</p>
      {o.evidence_quote && (
        <blockquote className={o.evidence_verified ? 'quote verified' : 'quote unverified'}>
          “{o.evidence_quote}”
          <span className="quote-tag">{o.evidence_verified ? 'Found in notes' : 'UNVERIFIED: not found in notes'}</span>
        </blockquote>
      )}
    </section>
  )
}
