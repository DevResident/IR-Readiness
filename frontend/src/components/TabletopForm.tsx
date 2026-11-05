import { useState, type FormEvent } from 'react'
import type { TabletopOptions, TabletopRequest } from '../api/types'
import { AUDIENCE_LABELS, ORG_SIZE_LABELS, humanize } from '../labels'

interface Props {
  options: TabletopOptions
  loading: boolean
  onSubmit: (request: TabletopRequest) => void
}

export function TabletopForm({ options, loading, onSubmit }: Props) {
  const [form, setForm] = useState<TabletopRequest>({
    industry: options.industries[0],
    org_size: options.org_sizes[1] ?? options.org_sizes[0],
    scenario: options.scenarios.find((s) => s.id === 'ransomware')?.id ?? options.scenarios[0].id,
    audience: options.audiences[0],
    duration_minutes: 90,
  })
  const set = <K extends keyof TabletopRequest>(key: K, value: TabletopRequest[K]) =>
    setForm((f) => ({ ...f, [key]: value }))

  const scenario = options.scenarios.find((s) => s.id === form.scenario)

  function submit(e: FormEvent) {
    e.preventDefault()
    onSubmit(form)
  }

  return (
    <form className="card form" onSubmit={submit}>
      <label>
        Industry
        <select value={form.industry} onChange={(e) => set('industry', e.target.value)}>
          {options.industries.map((i) => (
            <option key={i} value={i}>{humanize(i)}</option>
          ))}
        </select>
      </label>

      <label>
        Organization size
        <select value={form.org_size} onChange={(e) => set('org_size', e.target.value)}>
          {options.org_sizes.map((s) => (
            <option key={s} value={s}>{ORG_SIZE_LABELS[s] ?? humanize(s)}</option>
          ))}
        </select>
      </label>

      <label>
        Scenario
        <select value={form.scenario} onChange={(e) => set('scenario', e.target.value)}>
          {options.scenarios.map((s) => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </label>

      <label>
        Audience
        <select value={form.audience} onChange={(e) => set('audience', e.target.value)}>
          {options.audiences.map((a) => (
            <option key={a} value={a}>{AUDIENCE_LABELS[a] ?? humanize(a)}</option>
          ))}
        </select>
      </label>

      <label>
        Duration (minutes)
        <input
          type="number"
          min={30}
          max={240}
          step={15}
          required
          value={form.duration_minutes}
          onChange={(e) => set('duration_minutes', Number(e.target.value))}
        />
      </label>

      {scenario && <p className="hint">{scenario.summary}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Generating… (this can take a minute)' : 'Generate exercise'}
      </button>
    </form>
  )
}
