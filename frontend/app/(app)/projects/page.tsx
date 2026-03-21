'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projectsApi, type Project, type Task, type CreateProjectInput, type CreateTaskInput } from '@/lib/api/projects'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

function fmtDate(iso: string) {
  try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) } catch { return iso }
}

export default function ProjectsPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).projects
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [targetDate, setTargetDate] = useState('')

  const [activeProjectId, setActiveProjectId] = useState<number | null>(null)
  const [showTaskForm, setShowTaskForm] = useState(false)
  const [taskTitle, setTaskTitle] = useState('')
  const [taskNotes, setTaskNotes] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: () => projectsApi.list(),
  })

  const { data: tasksData } = useQuery({
    queryKey: ['project-tasks', activeProjectId],
    queryFn: () => projectsApi.listTasks(activeProjectId!),
    enabled: !!activeProjectId,
  })

  const createMut = useMutation({
    mutationFn: (input: CreateProjectInput) => projectsApi.create(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['projects'] })
      setShowForm(false)
      setName('')
      setDescription('')
      setTargetDate('')
    },
  })

  const completeMut = useMutation({
    mutationFn: (id: number) => projectsApi.complete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['projects'] }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => projectsApi.delete(id),
    onSuccess: (_data, deletedId) => {
      qc.invalidateQueries({ queryKey: ['projects'] })
      if (activeProjectId === deletedId) setActiveProjectId(null)
    },
  })

  const createTaskMut = useMutation({
    mutationFn: (input: CreateTaskInput) => projectsApi.createTask(activeProjectId!, input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['project-tasks', activeProjectId] })
      qc.invalidateQueries({ queryKey: ['projects'] })
      setShowTaskForm(false)
      setTaskTitle('')
      setTaskNotes('')
    },
  })

  const completeTaskMut = useMutation({
    mutationFn: (taskId: number) => projectsApi.completeTask(taskId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['project-tasks', activeProjectId] })
      qc.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  const projects = data?.items ?? []
  const tasks = tasksData?.items ?? []

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    createMut.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      target_date: targetDate || undefined,
    })
  }

  function handleCreateTask(e: React.FormEvent) {
    e.preventDefault()
    if (!taskTitle.trim()) return
    createTaskMut.mutate({
      title: taskTitle.trim(),
      notes: taskNotes.trim() || undefined,
    })
  }

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">{t.title}</h1>
          <p className="text-sm text-muted-foreground mt-1.5">{t.subtitle}</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? t.cancel : t.newProject}
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="glass rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-foreground">{t.createProject}</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="p-name">{t.name}</Label>
              <Input id="p-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder={t.namePlaceholder} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="p-date">{t.targetDate}</Label>
              <Input id="p-date" type="date" value={targetDate} onChange={(e) => setTargetDate(e.target.value)} />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="p-desc">{t.description}</Label>
            <Input id="p-desc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder={t.optional} />
          </div>
          <Button type="submit" disabled={createMut.isPending}>
            {createMut.isPending ? t.creating : t.createProject}
          </Button>
        </form>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_1fr] gap-6 items-start">
        {/* Projects list */}
        <div className="glass rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-foreground">{t.projects}</h2>
          {isLoading && <p className="text-sm text-muted-foreground">{t.loading}</p>}
          {!isLoading && projects.length === 0 && (
            <p className="text-sm text-muted-foreground">{t.noProjects}</p>
          )}
          {projects.length > 0 && (
            <ul className="space-y-2">
              {projects.map((p: Project) => (
                <li
                  key={p.id}
                  className={`rounded-xl px-4 py-3.5 transition-all cursor-pointer ${
                    activeProjectId === p.id ? 'bg-white/70 shadow-sm' : 'bg-white/30 hover:bg-white/50'
                  }`}
                  onClick={() => setActiveProjectId(activeProjectId === p.id ? null : p.id)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-foreground">{p.name}</p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        {p.status}
                        {p.target_date && ` · due ${fmtDate(p.target_date)}`}
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 shrink-0">
                      {p.status !== 'completed' && (
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); completeMut.mutate(p.id) }}
                          className="text-xs px-2.5 py-1 rounded-full bg-primary text-primary-foreground hover:bg-primary/85 transition-all"
                        >
                          {t.done}
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={(e) => { e.stopPropagation(); deleteMut.mutate(p.id) }}
                        className="text-xs px-2.5 py-1 rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all"
                      >
                        {t.delete}
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Tasks panel */}
        {activeProjectId && (
          <div className="glass rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="font-semibold text-foreground">{t.tasks}</h2>
              <Button size="sm" onClick={() => setShowTaskForm(!showTaskForm)}>
                {showTaskForm ? t.cancel : t.addTask}
              </Button>
            </div>

            {showTaskForm && (
              <form onSubmit={handleCreateTask} className="space-y-3 bg-white/30 rounded-xl p-4">
                <div className="space-y-2">
                  <Label htmlFor="t-title">{t.taskTitleLabel}</Label>
                  <Input id="t-title" required value={taskTitle} onChange={(e) => setTaskTitle(e.target.value)} placeholder={t.taskTitlePlaceholder} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="t-notes">{t.taskNotes}</Label>
                  <Input id="t-notes" value={taskNotes} onChange={(e) => setTaskNotes(e.target.value)} placeholder={t.optional} />
                </div>
                <Button type="submit" size="sm" disabled={createTaskMut.isPending}>
                  {createTaskMut.isPending ? t.adding : t.add}
                </Button>
              </form>
            )}

            {tasks.length === 0 && !showTaskForm && (
              <p className="text-sm text-muted-foreground">{t.noTasks}</p>
            )}
            {tasks.length > 0 && (
              <ul className="space-y-1.5">
                {tasks.map((task: Task) => (
                  <li key={task.id} className="rounded-lg bg-white/30 px-4 py-2.5 flex items-center justify-between gap-3">
                    <div className="min-w-0 flex-1">
                      <p className={`text-sm ${task.status === 'completed' ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                        {task.title}
                      </p>
                    </div>
                    {task.status !== 'completed' && (
                      <button
                        type="button"
                        onClick={() => completeTaskMut.mutate(task.id)}
                        className="text-xs px-2.5 py-1 rounded-full bg-white/50 text-foreground hover:bg-white/70 border border-white/40 transition-all"
                      >
                        {t.complete}
                      </button>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
