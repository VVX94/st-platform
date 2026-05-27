import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api, type Run, type WorkerPollResponse } from "../api/client";

interface Experiment {
  experiment_id: string;
  name: string;
  task_type: string;
  status: string;
  run_count: number;
  dataset_id: string | null;
  parameters: Record<string, unknown>;
  created_at: string | null;
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

interface ExperimentReport {
  comparison_summary: Record<string, Record<string, number>>;
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
  const [comparison, setComparison] = useState<Record<string, Record<string, number>>>({});

  // Experiment creation form state
  const [showForm, setShowForm] = useState(false);
  const [formName, setFormName] = useState("");
  const [formTaskType, setFormTaskType] = useState("domain_detection");
  const [formDatasetId, setFormDatasetId] = useState("");
  const [selectedAlgos, setSelectedAlgos] = useState<string[]>([]);
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);

  // Auto-refresh state
  const [autoRefresh, setAutoRefresh] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadExperiments = useCallback(() => {
    api
      .get<Experiment[]>("/api/experiments")
      .then(setExperiments)
      .catch((e) => setError(String(e)));
  }, []);

  const loadRuns = useCallback(
    (expId: string) => {
      setSelectedExp(expId);
      setComparison({});
      api
        .getExperimentRuns(expId)
        .then((loadedRuns) => {
          setRuns(loadedRuns);
          // Check if any runs are pending
          const hasPending = loadedRuns.some(
            (r) => r.status === "queued" || r.status === "running"
          );
          setAutoRefresh(hasPending);
          // If all runs succeeded and there are multiple, load comparison
          const succeeded = loadedRuns.filter((r) => r.status === "succeeded");
          const uniqueAlgos = new Set(succeeded.map((r) => r.algorithm_id));
          if (uniqueAlgos.size > 1) {
            api
              .getExperimentReport(expId)
              .then((report) => setComparison(report.comparison_summary || {}))
              .catch(() => {});
          }
        })
        .catch((e) => setError(String(e)));
    },
    []
  );

  // Load algorithms and datasets for the creation form
  useEffect(() => {
    api
      .get<Algorithm[]>("/api/algorithms")
      .then(setAlgorithms)
      .catch(() => {});
    api
      .get<Dataset[]>("/api/datasets")
      .then(setDatasets)
      .catch(() => {});
  }, []);

  useEffect(() => {
    loadExperiments();
  }, [loadExperiments]);

