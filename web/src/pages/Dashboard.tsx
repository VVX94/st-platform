import { useEffect, useState } from "react";
import { api } from "../api/client";

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
}

export default function Dashboard() {
  const [health, setHealth] = useState<Health | null>(null);
  const [algoCount, setAlgoCount] = useState<number>(0);
  const [dsCount, setDsCount] = useState<number>(0);
  const [expCount, setExpCount] = useState<number>(0);
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
      .then((data) => setExpCount(data.length))
      .catch(() => {});
  }, []);

  const card: React.CSSProperties = {
    padding: "1.5rem",
    borderRadius: "8px",
    backgroundColor: "#f5f5f5",
    flex: "1",
    minWidth: "200px",
  };

  return (
    <div>
      <h1>Dashboard</h1>
      {error && (
        <div style={{ color: "red", marginBottom: "1rem" }}>
          API unreachable: {error}
        </div>
      )}
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
      </div>
    </div>
  );
}
