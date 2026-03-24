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

    vi.mocked(skillsApi.path).mockResolvedValue({
      ok: true,
      path: {
        skill_id: 1,
        progress_state: 'on_track',
        risk_reason: null,
        goal: null,
        steps: [],
        next_recommended_step: null,
      },
    })

    vi.mocked(skillsApi.logPractice).mockResolvedValue({
      ok: true,
      session: {
        id: 1,
        skill_id: 1,
        duration_minutes: 30,
        intensity: null,
        step_id: null,
        notes: null,
        practiced_at: new Date().toISOString(),
      },
      next_recommended_step: null,
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

  it('allows creating from step 2 without goal values when strict rollout is not active', async () => {
    vi.mocked(skillsApi.create).mockResolvedValue({ ok: true, skill: {} as never })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new skill/i }))
    await user.type(screen.getByLabelText(/name/i), 'Sketching')
    await user.click(screen.getByRole('button', { name: /^continue$/i }))
    await user.clear(screen.getByLabelText(/target value/i))
    await user.click(screen.getByRole('button', { name: /create skill/i }))

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
    await user.click(screen.getByRole('button', { name: /^continue$/i }))
    await user.clear(screen.getByLabelText(/target value/i))
    await user.click(screen.getByRole('button', { name: /create skill/i }))

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

  it('shows live skill preview while typing in step 1', async () => {
    vi.mocked(skillsApi.create).mockResolvedValue({ ok: true, skill: {} as never })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new skill/i }))
    expect(await screen.findByText(/live reflection/i)).toBeInTheDocument()

    await user.type(screen.getByLabelText(/name/i), 'Piano')
    await user.type(screen.getByLabelText(/category/i), 'Music')

    expect(await screen.findByText('Piano')).toBeInTheDocument()
    expect((await screen.findAllByText('Music')).length).toBeGreaterThan(0)
  })

  it('applies goal target presets on step 2 before creating', async () => {
    vi.mocked(skillsApi.create).mockResolvedValue({ ok: true, skill: {} as never })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new skill/i }))
    await user.type(screen.getByLabelText(/name/i), 'Piano')
    await user.click(screen.getByRole('button', { name: /^continue$/i }))

    await screen.findByText(/quick presets/i)
    await user.click(screen.getByRole('button', { name: '20' }))
    expect(screen.getByLabelText(/target value/i)).toHaveValue(20)

    await user.click(screen.getByRole('button', { name: /create skill/i }))

    await waitFor(() => {
      expect(skillsApi.create).toHaveBeenCalledTimes(1)
    })

    const payload = vi.mocked(skillsApi.create).mock.calls[0][0]
    expect(payload.goal_type).toBe('sessions')
    expect(payload.goal_target_value).toBe(20)
  })

  it('uses create-goal type pills and submits selected type with type-aware helper copy', async () => {
    vi.mocked(skillsApi.create).mockResolvedValue({ ok: true, skill: {} as never })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /new skill/i }))
    await user.type(screen.getByLabelText(/name/i), 'Strength Training')
    await user.click(screen.getByRole('button', { name: /^continue$/i }))

    expect(await screen.findByText(/use sessions for consistency goals/i)).toBeInTheDocument()
    expect(await screen.findByText(/unit: sessions/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /hours/i }))
    expect(await screen.findByText(/use hours for volume goals/i)).toBeInTheDocument()
    expect(await screen.findByText(/unit: hours/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /milestones/i }))
    expect(await screen.findByText(/use milestones for qualitative checkpoints/i)).toBeInTheDocument()
    expect(await screen.findByText(/unit: milestones/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: '5' }))
    await user.click(screen.getByRole('button', { name: /create skill/i }))

    await waitFor(() => {
      expect(skillsApi.create).toHaveBeenCalledTimes(1)
    })

    const payload = vi.mocked(skillsApi.create).mock.calls[0][0]
    expect(payload.goal_type).toBe('milestones')
    expect(payload.goal_target_value).toBe(5)
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
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for piano/i }))

    expect(await screen.findByText(/forecast \(7d\)/i)).toBeInTheDocument()
    expect(await screen.findByText(/recent activity is low, so your goal trajectory may slip this week\./i)).toBeInTheDocument()
  })

  it('supports forecast scenario chips and updates projected summary deterministically', async () => {
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
          total_minutes: 120,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 4,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 2, total_sessions: 4, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 120,
            session_count: 4,
            progress_state: 'on_track',
            goal: {
              goal_type: 'sessions',
              target_value: 10,
              current_value: 4,
              progress_ratio: 0.4,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 120,
          session_count: 4,
          progress_state: 'on_track',
          goal: {
            goal_type: 'sessions',
            target_value: 10,
            current_value: 4,
            progress_ratio: 0.4,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    vi.mocked(skillsApi.forecast).mockResolvedValue({
      ok: true,
      forecast: {
        skill_id: 1,
        horizon_days: 7,
        forecast_state: 'on_track',
        risk_reason: null,
        goal: {
          goal_type: 'sessions',
          target_value: 10,
          current_value: 4,
          progress_ratio: 0.4,
          deadline: null,
        },
        baseline: {
          avg_daily_minutes_last_14: 2,
          sessions_last_14: 1,
          total_minutes_last_14: 28,
        },
        projection: {
          projected_minutes_next_window: 14,
          projected_sessions_next_window: 1,
          projected_goal_progress_ratio: 0.6,
        },
      },
    })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for piano/i }))

    expect(await screen.findByText(/forecast scenarios/i)).toBeInTheDocument()
    expect(await screen.findByText(/projected 14m and 1 sessions\./i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /\+1 session/i }))

    expect(await screen.findByText(/projected 42m and 2 sessions\./i)).toBeInTheDocument()
    expect(await screen.findByText(/scenario progress: 80% of goal\./i)).toBeInTheDocument()
  })

  it('updates forecast projection with +30 minutes scenario', async () => {
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
          total_minutes: 120,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 4,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 2, total_sessions: 4, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 120,
            session_count: 4,
            progress_state: 'on_track',
            goal: {
              goal_type: 'sessions',
              target_value: 10,
              current_value: 4,
              progress_ratio: 0.4,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 120,
          session_count: 4,
          progress_state: 'on_track',
          goal: {
            goal_type: 'sessions',
            target_value: 10,
            current_value: 4,
            progress_ratio: 0.4,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    vi.mocked(skillsApi.forecast).mockResolvedValue({
      ok: true,
      forecast: {
        skill_id: 1,
        horizon_days: 7,
        forecast_state: 'on_track',
        risk_reason: null,
        goal: {
          goal_type: 'sessions',
          target_value: 10,
          current_value: 4,
          progress_ratio: 0.4,
          deadline: null,
        },
        baseline: {
          avg_daily_minutes_last_14: 2,
          sessions_last_14: 1,
          total_minutes_last_14: 28,
        },
        projection: {
          projected_minutes_next_window: 14,
          projected_sessions_next_window: 1,
          projected_goal_progress_ratio: 0.6,
        },
      },
    })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for piano/i }))

    await user.click(await screen.findByRole('button', { name: /\+30 minutes/i }))

    expect(await screen.findByText(/projected 44m and 2 sessions\./i)).toBeInTheDocument()
  })

  it('shows needs-attention strip and opens insights from that strip', async () => {
    vi.mocked(skillsApi.list).mockResolvedValue({
      ok: true,
      skills: [
        {
          id: 1,
          name: 'Writing',
          category: 'Communication',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 80,
          session_count: 3,
          last_practiced_at: null,
          streak_days: 0,
          sessions_last_7: 0,
          sessions_last_30: 3,
          recent_sessions: [],
        },
        {
          id: 2,
          name: 'Piano',
          category: 'Music',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 120,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 2,
          sessions_last_7: 3,
          sessions_last_30: 4,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 3.3, total_sessions: 7, at_risk: 1, active: 2 },
      groups: {
        at_risk: [
          {
            skill_id: 1,
            name: 'Writing',
            category: 'Communication',
            total_minutes: 80,
            session_count: 3,
            progress_state: 'at_risk',
            goal: {
              goal_type: 'sessions',
              target_value: 10,
              current_value: 3,
              progress_ratio: 0.3,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
            risk_reason: 'no_recent_sessions',
          },
        ],
        on_track: [
          {
            skill_id: 2,
            name: 'Piano',
            category: 'Music',
            total_minutes: 120,
            session_count: 4,
            progress_state: 'on_track',
            goal: null,
            primary_action: 'continue_practice',
            requires_goal_setup: false,
            risk_reason: null,
          },
        ],
        completed: [],
      },
      skills: [
        {
          skill_id: 1,
          name: 'Writing',
          category: 'Communication',
          total_minutes: 80,
          session_count: 3,
          progress_state: 'at_risk',
          goal: {
            goal_type: 'sessions',
            target_value: 10,
            current_value: 3,
            progress_ratio: 0.3,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: 'no_recent_sessions',
        },
        {
          skill_id: 2,
          name: 'Piano',
          category: 'Music',
          total_minutes: 120,
          session_count: 4,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()

    expect(await screen.findByText(/needs attention/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /writing: stalled/i }))
    expect(await screen.findByText(/insights - writing/i)).toBeInTheDocument()
  })

  it('keeps compact density by default and shows more secondary metrics in comfortable mode', async () => {
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
          total_minutes: 120,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 2,
          sessions_last_7: 3,
          sessions_last_30: 4,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 2, total_sessions: 4, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 120,
            session_count: 4,
            progress_state: 'on_track',
            goal: null,
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 120,
          session_count: 4,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()

    await screen.findByRole('button', { name: /open details for piano/i })
    expect(screen.queryByText(/in last 7d/i)).not.toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /^comfortable$/i }))
    expect(await screen.findByText(/3 in last 7d/i)).toBeInTheDocument()
  })

  it('renders now-next-risk framing with concise deterministic summaries', async () => {
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
          total_minutes: 120,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 2,
          sessions_last_7: 3,
          sessions_last_30: 4,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 2, total_sessions: 4, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 120,
            session_count: 4,
            progress_state: 'on_track',
            goal: {
              goal_type: 'sessions',
              target_value: 10,
              current_value: 4,
              progress_ratio: 0.4,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 120,
          session_count: 4,
          progress_state: 'on_track',
          goal: {
            goal_type: 'sessions',
            target_value: 10,
            current_value: 4,
            progress_ratio: 0.4,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()

    expect(await screen.findByText(/^now$/i)).toBeInTheDocument()
    expect(await screen.findByText(/^next$/i)).toBeInTheDocument()
    expect(await screen.findByText(/40% of goal reached\./i)).toBeInTheDocument()
    expect(screen.queryByText(/^risk$/i)).not.toBeInTheDocument()
  })

  it('supports alphabetical sorting mode for skill cards', async () => {
    vi.mocked(skillsApi.list).mockResolvedValue({
      ok: true,
      skills: [
        {
          id: 1,
          name: 'Zebra Practice',
          category: 'Music',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 80,
          session_count: 3,
          last_practiced_at: null,
          streak_days: 0,
          sessions_last_7: 0,
          sessions_last_30: 3,
          recent_sessions: [],
        },
        {
          id: 2,
          name: 'Alpha Practice',
          category: 'Writing',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 100,
          session_count: 5,
          last_practiced_at: null,
          streak_days: 2,
          sessions_last_7: 3,
          sessions_last_30: 5,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 3, total_sessions: 8, at_risk: 1, active: 2 },
      groups: {
        at_risk: [
          {
            skill_id: 1,
            name: 'Zebra Practice',
            category: 'Music',
            total_minutes: 80,
            session_count: 3,
            progress_state: 'at_risk',
            goal: null,
            primary_action: 'continue_practice',
            requires_goal_setup: false,
            risk_reason: 'no_recent_sessions',
          },
        ],
        on_track: [
          {
            skill_id: 2,
            name: 'Alpha Practice',
            category: 'Writing',
            total_minutes: 100,
            session_count: 5,
            progress_state: 'on_track',
            goal: null,
            primary_action: 'continue_practice',
            requires_goal_setup: false,
            risk_reason: null,
          },
        ],
        completed: [],
      },
      skills: [
        {
          skill_id: 1,
          name: 'Zebra Practice',
          category: 'Music',
          total_minutes: 80,
          session_count: 3,
          progress_state: 'at_risk',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: 'no_recent_sessions',
        },
        {
          skill_id: 2,
          name: 'Alpha Practice',
          category: 'Writing',
          total_minutes: 100,
          session_count: 5,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()

    await screen.findByRole('button', { name: /open details for zebra practice/i })
    await user.selectOptions(screen.getByLabelText(/sort/i), 'alphabetical')

    const openButtons = screen.getAllByRole('button', { name: /open details for/i })
    expect(openButtons[0]).toHaveAttribute('aria-label', 'Open details for Alpha Practice')
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
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for piano/i }))

    expect(await screen.findByText(/this goal type is qualitative, so we show activity guidance without numeric projection\./i)).toBeInTheDocument()
  })

  it('renders weekly cadence strip and on-track next-action narrative', async () => {
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
          total_minutes: 240,
          session_count: 8,
          last_practiced_at: null,
          streak_days: 2,
          sessions_last_7: 5,
          sessions_last_30: 8,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 4, total_sessions: 8, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 240,
            session_count: 8,
            progress_state: 'on_track',
            goal: {
              goal_type: 'sessions',
              target_value: 12,
              current_value: 8,
              progress_ratio: 0.66,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 240,
          session_count: 8,
          progress_state: 'on_track',
          goal: {
            goal_type: 'sessions',
            target_value: 12,
            current_value: 8,
            progress_ratio: 0.66,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()

    await userEvent.setup().click(await screen.findByRole('button', { name: /open details for piano/i }))

    expect(await screen.findByText(/weekly cadence/i)).toBeInTheDocument()
    expect((await screen.findAllByLabelText(/weekly cadence for piano/i)).length).toBeGreaterThan(0)
    expect(await screen.findByText(/next action: continue practice to sustain this weekly rhythm\./i)).toBeInTheDocument()
  })

  it('renders at-risk recovery next-action narrative deterministically', async () => {
    vi.mocked(skillsApi.list).mockResolvedValue({
      ok: true,
      skills: [
        {
          id: 1,
          name: 'Writing',
          category: 'Communication',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 60,
          session_count: 2,
          last_practiced_at: null,
          streak_days: 0,
          sessions_last_7: 0,
          sessions_last_30: 2,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 1, total_sessions: 2, at_risk: 1, active: 1 },
      groups: {
        at_risk: [
          {
            skill_id: 1,
            name: 'Writing',
            category: 'Communication',
            total_minutes: 60,
            session_count: 2,
            progress_state: 'at_risk',
            goal: {
              goal_type: 'sessions',
              target_value: 8,
              current_value: 2,
              progress_ratio: 0.25,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
            risk_reason: 'no_recent_sessions',
          },
        ],
        on_track: [],
        completed: [],
      },
      skills: [
        {
          skill_id: 1,
          name: 'Writing',
          category: 'Communication',
          total_minutes: 60,
          session_count: 2,
          progress_state: 'at_risk',
          goal: {
            goal_type: 'sessions',
            target_value: 8,
            current_value: 2,
            progress_ratio: 0.25,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: 'no_recent_sessions',
        },
      ],
    })

    renderPage()

    expect(await screen.findByText(/next action: log a short session today to recover momentum\./i)).toBeInTheDocument()
  })

  it('prefills suggested duration in continue-practice modal from recent rhythm', async () => {
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
          total_minutes: 180,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 4,
          recent_sessions: [
            { id: 1, skill_id: 1, duration_minutes: 40, intensity: null, step_id: null, notes: null, practiced_at: new Date().toISOString() },
            { id: 2, skill_id: 1, duration_minutes: 35, intensity: null, step_id: null, notes: null, practiced_at: new Date().toISOString() },
            { id: 3, skill_id: 1, duration_minutes: 45, intensity: null, step_id: null, notes: null, practiced_at: new Date().toISOString() },
          ],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 3, total_sessions: 4, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 180,
            session_count: 4,
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
          total_minutes: 180,
          session_count: 4,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: true,
          risk_reason: null,
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /continue practice/i }))

    expect(await screen.findByText(/pacing cue/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/duration/i)).toHaveValue(40)
  })

  it('supports step chips and shows post-submit micro-celebration', async () => {
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
          total_minutes: 90,
          session_count: 3,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 3,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 1.5, total_sessions: 3, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 90,
            session_count: 3,
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
          total_minutes: 90,
          session_count: 3,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: true,
          risk_reason: null,
        },
      ],
    })

    vi.mocked(skillsApi.path).mockResolvedValue({
      ok: true,
      path: {
        skill_id: 1,
        progress_state: 'on_track',
        risk_reason: null,
        goal: null,
        steps: [
          { step_id: 'continue_practice', label: 'Continue Practice', status: 'recommended', action: 'continue_practice' },
          { step_id: 'review_goal', label: 'Review Goal', status: 'ready', action: 'review_goal' },
        ],
        next_recommended_step: { step_id: 'continue_practice', label: 'Continue Practice', status: 'recommended', action: 'continue_practice' },
      },
    })

    vi.mocked(skillsApi.logPractice).mockResolvedValue({
      ok: true,
      session: {
        id: 10,
        skill_id: 1,
        duration_minutes: 30,
        intensity: null,
        step_id: 2,
        notes: null,
        practiced_at: new Date().toISOString(),
      },
      next_recommended_step: {
        step_id: 'review_goal',
        label: 'Review Goal',
        status: 'ready',
        action: 'review_goal',
      },
    })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /continue practice/i }))
    await user.click(await screen.findByRole('button', { name: /review goal/i }))
    await user.clear(screen.getByLabelText(/duration/i))
    await user.type(screen.getByLabelText(/duration/i), '30')
    const continueButtons = screen.getAllByRole('button', { name: /continue practice/i })
    await user.click(continueButtons[continueButtons.length - 1])

    await waitFor(() => {
      expect(skillsApi.logPractice).toHaveBeenCalledTimes(1)
    })

    const logPayload = vi.mocked(skillsApi.logPractice).mock.calls[0][1]
    expect(logPayload.duration_minutes).toBe(30)
    expect(logPayload.step_id).toBe(2)

    expect(await screen.findByText(/session saved/i)).toBeInTheDocument()
    expect(await screen.findByText(/\+30 min, \+1 session, streak delta \+1\./i)).toBeInTheDocument()
    expect(await screen.findByText(/next up: review goal/i)).toBeInTheDocument()
  })

  it('renders deterministic goal insights in edit-goal modal', async () => {
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
          total_minutes: 180,
          session_count: 6,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 3,
          sessions_last_30: 6,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 3, total_sessions: 6, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 180,
            session_count: 6,
            progress_state: 'on_track',
            goal: {
              goal_type: 'sessions',
              target_value: 12,
              current_value: 6,
              progress_ratio: 0.5,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 180,
          session_count: 6,
          progress_state: 'on_track',
          goal: {
            goal_type: 'sessions',
            target_value: 12,
            current_value: 6,
            progress_ratio: 0.5,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for piano/i }))
    await user.click(await screen.findByRole('button', { name: /edit goal/i }))

    expect(await screen.findByText(/goal snapshot/i)).toBeInTheDocument()
    expect(await screen.findByText(/pace: 3 sessions\/week/i)).toBeInTheDocument()
    expect(await screen.findByText(/eta:/i)).toBeInTheDocument()
  })

  it('renders hour units and milestone qualitative guidance in goal snapshot', async () => {
    vi.mocked(skillsApi.list).mockResolvedValue({
      ok: true,
      skills: [
        {
          id: 1,
          name: 'Strength Training',
          category: 'Fitness',
          difficulty: null,
          target_level: null,
          current_level: null,
          description: null,
          tags: [],
          total_minutes: 850,
          session_count: 10,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 3,
          sessions_last_30: 10,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 14.2, total_sessions: 10, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Strength Training',
            category: 'Fitness',
            total_minutes: 850,
            session_count: 10,
            progress_state: 'on_track',
            goal: {
              goal_type: 'hours',
              target_value: 60,
              current_value: 14.4166666667,
              progress_ratio: 0.24,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
            risk_reason: null,
          },
        ],
        completed: [],
      },
      skills: [
        {
          skill_id: 1,
          name: 'Strength Training',
          category: 'Fitness',
          total_minutes: 850,
          session_count: 10,
          progress_state: 'on_track',
          goal: {
            goal_type: 'hours',
            target_value: 60,
            current_value: 14.4166666667,
            progress_ratio: 0.24,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for strength training/i }))
    await user.click(await screen.findByRole('button', { name: /edit goal/i }))
    expect(await screen.findByText(/14.4h done so far, targeting 60h total\./i)).toBeInTheDocument()
    expect(await screen.findByText(/pace: .*h\/week/i)).toBeInTheDocument()

    await user.click(screen.getByRole('button', { name: /milestones/i }))
    expect(await screen.findByText(/milestone goals are qualitative/i)).toBeInTheDocument()
  })

  it('applies goal quick actions for target and timeline in edit-goal modal', async () => {
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
          total_minutes: 120,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 4,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 2, total_sessions: 4, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 120,
            session_count: 4,
            progress_state: 'on_track',
            goal: {
              goal_type: 'sessions',
              target_value: 10,
              current_value: 4,
              progress_ratio: 0.4,
              deadline: null,
            },
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 120,
          session_count: 4,
          progress_state: 'on_track',
          goal: {
            goal_type: 'sessions',
            target_value: 10,
            current_value: 4,
            progress_ratio: 0.4,
            deadline: null,
          },
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for piano/i }))
    await user.click(await screen.findByRole('button', { name: /edit goal/i }))

    expect(screen.getByLabelText(/target value/i)).toHaveValue(10)
    expect(screen.getByLabelText(/deadline/i)).toHaveValue('')

    await user.click(screen.getByRole('button', { name: /raise target \+10%/i }))
    expect(screen.getByLabelText(/target value/i)).toHaveValue(11)

    await user.click(screen.getByRole('button', { name: /extend timeline \+14d/i }))
    expect(screen.getByLabelText(/deadline/i)).not.toHaveValue('')
  })

  it('shows delete confirmation before removing a skill', async () => {
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
          total_minutes: 120,
          session_count: 4,
          last_practiced_at: null,
          streak_days: 1,
          sessions_last_7: 2,
          sessions_last_30: 4,
          recent_sessions: [],
        },
      ],
    })

    vi.mocked(skillsApi.overview).mockResolvedValue({
      ok: true,
      summary: { total_hours: 2, total_sessions: 4, at_risk: 0, active: 1 },
      groups: {
        at_risk: [],
        on_track: [
          {
            skill_id: 1,
            name: 'Piano',
            category: 'Music',
            total_minutes: 120,
            session_count: 4,
            progress_state: 'on_track',
            goal: null,
            primary_action: 'continue_practice',
            requires_goal_setup: false,
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
          total_minutes: 120,
          session_count: 4,
          progress_state: 'on_track',
          goal: null,
          primary_action: 'continue_practice',
          requires_goal_setup: false,
          risk_reason: null,
        },
      ],
    })

    vi.mocked(skillsApi.delete).mockResolvedValue({ ok: true })

    renderPage()
    const user = userEvent.setup()

    await user.click(await screen.findByRole('button', { name: /open details for piano/i }))
    await user.click(await screen.findByRole('button', { name: /^delete$/i }))

    expect(await screen.findByText(/delete skill\?/i)).toBeInTheDocument()
    expect(skillsApi.delete).not.toHaveBeenCalled()

    const deleteButtons = screen.getAllByRole('button', { name: /^delete$/i })
    await user.click(deleteButtons[deleteButtons.length - 1])

    await waitFor(() => {
      expect(skillsApi.delete).toHaveBeenCalledTimes(1)
      expect(skillsApi.delete).toHaveBeenCalledWith(1)
    })
  })
})
