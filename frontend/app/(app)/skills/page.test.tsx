import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import type { InputHTMLAttributes } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import SkillsPage from './page'
import { skillsApi } from '@/lib/api/skills'

vi.mock('@/components/ui/input', () => ({
  Input: (props: InputHTMLAttributes<HTMLInputElement>) => <input {...props} />,
}))

vi.mock('@/lib/api/skills', () => ({
  skillsApi: {
    list: vi.fn(),
    overview: vi.fn(),
    get: vi.fn(),
    path: vi.fn(),
    forecast: vi.fn(),
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

    vi.mocked(skillsApi.forecast).mockResolvedValue({
      ok: true,
      forecast: {
        skill_id: 1,
        horizon_days: 7,
        forecast_state: 'on_track',
        risk_reason: null,
        goal: null,
        baseline: {
          avg_daily_minutes_last_14: 0,
          sessions_last_14: 0,
          total_minutes_last_14: 0,
        },
        projection: {
          projected_minutes_next_window: 0,
          projected_sessions_next_window: 0,
          projected_goal_progress_ratio: null,
        },
      },
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

  it('renders forecast reason copy when forecast data is available', async () => {
    vi.mocked(skillsApi.list).mockResolvedValue({
      ok: true,
      skills: [
        {
          id: 1,
          name: 'Piano',
          category: 'Music',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 60,
          session_count: 2,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 2,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 1, total_sessions: 2, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 60,
            session_count: 2,
            progress_state: 'on_track',
            goal: null,
            primary_action: 'continue_practice',
            requires_goal_setup: true,
            risk_reason: null,
          },
        ],
        completed: [],
      },
      skills: [
        {
          skill_id: 1,
          name: 'Piano',
          category: 'Music',
          total_minutes: 60,
          session_count: 2,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: true,
          risk_reason: null,
        },
      ],
    })

    vi.mocked(skillsApi.forecast).mockResolvedValue({
      ok: true,
      forecast: {
        skill_id: 1,
        horizon_days: 7,
        forecast_state: 'at_risk',
        risk_reason: 'no_recent_sessions',
        goal: null,
        baseline: {
          avg_daily_minutes_last_14: 2,
          sessions_last_14: 1,
          total_minutes_last_14: 28,
        },
        projection: {
          projected_minutes_next_window: 14,
          projected_sessions_next_window: 1,
          projected_goal_progress_ratio: null,
        },
      },
    })

    renderPage()

    expect(await screen.findByText(/forecast \(7d\)/i)).toBeInTheDocument()
    expect(await screen.findByText(/recent activity is low, so your goal trajectory may slip this week\./i)).toBeInTheDocument()
  })

  it('renders qualitative-goal forecast reason copy for non-projectable goal types', async () => {
    vi.mocked(skillsApi.list).mockResolvedValue({
      ok: true,
      skills: [
        {
          id: 1,
          name: 'Piano',
          category: 'Music',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 60,
          session_count: 2,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 2,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 1, total_sessions: 2, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 60,
            session_count: 2,
            progress_state: 'on_track',
            goal: null,
            primary_action: 'continue_practice',
            requires_goal_setup: true,
            risk_reason: null,
          },
        ],
        completed: [],
      },
      skills: [
        {
          skill_id: 1,
          name: 'Piano',
          category: 'Music',
          total_minutes: 60,
          session_count: 2,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: true,
          risk_reason: null,
        },
      ],
    })

    vi.mocked(skillsApi.forecast).mockResolvedValue({
      ok: true,
      forecast: {
        skill_id: 1,
        horizon_days: 7,
        forecast_state: 'insufficient_data',
        risk_reason: 'non_projectable_goal_type',
        goal: null,
        baseline: {
          avg_daily_minutes_last_14: 2,
          sessions_last_14: 2,
          total_minutes_last_14: 30,
        },
        projection: {
          projected_minutes_next_window: 15,
          projected_sessions_next_window: 1,
          projected_goal_progress_ratio: null,
        },
      },
    })

    renderPage()

    expect(await screen.findByText(/this goal type is qualitative, so we show activity guidance without numeric projection\./i)).toBeInTheDocument()
  })
})
