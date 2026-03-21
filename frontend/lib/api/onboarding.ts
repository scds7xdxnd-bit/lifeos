import { apiPost } from './client'

export interface OnboardingStepPayload {
  step: 'domains' | 'calendar' | 'complete'
  data: Record<string, unknown>
}

interface OnboardingResponse {
  ok: boolean
  message?: string
}

export const onboardingApi = {
  submitStep: (payload: OnboardingStepPayload) =>
    apiPost<OnboardingResponse>('/api/users/me/onboarding', payload),
}
