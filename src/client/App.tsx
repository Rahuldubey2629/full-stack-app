import { useEffect, useMemo, useState } from "react";

import {
  createTask,
  deleteTask,
  fetchConfig,
  fetchTasks,
  type AppConfig,
  type Task,
  type TaskStatus,
  type TaskSummary,
  updateTask
} from "./api";

type TaskFormState = {
  title: string;
  owner: string;
  status: TaskStatus;
  dueDate: string;
  notes: string;
};

const initialFormState: TaskFormState = {
  title: "",
  owner: "",
  status: "new",
  dueDate: "",
  notes: ""
};

const statusOrder: TaskStatus[] = ["new", "in_progress", "blocked", "done"];

const statusLabels: Record<TaskStatus, string> = {
  new: "New",
  in_progress: "In progress",
  blocked: "Blocked",
  done: "Done"
};

const statusHints: Record<TaskStatus, string> = {
  new: "Ready to plan",
  in_progress: "Actively moving",
  blocked: "Needs attention",
  done: "Completed"
};

function nextStatus(current: TaskStatus): TaskStatus {
  const index = statusOrder.indexOf(current);
  return statusOrder[(index + 1) % statusOrder.length];
}

function formatDate(dateValue: string) {
  if (!dateValue) {
    return "No due date";
  }

  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric"
  }).format(new Date(dateValue));
}

