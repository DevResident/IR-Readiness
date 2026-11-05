import type { PhaseId, PhaseOption, TabletopExercise } from '../api/types'

interface Props {
  exercise: TabletopExercise
  phases: PhaseOption[]
}

const List = ({ items }: { items: string[] }) => (
  <ul>
    {items.map((item, i) => (
      <li key={i}>{item}</li>
    ))}
  </ul>
)

export function ExerciseView({ exercise, phases }: Props) {
  const phaseName = (id: PhaseId) => phases.find((p) => p.id === id)?.name ?? id
  const v = exercise.validation
  const guide = exercise.facilitator_guide

  return (
    <article className="exercise">
      <ValidationPanel exercise={exercise} />

      <h2>{exercise.title}</h2>
      <p>{exercise.narrative}</p>

      <section className="card">
        <h3>Objectives</h3>
        <List items={exercise.objectives} />
      </section>

      <section className="card">
        <h3>Roles</h3>
        <div className="roles">
          {exercise.roles.map((r) => (
            <div key={r.title} className="role">
              <strong>{r.title}</strong>
              <List items={r.responsibilities} />
            </div>
          ))}
        </div>
      </section>

      <section>
        <h3>Injects</h3>
        <ol className="timeline">
          {exercise.injects.map((inj) => (
            <li key={inj.sequence} className={`inject phase-${inj.phase}`}>
              <div className="inject-meta">
                <span className="time">{inj.time_offset}</span>
                <span className={`phase-tag phase-${inj.phase}`}>{phaseName(inj.phase)}</span>
              </div>
              <h4>
                {inj.sequence}. {inj.title}
              </h4>
              <p>{inj.description}</p>
              {inj.techniques.length > 0 && (
                <div className="techniques" aria-label="MITRE ATT&CK techniques">
                  {inj.techniques.map((t) => (
                    <a
                      key={t.id}
                      className="badge"
                      href={t.url ?? undefined}
                      target="_blank"
                      rel="noreferrer noopener"
                      title={t.tactics.join(', ')}
                    >
                      <code>{t.id}</code> {t.name}
                    </a>
                  ))}
                </div>
              )}
              <details>
                <summary>Expected actions ({inj.expected_actions.length})</summary>
                <List items={inj.expected_actions} />
              </details>
            </li>
          ))}
        </ol>
      </section>

      <section className="card">
        <h3>Discussion questions</h3>
        {phases.map((p) => {
          const qs = exercise.discussion_questions.filter((q) => q.phase === p.id)
          if (qs.length === 0) return null
          return (
            <div key={p.id} className="question-group">
              <h4>
                <span className={`phase-tag phase-${p.id}`}>{p.name}</span>
                <span className="muted"> CSF {p.csf_functions.join(', ')} · Rev. 2: {p.rev2_equivalent}</span>
              </h4>
              <ol>
                {qs.map((q, i) => (
                  <li key={i}>
                    {q.question} {q.csf_category && <code className="csf">{q.csf_category}</code>}
                  </li>
                ))}
              </ol>
            </div>
          )
        })}
      </section>

      <section className="card">
        <h3>Facilitator guide</h3>
        <div className="guide">
          <div>
            <h4>Preparation</h4>
            <List items={guide.preparation} />
          </div>
          <div>
            <h4>Agenda</h4>
            <List items={guide.agenda} />
          </div>
          <div>
            <h4>Facilitation tips</h4>
            <List items={guide.facilitation_tips} />
          </div>
          <div>
            <h4>Expected gaps</h4>
            <List items={guide.expected_gaps} />
          </div>
        </div>
      </section>

      <p className="muted small">
        ATT&CK Enterprise v{v.attack_version}. Fictional scenario for training purposes.
      </p>
    </article>
  )
}

function ValidationPanel({ exercise }: { exercise: TabletopExercise }) {
  const v = exercise.validation
  const clean = v.rejected.length === 0 && v.techniques_remapped.length === 0 && v.warnings.length === 0
  return (
    <section className={`card validation ${clean ? 'ok' : 'attention'}`} aria-label="Validation report">
      <strong>Validation</strong>
      <span>
        {v.techniques_accepted} ATT&CK technique{v.techniques_accepted === 1 ? '' : 's'} verified against v
        {v.attack_version} · {v.techniques_remapped.length} remapped · {v.rejected.length} rejected
      </span>
      {v.warnings.length > 0 && (
        <ul>
          {v.warnings.map((w, i) => (
            <li key={i}>{w}</li>
          ))}
        </ul>
      )}
      {v.techniques_remapped.length > 0 && <List items={v.techniques_remapped} />}
      {v.rejected.length > 0 && (
        <ul>
          {v.rejected.map((r, i) => (
            <li key={i}>
              Rejected {r.location}: <code>{r.value}</code> ({r.reason})
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}
