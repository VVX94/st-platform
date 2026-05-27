import { useEffect, useState } from "react";
import { api } from "../api/client";

interface Dataset {
  dataset_id: string;
  name: string;
  platform: string;
  sample_id: string;
  description: string;
  metadata: Record<string, unknown>;
}

export default function Datasets() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [error, setError] = useState<string>("");
  const [showRealForm, setShowRealForm] = useState(false);
  const [realName, setRealName] = useState("");
  const [realPath, setRealPath] = useState("");
  const [realLabelCol, setRealLabelCol] = useState("");

  const loadDatasets = () => {
    api
      .get<Dataset[]>("/api/datasets")
      .then(setDatasets)
      .catch((e) => setError(String(e)));
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const handleRegisterDemo = () => {
    api
      .registerDemoDataset()
      .then(() => loadDatasets())
      .catch((e) => setError(String(e)));
  };

  const handleRegisterAllDemos = () => {
    api
      .registerAllDemoDatasets()
      .then(() => loadDatasets())
      .catch((e) => setError(String(e)));
  };

  const handleRegisterReal = () => {
    if (!realName || !realPath) {
      setError("Name and path are required.");
      return;
    }
    setError("");
    api
      .post("/api/datasets/register-real", {
        name: realName,
        path: realPath,
        label_column: realLabelCol || null,
      })
      .then(() => {
        setShowRealForm(false);
        setRealName("");
        setRealPath("");
        setRealLabelCol("");
        loadDatasets();
      })
      .catch((e) => setError(String(e)));
  };

  const btnStyle = (bg: string): React.CSSProperties => ({
    padding: "0.5rem 1rem",
    backgroundColor: bg,
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontWeight: 600,
  });

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
      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}

      {/* Action buttons */}
      <div style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <button onClick={handleRegisterDemo} style={btnStyle("#198754")}>
          Register Demo Dataset
        </button>
        <button onClick={handleRegisterAllDemos} style={btnStyle("#0d6efd")}>
          Register All Demos
        </button>
        <button
          onClick={() => setShowRealForm(!showRealForm)}
          style={btnStyle("#6c757d")}
        >
          {showRealForm ? "Cancel" : "Register Real Dataset"}
        </button>
      </div>

      {/* Real dataset registration form */}
      {showRealForm && (
        <div
          style={{
            padding: "1rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "1rem",
            backgroundColor: "#f9f9f9",
          }}
        >
          <h3 style={{ marginTop: 0 }}>Register Real Dataset</h3>
          <div style={{ display: "grid", gap: "0.75rem", maxWidth: "500px" }}>
            <label>
              Name:
              <input
                type="text"
                value={realName}
                onChange={(e) => setRealName(e.target.value)}
                style={{ width: "100%", padding: "0.4rem", marginTop: "0.25rem" }}
              />
            </label>
            <label>
              File Path:
              <input
                type="text"
                value={realPath}
                onChange={(e) => setRealPath(e.target.value)}
                placeholder="/path/to/data.h5ad"
                style={{ width: "100%", padding: "0.4rem", marginTop: "0.25rem" }}
              />
            </label>
            <label>
              Label Column (optional):
              <input
                type="text"
                value={realLabelCol}
                onChange={(e) => setRealLabelCol(e.target.value)}
                placeholder="e.g. label"
                style={{ width: "100%", padding: "0.4rem", marginTop: "0.25rem" }}
              />
            </label>
            <button onClick={handleRegisterReal} style={btnStyle("#198754")}>
              Register
            </button>
          </div>
        </div>
      )}

      {/* Datasets table */}
      {datasets.length === 0 && !error ? (
        <p>No datasets registered yet. Use the buttons above to register one.</p>
      ) : (
        <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
          <thead>
            <tr>
              <th style={th}>ID</th>
              <th style={th}>Name</th>
              <th style={th}>Platform</th>
              <th style={th}>Sample</th>
              <th style={th}>n_obs</th>
              <th style={th}>n_vars</th>
              <th style={th}>Label Col</th>
            </tr>
          </thead>
          <tbody>
            {datasets.map((d) => (
              <tr key={d.dataset_id}>
                <td style={td}>{d.dataset_id.slice(0, 8)}...</td>
                <td style={td}>{d.name}</td>
                <td style={td}>{d.platform}</td>
                <td style={td}>{d.sample_id}</td>
                <td style={td}>
                  {d.metadata.n_obs !== undefined ? String(d.metadata.n_obs) : "-"}
                </td>
                <td style={td}>
                  {d.metadata.n_vars !== undefined ? String(d.metadata.n_vars) : "-"}
                </td>
                <td style={td}>
                  {d.metadata.label_column ? String(d.metadata.label_column) : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