function MetricCard({ label, value, detail }: { label: string; value: string | number; detail: string }) {
  return (
    <div className="metric-card">
      <span className="metric-label">{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </div>
  );
}

function TaskCard({
  task,
  onAdvance,
  onDelete,
  busy
}: {
  task: Task;
  onAdvance: (task: Task) => void;
  onDelete: (task: Task) => void;
  busy: boolean;
}) {
  const statusClass = `status-pill status-${task.status}`;

  return (
    <article className="task-card">
      <div className="task-card-header">
        <div>
          <p className="task-owner">{task.owner}</p>
          <h3>{task.title}</h3>
        </div>
        <span className={statusClass}>{statusLabels[task.status]}</span>
      </div>
      <p className="task-notes">{task.notes || statusHints[task.status]}</p>
      <div className="task-meta">
        <span>Due {formatDate(task.dueDate)}</span>
        <span>Updated {formatDate(task.updatedAt)}</span>
      </div>
      <div className="task-actions">
        <button type="button" className="button ghost" onClick={() => onAdvance(task)} disabled={busy}>
          Move to {statusLabels[nextStatus(task.status)]}
        </button>
        <button type="button" className="button danger" onClick={() => onDelete(task)} disabled={busy}>
          Delete
        </button>
      </div>
    </article>
  );
}

export function App() {
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [summary, setSummary] = useState<TaskSummary>({ total: 0, done: 0, blocked: 0, inProgress: 0, new: 0 });
  const [form, setForm] = useState<TaskFormState>(initialFormState);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [actionTaskId, setActionTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>(new Date().toLocaleTimeString());

  async function refreshData() {
    try {
      setError(null);
      const [configResponse, tasksResponse] = await Promise.all([fetchConfig(), fetchTasks()]);
      setConfig(configResponse);
      setTasks(tasksResponse.tasks);
      setSummary(tasksResponse.summary);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Something went wrong while loading the app.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refreshData();
  }, []);

  const completionRate = useMemo(() => {
    if (summary.total === 0) {
      return 0;
    }

    return Math.round((summary.done / summary.total) * 100);
  }, [summary.done, summary.total]);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);

    try {
      await createTask(form);
      setForm(initialFormState);
      await refreshData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to create a task.");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleAdvance(task: Task) {
    setActionTaskId(task.id);

    try {
      await updateTask(task.id, { status: nextStatus(task.status) });
      await refreshData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to update the task.");
    } finally {
      setActionTaskId(null);
    }
  }

  async function handleDelete(task: Task) {
    const confirmed = window.confirm(`Delete task \"${task.title}\"?`);

    if (!confirmed) {
      return;
    }

    setActionTaskId(task.id);

    try {
      await deleteTask(task.id);
      await refreshData();
    } catch (caughtError) {
      setError(caughtError instanceof Error ? caughtError.message : "Failed to delete the task.");
    } finally {
      setActionTaskId(null);
    }
  }

  return (
    <div className="page-shell">
      <div className="backdrop backdrop-one" />
      <div className="backdrop backdrop-two" />
      <main className="workspace">
        <section className="hero panel">
          <div className="hero-copy">
            <p className="eyebrow">Azure learning lab</p>
            <h1>{config?.appName ?? "Azure Learning Lab"}</h1>
            <p className="hero-text">
              Learn Azure by deploying a real full stack app, then front it with App Service, APIM, Key Vault references,
              and Azure DevOps pipelines.
            </p>
            <div className="hero-tags">
              <span>App Service</span>
              <span>APIM</span>
              <span>Key Vault</span>
              <span>Azure DevOps</span>
            </div>
          </div>
          <div className="hero-sidecard">
            <span className="eyebrow">Live signals</span>
            <strong>{config?.environment ?? "development"}</strong>
            <p>{config?.message ?? "Practical Azure demo for deployment practice."}</p>
            <div className="signal-list">
              <div>
                <span>OpenAPI</span>
                <strong>/openapi.json</strong>
              </div>
              <div>
                <span>Health</span>
                <strong>/health/live</strong>
              </div>
              <div>
                <span>Secrets</span>
                <strong>{config?.hasSecretConfigured ? "Configured" : "Not configured yet"}</strong>
              </div>
            </div>
          </div>
        </section>

        <section className="metrics-grid">
          <MetricCard label="Tasks" value={summary.total} detail="Total backlog items in the learning app." />
          <MetricCard label="Done" value={summary.done} detail={`${completionRate}% completion across the board.`} />
          <MetricCard label="In progress" value={summary.inProgress} detail="Items currently being worked on." />
          <MetricCard label="Blocked" value={summary.blocked} detail="Items that need a decision or dependency." />
        </section>

        <section className="content-grid">
          <article className="panel form-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Create task</p>
                <h2>Capture the next Azure experiment</h2>
              </div>
              <span className="timestamp">Synced {lastUpdated}</span>
            </div>

            <form className="task-form" onSubmit={handleSubmit}>
              <label>
                Title
                <input
                  value={form.title}
                  onChange={(event) => setForm({ ...form, title: event.target.value })}
                  placeholder="Deploy the API behind APIM"
                  required
                  maxLength={120}
                />
              </label>
              <label>
                Owner
                <input
                  value={form.owner}
                  onChange={(event) => setForm({ ...form, owner: event.target.value })}
                  placeholder="Platform team"
                  required
                  maxLength={80}
                />
              </label>
              <label>
                Status
                <select value={form.status} onChange={(event) => setForm({ ...form, status: event.target.value as TaskStatus })}>
                  {statusOrder.map((status) => (
                    <option key={status} value={status}>
                      {statusLabels[status]}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Due date
                <input type="date" value={form.dueDate} onChange={(event) => setForm({ ...form, dueDate: event.target.value })} />
              </label>
              <label className="wide">
                Notes
                <textarea
                  value={form.notes}
                  onChange={(event) => setForm({ ...form, notes: event.target.value })}
                  placeholder="What should I validate in Azure next?"
                  rows={4}
                  maxLength={500}
                />
              </label>
              <div className="form-actions wide">
                <button type="submit" className="button primary" disabled={submitting}>
                  {submitting ? "Saving..." : "Add task"}
                </button>
                <button type="button" className="button ghost" onClick={() => setForm(initialFormState)} disabled={submitting}>
                  Reset form
                </button>
              </div>
            </form>
          </article>

          <article className="panel tasks-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Task board</p>
                <h2>Practice the deployment flow end to end</h2>
              </div>
              <span className="timestamp">{loading ? "Loading..." : `${tasks.length} items`}</span>
            </div>

            {error ? <div className="error-banner">{error}</div> : null}

            <div className="task-list">
              {tasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onAdvance={handleAdvance}
                  onDelete={handleDelete}
                  busy={actionTaskId === task.id}
                />
              ))}
              {!loading && tasks.length === 0 ? <p className="empty-state">No tasks yet. Add one to start exploring the flow.</p> : null}
            </div>
          </article>
        </section>
      </main>
    </div>
  );
}
