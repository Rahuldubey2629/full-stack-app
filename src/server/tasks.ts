import { randomUUID } from "node:crypto";
import { z } from "zod";

export const taskStatusSchema = z.enum(["new", "in_progress", "blocked", "done"]);

export const taskCreateSchema = z.object({
  title: z.string().trim().min(3).max(120),
  owner: z.string().trim().min(2).max(80),
  status: taskStatusSchema.default("new"),
  dueDate: z.string().trim().max(10).optional().default(""),
  notes: z.string().trim().max(500).optional().default("")
});

export const taskUpdateSchema = taskCreateSchema.partial();

export type TaskStatus = z.infer<typeof taskStatusSchema>;
export type TaskInput = z.infer<typeof taskCreateSchema>;

export type Task = TaskInput & {
  id: string;
  createdAt: string;
  updatedAt: string;
};

const seedTasks: Task[] = [
  {
    id: randomUUID(),
    title: "Wire App Service deployment",
    owner: "DevOps",
    status: "in_progress",
    dueDate: "",
    notes: "Package the app from Azure DevOps and deploy to Linux App Service.",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: randomUUID(),
    title: "Import the API into APIM",
    owner: "Platform",
    status: "new",
    dueDate: "",
    notes: "Use the generated OpenAPI document to create the APIM API.",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  },
  {
    id: randomUUID(),
    title: "Store secrets in Key Vault",
    owner: "Security",
    status: "blocked",
    dueDate: "",
    notes: "Map App Service settings to Key Vault references instead of plain text values.",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }
];

const tasks: Task[] = [...seedTasks];

export function listTasks(): Task[] {
  return [...tasks].sort((left, right) => right.updatedAt.localeCompare(left.updatedAt));
}

export function getTaskSummary() {
  const allTasks = listTasks();
  return {
    total: allTasks.length,
    done: allTasks.filter((task) => task.status === "done").length,
    blocked: allTasks.filter((task) => task.status === "blocked").length,
    inProgress: allTasks.filter((task) => task.status === "in_progress").length,
    new: allTasks.filter((task) => task.status === "new").length
  };
}

export function createTask(input: TaskInput): Task {
  const now = new Date().toISOString();
  const task: Task = {
    id: randomUUID(),
    createdAt: now,
    updatedAt: now,
    ...input
  };

  tasks.unshift(task);
  return task;
}

export function updateTask(id: string, input: Partial<TaskInput>): Task | null {
  const task = tasks.find((currentTask) => currentTask.id === id);

  if (!task) {
    return null;
  }

  Object.assign(task, input, { updatedAt: new Date().toISOString() });
  return task;
}

export function deleteTask(id: string): boolean {
  const taskIndex = tasks.findIndex((currentTask) => currentTask.id === id);

  if (taskIndex === -1) {
    return false;
  }

  tasks.splice(taskIndex, 1);
  return true;
}
