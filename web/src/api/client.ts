const BASE = "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`API ${resp.status}: ${text}`);
  }
  return resp.json() as Promise<T>;
}

export interface Run {
  run_id: string;
  experiment_id: string | null;
  algorithm_id: string;
  task_type: string;
  status: string;
  parameters: Record<string, unknown>;
  dataset: Record<string, unknown>;
  summary: Record<string, unknown>;
  metrics: Record<string, number>;
  artifacts: Array<Record<string, unknown>>;
  error: string | null;
  run_root: string | null;
  created_at: string | null;
  started_at: string | null;
  finished_at: string | null;
}

export interface Metric {
  metric_id: string;
  run_id: string;
  name: string;
  value: number;
  created_at: string | null;
}

export interface Artifact {
  artifact_id: string;
  run_id: string;
  kind: string;
  uri: string;
  description: string;
  metadata: Record<string, unknown>;
  created_at: string | null;
}

export interface WorkerPollResponse {
  processed: number;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    }),
  getRunMetrics: (runId: string) =>
    request<Metric[]>(`/api/runs/${runId}/metrics`),
  getRunArtifacts: (runId: string) =>
    request<Artifact[]>(`/api/runs/${runId}/artifacts`),
  getExperimentRuns: (experimentId: string) =>
    request<Run[]>(`/api/experiments/${experimentId}/runs`),
  triggerWorkerPoll: () =>
    request<WorkerPollResponse>("/api/worker/poll", { method: "POST" }),
  registerDemoDataset: () =>
    request<unknown>("/api/datasets/register-demo", { method: "POST" }),
};
