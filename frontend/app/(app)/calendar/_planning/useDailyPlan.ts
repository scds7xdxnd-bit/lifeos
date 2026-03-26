import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { calendarApi } from '@/lib/api/calendar'
import { habitsApi } from '@/lib/api/habits'
import { skillsApi } from '@/lib/api/skills'
import { generateDailyPlan, type DailyPlan } from './planning-engine'

export function useDailyPlan(selectedDate: Date) {
  const { data: calendarData, isLoading: calLoading } = useQuery({
    queryKey: ['calendar-events'],
    queryFn: () => calendarApi.list(200),
  })

  const { data: habitsData, isLoading: habLoading } = useQuery({
    queryKey: ['habits'],
    queryFn: () => habitsApi.list(),
  })

  const { data: skillsData, isLoading: skLoading } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsApi.list(),
  })

  const isLoading = calLoading || habLoading || skLoading

  const plan: DailyPlan | null = useMemo(() => {
    if (!calendarData || !habitsData || !skillsData) return null

    const events = calendarData.events ?? []
    const habits = habitsData.habits ?? []
    const skills = skillsData.skills ?? []

    return generateDailyPlan(events, habits, skills, selectedDate)
  }, [calendarData, habitsData, skillsData, selectedDate])

  return { plan, isLoading }
}
