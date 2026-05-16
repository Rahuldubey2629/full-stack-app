export type TaskStatus = "new" | "in_progress" | "blocked" | "done";

export type Task = {
  id: string;
  title: string;
  owner: string;
  status: TaskStatus;
  dueDate: string;
  notes: string;
  createdAt: string;
  updatedAt: string;
};

export type TaskSummary = {
  total: number;
  done: number;
  blocked: number;
  inProgress: number;
  new: number;
};

export type AppConfig = {
  appName: string;
  message: string;
  environment: string;
  hasSecretConfigured: boolean;
  apiVersion: string;
};

export type TasksResponse = {
  tasks: Task[];
  summary: TaskSummary;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";

function buildUrl(path: string) {
  return new URL(path, apiBaseUrl || window.location.origin).toString();
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(buildUrl(path), {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {})
    },
    ...init
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function fetchConfig() {
  return request<AppConfig>("/api/config");
}

export function fetchTasks() {
  return request<TasksResponse>("/api/tasks");
}

export function createTask(input: Omit<Task, "id" | "createdAt" | "updatedAt">) {
  return request<{ task: Task }>("/api/tasks", {
    method: "POST",
    body: JSON.stringify(input)
  });
}

export function updateTask(id: string, input: Partial<Omit<Task, "id" | "createdAt" | "updatedAt">>) {
  return request<{ task: Task }>(`/api/tasks/${id}`, {
    method: "PUT",
    body: JSON.stringify(input)
  });
}

export function deleteTask(id: string) {
  return request<void>(`/api/tasks/${id}`, {
    method: "DELETE"
  });
}
