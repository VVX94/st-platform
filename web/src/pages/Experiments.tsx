import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Experiment {
  experiment_id: string;
  name: string;
  task_type: string;
  status: string;
  run_count: number;
}

export default function Experiments() {
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    api
      .get<Experiment[]>("/api/experiments")
      .then(setExperiments)
      .catch((e) => setError(String(e)));
  }, []);

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
      {error && <div style={{ color: "red" }}>{error}</div>}
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
            </tr>
          </thead>
          <tbody>
            {experiments.map((e) => (
              <tr key={e.experiment_id}>
                <td style={td}>{e.experiment_id.slice(0, 8)}...</td>
                <td style={td}>{e.name}</td>
                <td style={td}>{e.task_type}</td>
                <td style={td}>{e.status}</td>
                <td style={td}>{e.run_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
