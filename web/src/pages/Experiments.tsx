import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Run, type WorkerPollResponse } from "../api/client";

interface Experiment {
  experiment_id: string;
  name: string;
  task_type: string;
  status: string;
  run_count: number;
  dataset_id: string | null;
  created_at: string | null;
}

function statusBadge(status: string): React.CSSProperties {
  const colors: Record<string, string> = {
    queued: "#6c757d",
    running: "#0d6efd",
    succeeded: "#198754",
    failed: "#dc3545",
    created: "#6c757d",
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

export default function Experiments() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [error, setError] = useState<string>("");
  const [selectedExp, setSelectedExp] = useState<string | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [pollResult, setPollResult] = useState<string>("");

  const loadExperiments = () => {
    api
      .get<Experiment[]>("/api/experiments")
      .then(setExperiments)
      .catch((e) => setError(String(e)));
  };

  useEffect(() => {
    loadExperiments();
  }, []);

  const loadRuns = (expId: string) => {
    setSelectedExp(expId);
    api
      .getExperimentRuns(expId)
      .then(setRuns)
      .catch((e) => setError(String(e)));
  };

  const handlePoll = () => {
    api
      .triggerWorkerPoll()
      .then((r: WorkerPollResponse) => {
        setPollResult(`Processed ${r.processed} run(s)`);
        loadExperiments();
        if (selectedExp) loadRuns(selectedExp);
      })
      .catch((e) => setPollResult(`Error: ${String(e)}`));
  };

  const th: React.CSSProperties = {
    textAlign: "left",
    padding: "0.5rem 1rem",
    borderBottom: "2px solid #ddd",
  };
  const td: React.CSSProperties = {
    padding: "0.5rem 1rem",
    borderBottom: "1px solid #eee",
  };

  return (
    <div>
      <h1>Experiments</h1>
      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}

      <div style={{ marginBottom: "1rem" }}>
        <button
          onClick={handlePoll}
          style={{
            padding: "0.5rem 1rem",
            backgroundColor: "#198754",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          Run Worker
        </button>
        {pollResult && (
          <span style={{ marginLeft: "1rem", color: "#555" }}>{pollResult}</span>
        )}
      </div>

      {experiments.length === 0 && !error ? (
        <p>No experiments created yet.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
          <thead>
            <tr>
              <th style={th}>ID</th>
              <th style={th}>Name</th>
              <th style={th}>Task Type</th>
              <th style={th}>Status</th>
              <th style={th}>Runs</th>
              <th style={th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {experiments.map((e) => (
              <tr key={e.experiment_id} style={{ backgroundColor: selectedExp === e.experiment_id ? "#f0f8ff" : undefined }}>
                <td style={td}>{e.experiment_id.slice(0, 8)}...</td>
                <td style={td}>{e.name}</td>
                <td style={td}>{e.task_type}</td>
                <td style={td}>
                  <span style={statusBadge(e.status)}>{e.status}</span>
                </td>
                <td style={td}>{e.run_count}</td>
                <td style={td}>
                  <button
                    onClick={() => loadRuns(e.experiment_id)}
                    style={{
                      padding: "0.25rem 0.5rem",
                      backgroundColor: "#0d6efd",
                      color: "#fff",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "0.85rem",
                    }}
                  >
                    View Runs
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {selectedExp && runs.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Runs for Experiment {selectedExp.slice(0, 8)}...</h2>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}>
            <thead>
              <tr>
                <th style={th}>Run ID</th>
                <th style={th}>Algorithm</th>
                <th style={th}>Status</th>
                <th style={th}>Started</th>
                <th style={th}>Finished</th>
                <th style={th}>Details</th>
              </tr>
            </thead>
            <tbody>
              {runs.map((r) => (
                <tr key={r.run_id}>
                  <td style={td}>{r.run_id.slice(0, 12)}...</td>
                  <td style={td}>{r.algorithm_id}</td>
                  <td style={td}>
                    <span style={statusBadge(r.status)}>{r.status}</span>
                  </td>
                  <td style={td}>{r.started_at ? new Date(r.started_at).toLocaleTimeString() : "-"}</td>
                  <td style={td}>{r.finished_at ? new Date(r.finished_at).toLocaleTimeString() : "-"}</td>
                  <td style={td}>
                    <Link to={`/runs/${r.run_id}`} style={{ color: "#0d6efd" }}>
                      View Detail
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
