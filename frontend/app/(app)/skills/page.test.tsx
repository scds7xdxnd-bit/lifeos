import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import SkillsPage from './page'
import { skillsApi } from '@/lib/api/skills'

vi.mock('@/components/ui/input', () => ({
  Input: (props: React.InputHTMLAttributes<HTMLInputElement>) => <input {...props} />,
}))

vi.mock('@/lib/api/skills', () => ({
  skillsApi: {
    list: vi.fn(),
    overview: vi.fn(),
    get: vi.fn(),
    path: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    logPractice: vi.fn(),
    deleteSession: vi.fn(),
  },
}))

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <SkillsPage />
    </QueryClientProvider>,
  )
}

describe('SkillsPage create flow rollout behavior', () => {
  beforeEach(() => {
    vi.clearAllMocks()

    vi.mocked(skillsApi.list).mockResolvedValue({ ok: true, skills: [] })
    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 0, total_sessions: 0, at_risk: 0, active: 0 },
      groups: { at_risk: [], on_track: [], completed: [] },
      skills: [],
    })
  })

  it('allows create without goal when strict rollout is not active', async () => {
    vi.mocked(skillsApi.create).mockResolvedValue({ ok: true, skill: {} as never })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new skill/i }))
    await user.type(screen.getByLabelText(/name/i), 'Sketching')
    await user.click(screen.getByRole('button', { name: /create without goal/i }))

    await waitFor(() => {
      expect(skillsApi.create).toHaveBeenCalledTimes(1)
    })

    const payload = vi.mocked(skillsApi.create).mock.calls[0][0]
    expect(payload.name).toBe('Sketching')
    expect(payload.goal_type).toBeUndefined()
    expect(payload.goal_target_value).toBeUndefined()
  })

  it('moves to goal step when backend requires goal and submits with goal values', async () => {
    vi.mocked(skillsApi.create)
      .mockRejectedValueOnce(new Error('goal_required'))
      .mockResolvedValueOnce({ ok: true, skill: {} as never })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new skill/i }))
    await user.type(screen.getByLabelText(/name/i), 'Piano')
    await user.click(screen.getByRole('button', { name: /create without goal/i }))

    await screen.findByText(/goal endpoint is required in this rollout/i)
    expect(screen.getByText(/step 2 of 2/i)).toBeInTheDocument()

    await user.clear(screen.getByLabelText(/target value/i))
    await user.type(screen.getByLabelText(/target value/i), '15')
    await user.click(screen.getByRole('button', { name: /create skill/i }))

    await waitFor(() => {
      expect(skillsApi.create).toHaveBeenCalledTimes(2)
    })

    const secondPayload = vi.mocked(skillsApi.create).mock.calls[1][0]
    expect(secondPayload.name).toBe('Piano')
    expect(secondPayload.goal_type).toBe('sessions')
    expect(secondPayload.goal_target_value).toBe(15)
  })
})
