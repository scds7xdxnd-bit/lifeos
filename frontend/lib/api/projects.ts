import { apiFetch, apiGet, apiPost } from './client'

export interface Project {
  id: number
  name: string
  description: string | null
  status: string
  target_date: string | null
  created_at: string
  updated_at: string | null
}

export interface Task {
  id: number
  title: string
  status: string
  due_date: string | null
  priority: number | null
  notes: string | null
  created_at: string
  updated_at: string | null
}

export interface CreateProjectInput {
  name: string
  description?: string | null
  target_date?: string | null
}

export interface CreateTaskInput {
  title: string
  due_date?: string | null
  priority?: number | null
  notes?: string | null
}

interface ProjectListResponse {
  ok: boolean
  items: Project[]
  page: number
  pages: number
  total: number
}
interface ProjectResponse { ok: boolean; project: Project }
interface TaskListResponse { ok: boolean; items: Task[]; page: number; pages: number; total: number }
interface TaskResponse { ok: boolean; task: Task }

export const projectsApi = {
  list: (page = 1, perPage = 50) =>
    apiGet<ProjectListResponse>(`/api/projects?page=${page}&per_page=${perPage}`),

  get: (id: number) => apiGet<ProjectResponse>(`/api/projects/${id}`),

  create: (data: CreateProjectInput) =>
    apiPost<ProjectResponse>('/api/projects', data),

  update: (id: number, data: Partial<CreateProjectInput & { status: string }>) =>
    apiFetch<ProjectResponse>(`/api/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  complete: (id: number) =>
    apiPost<ProjectResponse>(`/api/projects/${id}/complete`, {}),

  archive: (id: number) =>
    apiPost<ProjectResponse>(`/api/projects/${id}/archive`, {}),

  delete: (id: number) =>
    apiFetch<{ ok: boolean }>(`/api/projects/${id}`, { method: 'DELETE' }),

  listTasks: (projectId: number, page = 1) =>
    apiGet<TaskListResponse>(`/api/projects/${projectId}/tasks?page=${page}`),

  createTask: (projectId: number, data: CreateTaskInput) =>
    apiPost<TaskResponse>(`/api/projects/${projectId}/tasks`, data),

  updateTask: (taskId: number, data: Partial<CreateTaskInput & { status: string }>) =>
    apiFetch<TaskResponse>(`/api/projects/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  completeTask: (taskId: number) =>
    apiPost<TaskResponse>(`/api/projects/tasks/${taskId}/complete`, {}),

  deleteTask: (taskId: number) =>
    apiFetch<{ ok: boolean }>(`/api/projects/tasks/${taskId}`, { method: 'DELETE' }),
}