  // Auto-refresh effect: poll every 3 seconds while autoRefresh is true
  useEffect(() => {
    if (autoRefresh && selectedExp) {
      intervalRef.current = setInterval(() => {
        api
          .getExperimentRuns(selectedExp)
          .then((loadedRuns) => {
            setRuns(loadedRuns);
            const hasPending = loadedRuns.some(
              (r) => r.status === "queued" || r.status === "running"
            );
            if (!hasPending) {
              setAutoRefresh(false);
              // Load comparison when all done
              const succeeded = loadedRuns.filter((r) => r.status === "succeeded");
              const uniqueAlgos = new Set(succeeded.map((r) => r.algorithm_id));
              if (uniqueAlgos.size > 1) {
                api
                  .getExperimentReport(selectedExp)
                  .then((report) =>
                    setComparison(report.comparison_summary || {})
                  )
                  .catch(() => {});
              }
            }
            loadExperiments();
          })
          .catch(() => {});
      }, 3000);
    }
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
    };
  }, [autoRefresh, selectedExp, loadExperiments]);

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

  const handleCreateExperiment = () => {
    if (!formName || selectedAlgos.length === 0) {
      setError("Name and at least one algorithm are required.");
      return;
    }
    setError("");
    api
      .post<{ experiment_id: string }>("/api/experiments", {
        name: formName,
        task_type: formTaskType,
        algorithm_ids: selectedAlgos,
        dataset_id: formDatasetId || undefined,
        parameters: {},
      })
      .then((exp) => {
        setShowForm(false);
        setFormName("");
        setSelectedAlgos([]);
        loadExperiments();
        loadRuns(exp.experiment_id);
      })
      .catch((e) => setError(String(e)));
  };

  const handleRegisterDemos = () => {
    api
      .registerAllDemoDatasets()
      .then(() => {
        // Reload datasets
        api.get<Dataset[]>("/api/datasets").then(setDatasets).catch(() => {});
      })
      .catch((e) => setError(String(e)));
  };

  const toggleAlgo = (algoId: string) => {
    setSelectedAlgos((prev) =>
      prev.includes(algoId) ? prev.filter((a) => a !== algoId) : [...prev, algoId]
    );
  };

  // Compute comparison metric names
  const comparisonMetricNames = Array.from(
    new Set(Object.values(comparison).flatMap((m) => Object.keys(m)))
  ).sort();

  const th: React.CSSProperties = {
    textAlign: "left",
    padding: "0.5rem 1rem",
    borderBottom: "2px solid #ddd",
  };
  const td: React.CSSProperties = {
    padding: "0.5rem 1rem",
    borderBottom: "1px solid #eee",
  };
  const btnStyle = (
    bg: string
  ): React.CSSProperties => ({
    padding: "0.5rem 1rem",
    backgroundColor: bg,
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontWeight: 600,
  });

  return (
    <div>
      <h1>Experiments</h1>
      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}

      {/* Top actions */}
      <div style={{ marginBottom: "1rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
        <button onClick={handlePoll} style={btnStyle("#198754")}>
          Run Worker
        </button>
        <button onClick={() => setShowForm(!showForm)} style={btnStyle("#0d6efd")}>
          {showForm ? "Cancel" : "New Experiment"}
        </button>
        {datasets.length === 0 && (
          <button onClick={handleRegisterDemos} style={btnStyle("#6c757d")}>
            Register Demo Datasets
          </button>
        )}
        {autoRefresh && (
          <span style={{ alignSelf: "center", color: "#0d6efd", fontSize: "0.85rem" }}>
            Auto-refreshing...
          </span>
        )}
        {pollResult && (
          <span style={{ alignSelf: "center", color: "#555" }}>{pollResult}</span>
        )}
      </div>

      {/* Experiment creation form */}
      {showForm && (
        <div
          style={{
            padding: "1rem",
            border: "1px solid #ddd",
            borderRadius: "8px",
            marginBottom: "1rem",
            backgroundColor: "#f9f9f9",
          }}
        >
          <h3 style={{ marginTop: 0 }}>Create Experiment</h3>
          <div style={{ display: "grid", gap: "0.75rem", maxWidth: "500px" }}>
            <label>
              Name:
              <input
                type="text"
                value={formName}
                onChange={(e) => setFormName(e.target.value)}
                style={{ width: "100%", padding: "0.4rem", marginTop: "0.25rem" }}
              />
            </label>
            <label>
              Task Type:
              <select
                value={formTaskType}
                onChange={(e) => setFormTaskType(e.target.value)}
                style={{ width: "100%", padding: "0.4rem", marginTop: "0.25rem" }}
              >
                <option value="domain_detection">Domain Detection</option>
                <option value="quality_control">Quality Control</option>
                <option value="deconvolution">Deconvolution</option>
              </select>
            </label>
            <label>
              Dataset:
              <select
                value={formDatasetId}
                onChange={(e) => setFormDatasetId(e.target.value)}
                style={{ width: "100%", padding: "0.4rem", marginTop: "0.25rem" }}
              >
                <option value="">-- None --</option>
                {datasets.map((d) => (
                  <option key={d.dataset_id} value={d.dataset_id}>
                    {d.name} ({d.platform})
                  </option>
                ))}
              </select>
            </label>
            <div>
              <div style={{ marginBottom: "0.25rem", fontWeight: 600 }}>Algorithms:</div>
              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: "0.5rem",
                  maxHeight: "120px",
                  overflowY: "auto",
                  padding: "0.5rem",
                  border: "1px solid #ddd",
                  borderRadius: "4px",
                  backgroundColor: "#fff",
                }}
              >
                {algorithms.map((a) => (
                  <label
                    key={a.algorithm_id}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.3rem",
                      fontSize: "0.85rem",
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={selectedAlgos.includes(a.algorithm_id)}
                      onChange={() => toggleAlgo(a.algorithm_id)}
                    />
                    {a.algorithm_id}
                  </label>
                ))}
              </div>
            </div>
            <button onClick={handleCreateExperiment} style={btnStyle("#198754")}>
              Create
            </button>
          </div>
        </div>
      )}

      {/* Experiments table */}
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
              <tr
                key={e.experiment_id}
                style={{
                  backgroundColor:
                    selectedExp === e.experiment_id ? "#f0f8ff" : undefined,
                }}
              >
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

      {/* Runs table for selected experiment */}
      {selectedExp && runs.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Runs for Experiment {selectedExp.slice(0, 8)}...</h2>
          <table
            style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}
          >
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
                  <td style={td}>
                    {r.started_at
                      ? new Date(r.started_at).toLocaleTimeString()
                      : "-"}
                  </td>
                  <td style={td}>
                    {r.finished_at
                      ? new Date(r.finished_at).toLocaleTimeString()
                      : "-"}
                  </td>
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

      {/* Algorithm comparison table */}
      {Object.keys(comparison).length > 0 && comparisonMetricNames.length > 0 && (
        <div style={{ marginTop: "2rem" }}>
          <h2>Algorithm Comparison</h2>
          <table
            style={{ width: "100%", borderCollapse: "collapse", marginTop: "0.5rem" }}
          >
            <thead>
              <tr>
                <th style={th}>Algorithm</th>
                {comparisonMetricNames.map((name) => (
                  <th key={name} style={th}>{name}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {Object.entries(comparison).map(([algoId, metrics]) => (
                <tr key={algoId}>
                  <td style={td}>{algoId}</td>
                  {comparisonMetricNames.map((name) => (
                    <td key={name} style={td}>
                      {metrics[name] !== undefined ? metrics[name].toFixed(4) : "-"}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
