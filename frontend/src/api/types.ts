// Mirrors backend/app/modules/tabletop/schemas.py (public models only).

export type PhaseId = 'prepare' | 'detect' | 'respond' | 'recover' | 'improve'

export interface TabletopRequest {
  industry: string
  org_size: string
  scenario: string
  audience: string
  duration_minutes: number
}

export interface ScenarioOption {
  id: string
  name: string
  summary: string
}

export interface PhaseOption {
  id: PhaseId
  name: string
  csf_functions: string[]
  rev2_equivalent: string
}

export interface TabletopOptions {
  industries: string[]
  org_sizes: string[]
  audiences: string[]
  scenarios: ScenarioOption[]
  phases: PhaseOption[]
}

export interface Health {
  status: string
  attack_version: string
  attack_techniques: number
  llm_provider: 'anthropic' | 'demo'
  llm_configured: boolean
}

export interface AttackTechniqueRef {
  id: string
  name: string
  tactics: string[]
  url: string | null
}

export interface Inject {
  sequence: number
  time_offset: string
  title: string
  description: string
  phase: PhaseId
  techniques: AttackTechniqueRef[]
  expected_actions: string[]
}

export interface Role {
  title: string
  responsibilities: string[]
}

export interface DiscussionQuestion {
  phase: PhaseId
  question: string
  csf_category: string | null
}

export interface FacilitatorGuide {
  preparation: string[]
  agenda: string[]
  facilitation_tips: string[]
  expected_gaps: string[]
}

export interface RejectedReference {
  location: string
  value: string
  reason: string
}

export interface ValidationReport {
  attack_version: string
  techniques_accepted: number
  techniques_remapped: string[]
  rejected: RejectedReference[]
  warnings: string[]
}

export interface TabletopExercise {
  request: TabletopRequest
  title: string
  narrative: string
  objectives: string[]
  roles: Role[]
  injects: Inject[]
  discussion_questions: DiscussionQuestion[]
  facilitator_guide: FacilitatorGuide
  validation: ValidationReport
}

// ---------- Module 1: assessment (mirrors backend/app/modules/assessment/schemas.py) ----------

export type ControlStatus = 'met' | 'partial' | 'missing'
export type Priority = 'critical' | 'high' | 'medium'

export interface CsfReference {
  id: string
  text: string
}

export interface ControlResult {
  control_id: string
  title: string
  topic: string
  phase: PhaseId
  priority: Priority
  csf: CsfReference[]
  sp800_61r3: string
  status: ControlStatus
  model_status: ControlStatus
  evidence: { quote: string; verified: boolean } | null
  rationale: string
  recommendation: string
}

export interface AssessmentReport {
  checklist: string
  document: { kind: string; pages: number | null; characters: number; truncated: boolean }
  summary: string
  score: { score: number; coverage: number; met: number; partial: number; missing: number; formula: string }
  results: ControlResult[]
  top_gaps: string[]
  validation: { unverified_quotes: string[]; unknown_controls: string[]; not_assessed: string[]; warnings: string[] }
}
