import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Run } from "../api/client";

interface Health {
  status: string;
  version: string;
}

interface Algorithm {
  algorithm_id: string;
  name: string;
  task_type: string;
}

interface Dataset {
  dataset_id: string;
  name: string;
  platform: string;
}

interface Experiment {
  experiment_id: string;
  name: string;
  status: string;
  run_count: number;
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

export default function Dashboard() {
  const [health, setHealth] = useState<Health | null>(null);
  const [algoCount, setAlgoCount] = useState<number>(0);
  const [dsCount, setDsCount] = useState<number>(0);
  const [expCount, setExpCount] = useState<number>(0);
  const [runCount, setRunCount] = useState<number>(0);
  const [recentExps, setRecentExps] = useState<Experiment[]>([]);
  const [recentRuns, setRecentRuns] = useState<Run[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    api
      .get<Health>("/api/health")
      .then(setHealth)
      .catch((e) => setError(String(e)));

    api
      .get<Algorithm[]>("/api/algorithms")
      .then((data) => setAlgoCount(data.length))
      .catch(() => {});

    api
      .get<Dataset[]>("/api/datasets")
      .then((data) => setDsCount(data.length))
      .catch(() => {});

    api
      .get<Experiment[]>("/api/experiments")
      .then((data) => {
        setExpCount(data.length);
        setRecentExps(data.slice(0, 5));
      })
      .catch(() => {});

    api
      .get<Run[]>("/api/runs")
      .then((data) => {
        setRunCount(data.length);
        setRecentRuns(data.slice(0, 5));
      })
      .catch(() => {});
  }, []);

  const card: React.CSSProperties = {
    padding: "1.5rem",
    borderRadius: "8px",
    backgroundColor: "#f5f5f5",
    flex: "1",
    minWidth: "200px",
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
      <h1>Dashboard</h1>
      {error && (
        <div style={{ color: "red", marginBottom: "1rem" }}>
          API unreachable: {error}
        </div>
      )}

      {/* Summary cards */}
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: "1rem" }}>
        <div style={card}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>API Status</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
            {health ? health.status : "..."}
          </div>
          {health && (
            <div style={{ fontSize: "0.8rem", color: "#999" }}>v{health.version}</div>
          )}
        </div>
        <div style={card}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>Algorithms</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{algoCount}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>Datasets</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{dsCount}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>Experiments</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{expCount}</div>
        </div>
        <div style={card}>
          <div style={{ fontSize: "0.85rem", color: "#666" }}>Total Runs</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "bold" }}>{runCount}</div>
        </div>
      </div>

      {/* Recent experiments */}
      {recentExps.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Recent Experiments</h2>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}>
            <thead>
              <tr>
                <th style={th}>ID</th>
                <th style={th}>Name</th>
                <th style={th}>Status</th>
                <th style={th}>Runs</th>
                <th style={th}>Report</th>
              </tr>
            </thead>
            <tbody>
              {recentExps.map((e) => (
                <tr key={e.experiment_id}>
                  <td style={td}>{e.experiment_id.slice(0, 8)}...</td>
                  <td style={td}>{e.name}</td>
                  <td style={td}>
                    <span style={statusBadge(e.status)}>{e.status}</span>
                  </td>
                  <td style={td}>{e.run_count}</td>
                  <td style={td}>
                    <Link
                      to={`/reports/${e.experiment_id}`}
                      style={{ color: "#0d6efd" }}
                    >
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Recent runs */}
      {recentRuns.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Recent Runs</h2>
          <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}>
            <thead>
              <tr>
                <th style={th}>Run ID</th>
                <th style={th}>Algorithm</th>
                <th style={th}>Status</th>
                <th style={th}>Details</th>
              </tr>
            </thead>
            <tbody>
              {recentRuns.map((r) => (
                <tr key={r.run_id}>
                  <td style={td}>{r.run_id.slice(0, 12)}...</td>
                  <td style={td}>{r.algorithm_id}</td>
                  <td style={td}>
                    <span style={statusBadge(r.status)}>{r.status}</span>
                  </td>
                  <td style={td}>
                    <Link to={`/runs/${r.run_id}`} style={{ color: "#0d6efd" }}>
                      View
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
