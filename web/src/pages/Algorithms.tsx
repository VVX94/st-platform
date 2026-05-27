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
  const [expanded, setExpanded] = useState<string | null>(null);

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

  // Group algorithms by task type
  const taskTypeGroups = algorithms.reduce<Record<string, Algorithm[]>>((acc, algo) => {
    if (!acc[algo.task_type]) acc[algo.task_type] = [];
    acc[algo.task_type].push(algo);
    return acc;
  }, {});

  return (
    <div>
      <h1>Algorithms</h1>
      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}

      {/* Task type summary */}
      {Object.keys(taskTypeGroups).length > 0 && (
        <div
          style={{
            display: "flex",
            gap: "0.5rem",
            flexWrap: "wrap",
            marginBottom: "1.5rem",
          }}
        >
          {Object.entries(taskTypeGroups).map(([taskType, algos]) => (
            <span
              key={taskType}
              style={{
                display: "inline-block",
                padding: "0.3rem 0.75rem",
                borderRadius: "16px",
                fontSize: "0.8rem",
                backgroundColor: "#e9ecef",
                color: "#495057",
              }}
            >
              {taskType}: {algos.length} algorithm{algos.length > 1 ? "s" : ""}
            </span>
          ))}
        </div>
      )}

      {/* Algorithms table */}
      <table style={{ width: "100%", borderCollapse: "collapse", marginTop: "1rem" }}>
        <thead>
          <tr>
            <th style={th}>ID</th>
            <th style={th}>Name</th>
            <th style={th}>Task Type</th>
            <th style={th}>Runtime</th>
            <th style={th}>Version</th>
            <th style={th}>Tags</th>
            <th style={th}>Details</th>
          </tr>
        </thead>
        <tbody>
          {algorithms.map((a) => (
            <>
              <tr key={a.algorithm_id}>
                <td style={td}>{a.algorithm_id}</td>
                <td style={td}>{a.name}</td>
                <td style={td}>{a.task_type}</td>
                <td style={td}>{a.runtime}</td>
                <td style={td}>{a.version}</td>
                <td style={td}>
                  {a.tags.map((tag) => (
                    <span
                      key={tag}
                      style={{
                        display: "inline-block",
                        padding: "0.1rem 0.4rem",
                        borderRadius: "4px",
                        fontSize: "0.75rem",
                        backgroundColor: "#e9ecef",
                        color: "#495057",
                        marginRight: "0.25rem",
                      }}
                    >
                      {tag}
                    </span>
                  ))}
                </td>
                <td style={td}>
                  <button
                    onClick={() =>
                      setExpanded(expanded === a.algorithm_id ? null : a.algorithm_id)
                    }
                    style={{
                      padding: "0.2rem 0.5rem",
                      backgroundColor: expanded === a.algorithm_id ? "#6c757d" : "#0d6efd",
                      color: "#fff",
                      border: "none",
                      borderRadius: "4px",
                      cursor: "pointer",
                      fontSize: "0.8rem",
                    }}
                  >
                    {expanded === a.algorithm_id ? "Hide" : "Show"}
                  </button>
                </td>
              </tr>
              {expanded === a.algorithm_id && (
                <tr key={`${a.algorithm_id}-detail`}>
                  <td
                    colSpan={7}
                    style={{
                      ...td,
                      backgroundColor: "#f8f9fa",
                      padding: "1rem",
                    }}
                  >
                    <div style={{ maxWidth: "600px" }}>
                      <strong>Description:</strong>{" "}
                      {a.description || "No description available."}
                    </div>
                    <div style={{ marginTop: "0.5rem" }}>
                      <strong>Supports task type:</strong> {a.task_type}
                    </div>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
      {algorithms.length === 0 && !error && <p>Loading...</p>}
    </div>
  );
}
