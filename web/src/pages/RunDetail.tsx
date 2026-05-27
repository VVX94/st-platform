import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, type Run, type Metric, type Artifact } from "../api/client";

function statusBadge(status: string): React.CSSProperties {
  const colors: Record<string, string> = {
    queued: "#6c757d",
    running: "#0d6efd",
    succeeded: "#198754",
    failed: "#dc3545",
  };
  return {
    display: "inline-block",
    padding: "0.15rem 0.5rem",
    borderRadius: "4px",
    fontSize: "0.8rem",
    fontWeight: 600,
    color: "#fff",
    backgroundColor: colors[status] || "#6c757d",
  };
}

export default function RunDetail() {
  const { runId } = useParams<{ runId: string }>();
  const [run, setRun] = useState<Run | null>(null);
  const [metrics, setMetrics] = useState<Metric[]>([]);
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (!runId) return;
    api
      .get<Run>(`/api/runs/${runId}`)
      .then(setRun)
      .catch((e) => setError(String(e)));
    api
      .getRunMetrics(runId)
      .then(setMetrics)
      .catch(() => {});
    api
      .getRunArtifacts(runId)
      .then(setArtifacts)
      .catch(() => {});
  }, [runId]);

  if (error) {
    return (
      <div>
        <h1>Run Detail</h1>
        <p style={{ color: "red" }}>{error}</p>
        <Link to="/experiments">Back to Experiments</Link>
      </div>
    );
  }

  if (!run) {
    return <p>Loading...</p>;
  }

  const th: React.CSSProperties = {
    textAlign: "left",
    padding: "0.5rem 1rem",
    borderBottom: "2px solid #ddd",
  };
  const td: React.CSSProperties = {
    padding: "0.5rem 1rem",
    borderBottom: "1px solid #eee",
  };
  const labelStyle: React.CSSProperties = {
    fontWeight: 600,
    padding: "0.25rem 0",
    color: "#555",
  };

  return (
    <div>
      <Link to="/experiments" style={{ color: "#0d6efd", textDecoration: "none" }}>
        &larr; Back to Experiments
      </Link>
      <h1 style={{ marginTop: "0.5rem" }}>Run Detail</h1>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginTop: "1rem" }}>
        <div>
          <div style={labelStyle}>Run ID</div>
          <div>{run.run_id}</div>
        </div>
        <div>
          <div style={labelStyle}>Algorithm</div>
          <div>{run.algorithm_id}</div>
        </div>
        <div>
          <div style={labelStyle}>Task Type</div>
          <div>{run.task_type}</div>
        </div>
        <div>
          <div style={labelStyle}>Status</div>
          <div>
            <span style={statusBadge(run.status)}>{run.status}</span>
          </div>
        </div>
        <div>
          <div style={labelStyle}>Started At</div>
          <div>{run.started_at ? new Date(run.started_at).toLocaleString() : "-"}</div>
        </div>
        <div>
          <div style={labelStyle}>Finished At</div>
          <div>{run.finished_at ? new Date(run.finished_at).toLocaleString() : "-"}</div>
        </div>
      </div>

      {run.error && (
        <div style={{ marginTop: "1.5rem" }}>
          <h3 style={{ color: "#dc3545" }}>Error</h3>
          <pre style={{ backgroundColor: "#f8d7da", padding: "1rem", borderRadius: "4px", overflow: "auto" }}>
            {run.error}
          </pre>
        </div>
      )}

      {metrics.length > 0 && (
        <div style={{ marginTop: "1.5rem" }}>
          <h2>Metrics</h2>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}>
            <thead>
              <tr>
                <th style={th}>Metric</th>
                <th style={th}>Value</th>
              </tr>
            </thead>
            <tbody>
              {metrics.map((m) => (
                <tr key={m.metric_id}>
                  <td style={td}>{m.name}</td>
                  <td style={td}>{m.value.toFixed(4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {artifacts.length > 0 && (
        <div style={{ marginTop: "1.5rem" }}>
          <h2>Artifacts</h2>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}>
            <thead>
              <tr>
                <th style={th}>Kind</th>
                <th style={th}>URI</th>
                <th style={th}>Description</th>
              </tr>
            </thead>
            <tbody>
              {artifacts.map((a) => (
                <tr key={a.artifact_id}>
                  <td style={td}>{a.kind}</td>
                  <td style={td}>{a.uri}</td>
                  <td style={td}>{a.description}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
