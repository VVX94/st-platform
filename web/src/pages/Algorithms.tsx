import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Algorithm {
  algorithm_id: string;
  name: string;
  task_type: string;
  runtime: string;
  version: string;
  description: string;
  tags: string[];
}

export default function Algorithms() {
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    api
      .get<Algorithm[]>("/api/algorithms")
      .then(setAlgorithms)
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
      <h1>Algorithms</h1>
      {error && <div style={{ color: "red" }}>{error}</div>}
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
        <thead>
          <tr>
            <th style={th}>ID</th>
            <th style={th}>Name</th>
            <th style={th}>Task Type</th>
            <th style={th}>Runtime</th>
            <th style={th}>Version</th>
          </tr>
        </thead>
        <tbody>
          {algorithms.map((a) => (
            <tr key={a.algorithm_id}>
              <td style={td}>{a.algorithm_id}</td>
              <td style={td}>{a.name}</td>
              <td style={td}>{a.task_type}</td>
              <td style={td}>{a.runtime}</td>
              <td style={td}>{a.version}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {algorithms.length === 0 && !error && <p>Loading...</p>}
    </div>
  );
}
