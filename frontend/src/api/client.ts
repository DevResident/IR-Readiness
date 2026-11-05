import type { AARRequest, AfterActionReport, AssessmentReport, Health, TabletopExercise, TabletopOptions, TabletopRequest } from './types'

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

// The backend already returns generic, user-safe messages in `detail`.
async function readError(res: Response): Promise<ApiError> {
  let message = `Request failed (${res.status})`
  try {
    const body = await res.json()
    if (typeof body.detail === 'string') message = body.detail
    else if (Array.isArray(body.detail)) message = 'Some inputs are invalid. Check the form and try again.'
  } catch {
    // Not JSON (e.g. the backend is down and the dev proxy answered): keep the generic message.
  }
  return new ApiError(res.status, message)
}

async function request(path: string, init?: RequestInit): Promise<Response> {
  const res = await fetch(`/api${path}`, init)
  if (!res.ok) throw await readError(res)
  return res
}

const json = (body: unknown): RequestInit => ({
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(body),
})

export const api = {
  health: async (): Promise<Health> => (await request('/health')).json(),
  tabletopOptions: async (): Promise<TabletopOptions> => (await request('/tabletop/options')).json(),
  generateTabletop: async (req: TabletopRequest): Promise<TabletopExercise> =>
    (await request('/tabletop', json(req))).json(),
  assessPlan: async (file: File): Promise<AssessmentReport> => {
    const body = new FormData()
    body.append('file', file)
    return (await request('/assessment', { method: 'POST', body })).json()
  },
  generateAAR: async (req: AARRequest): Promise<AfterActionReport> => (await request('/aar', json(req))).json(),
  aarMarkdown: async (report: AfterActionReport): Promise<string> => (await request('/aar/markdown', json(report))).text(),
  aarDocx: async (report: AfterActionReport): Promise<Blob> => (await request('/aar/docx', json(report))).blob(),
  tabletopMarkdown: async (exercise: TabletopExercise): Promise<string> =>
    (await request('/tabletop/markdown', json(exercise))).text(),
}
