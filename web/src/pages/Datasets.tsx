import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Dataset {
  dataset_id: string;
  name: string;
  platform: string;
  sample_id: string;
  description: string;
}

export default function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    api
      .get<Dataset[]>("/api/datasets")
      .then(setDatasets)
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
      <h1>Datasets</h1>
      {error && <div style={{ color: "red" }}>{error}</div>}
      {datasets.length === 0 && !error ? (
        <p>No datasets registered yet.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
          <thead>
            <tr>
              <th style={th}>ID</th>
              <th style={th}>Name</th>
              <th style={th}>Platform</th>
              <th style={th}>Sample</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((d) => (
              <tr key={d.dataset_id}>
                <td style={td}>{d.dataset_id.slice(0, 8)}...</td>
                <td style={td}>{d.name}</td>
                <td style={td}>{d.platform}</td>
                <td style={td}>{d.sample_id}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
