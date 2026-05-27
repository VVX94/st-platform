import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api, type ExperimentReport } from "../api/client";

interface Experiment {
  experiment_id: string;
  name: string;
  status: string;
  run_count: number;
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

export default function Reports() {
  const { experimentId } = useParams<{ experimentId: string }>();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [report, setReport] = useState<ExperimentReport | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (experimentId) {
      api
        .getExperimentReport(experimentId)
        .then(setReport)
        .catch((e) => setError(String(e)));
    } else {
      api
        .get<Experiment[]>("/api/experiments")
        .then(setExperiments)
        .catch((e) => setError(String(e)));
    }
  }, [experimentId]);

  const th: React.CSSProperties = {
    textAlign: "left",
    padding: "0.5rem 1rem",
    borderBottom: "2px solid #ddd",
  };
  const td: React.CSSProperties = {
    padding: "0.5rem 1rem",
    borderBottom: "1px solid #eee",
  };

  // If viewing a specific experiment report
  if (experimentId && report) {
    const domainGridArtifact = report.artifacts.find(
      (a) => a.kind === "domain_grid_plot"
    );
    const metricsBarArtifact = report.artifacts.find(
      (a) => a.kind === "metrics_bar_plot"
    );
    const metricsCsvArtifact = report.artifacts.find(
      (a) => a.kind === "metrics_csv"
    );
    const domainCsvArtifact = report.artifacts.find(
      (a) => a.kind === "domain_predictions_csv"
    );

    return (
      <div>
        <Link to="/reports" style={{ color: "#0d6efd", textDecoration: "none" }}>
          &larr; Back to Reports
        </Link>
        <h1 style={{ marginTop: "0.5rem" }}>{report.name}</h1>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr 1fr",
            gap: "1rem",
            marginTop: "1rem",
          }}
        >
          <div>
            <div style={{ fontWeight: 600, color: "#555" }}>Experiment ID</div>
            <div>{report.experiment_id}</div>
          </div>
          <div>
            <div style={{ fontWeight: 600, color: "#555" }}>Status</div>
            <span style={statusBadge(report.status)}>{report.status}</span>
          </div>
          <div>
            <div style={{ fontWeight: 600, color: "#555" }}>Task Type</div>
            <div>{report.task_type}</div>
          </div>
        </div>

        {/* Metrics Summary */}
        {Object.keys(report.metrics_summary).length > 0 && (
          <div style={{ marginTop: "2rem" }}>
            <h2>Metrics Summary</h2>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginTop: "0.5rem",
              }}
            >
              <thead>
                <tr>
                  <th style={th}>Metric</th>
                  <th style={th}>Average</th>
                  <th style={th}>Min</th>
                  <th style={th}>Max</th>
                  <th style={th}>Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(report.metrics_summary).map(([name, stats]) => (
                  <tr key={name}>
                    <td style={td}>{name}</td>
                    <td style={td}>{stats.avg.toFixed(4)}</td>
                    <td style={td}>{stats.min.toFixed(4)}</td>
                    <td style={td}>{stats.max.toFixed(4)}</td>
                    <td style={td}>{stats.count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Runs Table */}
        {report.runs.length > 0 && (
          <div style={{ marginTop: "2rem" }}>
            <h2>Runs</h2>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginTop: "0.5rem",
              }}
            >
              <thead>
                <tr>
                  <th style={th}>Run ID</th>
                  <th style={th}>Algorithm</th>
                  <th style={th}>Status</th>
                  <th style={th}>Metrics</th>
                  <th style={th}>Details</th>
                </tr>
              </thead>
              <tbody>
                {report.runs.map((r) => (
                  <tr key={r.run_id}>
                    <td style={td}>{r.run_id.slice(0, 12)}...</td>
                    <td style={td}>{r.algorithm_id}</td>
                    <td style={td}>
                      <span style={statusBadge(r.status)}>{r.status}</span>
                    </td>
                    <td style={td}>
                      {Object.entries(r.metrics)
                        .map(([k, v]) => `${k}=${v.toFixed(3)}`)
                        .join(", ") || "-"}
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

        {/* Plots */}
        <div style={{ marginTop: "2rem" }}>
          <h2>Visualizations</h2>
          <div
            style={{
              display: "flex",
              gap: "2rem",
              flexWrap: "wrap",
              marginTop: "1rem",
            }}
          >
            {domainGridArtifact && (
              <div>
                <h3>Domain Grid Plot</h3>
                <img
                  src={`/artifacts/file?path=${encodeURIComponent(domainGridArtifact.uri)}`}
                  alt="Domain Grid Plot"
                  style={{
                    maxWidth: "450px",
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                  }}
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              </div>
            )}
            {metricsBarArtifact && (
              <div>
                <h3>Metrics Bar Chart</h3>
                <img
                  src={`/artifacts/file?path=${encodeURIComponent(metricsBarArtifact.uri)}`}
                  alt="Metrics Bar Chart"
                  style={{
                    maxWidth: "450px",
                    border: "1px solid #ddd",
                    borderRadius: "4px",
                  }}
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              </div>
            )}
            {!domainGridArtifact && !metricsBarArtifact && (
              <p style={{ color: "#888" }}>
                No plot artifacts found. Run an experiment first.
              </p>
            )}
          </div>
        </div>

        {/* Download Links */}
        {(metricsCsvArtifact || domainCsvArtifact) && (
          <div style={{ marginTop: "2rem" }}>
            <h2>Downloads</h2>
            <ul style={{ listStyle: "none", padding: 0 }}>
              {metricsCsvArtifact && (
                <li style={{ marginBottom: "0.5rem" }}>
                  <a
                    href={`/artifacts/file?path=${encodeURIComponent(metricsCsvArtifact.uri)}`}
                    style={{ color: "#0d6efd" }}
                  >
                    Download Metrics CSV
                  </a>
                </li>
              )}
              {domainCsvArtifact && (
                <li style={{ marginBottom: "0.5rem" }}>
                  <a
                    href={`/artifacts/file?path=${encodeURIComponent(domainCsvArtifact.uri)}`}
                    style={{ color: "#0d6efd" }}
                  >
                    Download Domain Predictions CSV
                  </a>
                </li>
              )}
            </ul>
          </div>
        )}

        {/* All artifacts list */}
        {report.artifacts.length > 0 && (
          <div style={{ marginTop: "2rem" }}>
            <h2>All Artifacts</h2>
            <table
              style={{
                width: "100%",
                borderCollapse: "collapse",
                marginTop: "0.5rem",
              }}
            >
              <thead>
                <tr>
                  <th style={th}>Kind</th>
                  <th style={th}>Run</th>
                  <th style={th}>URI</th>
                  <th style={th}>Description</th>
                </tr>
              </thead>
              <tbody>
                {report.artifacts.map((a) => (
                  <tr key={a.artifact_id}>
                    <td style={td}>{a.kind}</td>
                    <td style={td}>{a.run_id.slice(0, 8)}...</td>
                    <td
                      style={{
                        ...td,
                        maxWidth: "300px",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                        whiteSpace: "nowrap",
                      }}
                    >
                      {a.uri}
                    </td>
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

  // Default: list experiments with report links
  return (
    <div>
      <h1>Reports</h1>
      {error && <div style={{ color: "red", marginBottom: "1rem" }}>{error}</div>}
      {experiments.length === 0 && !error ? (
        <p>No experiments created yet. Create an experiment first to generate reports.</p>
      ) : (
        <table
          style={{
            width: "100%",
            borderCollapse: "collapse",
            marginTop: "1rem",
          }}
        >
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
            {experiments.map((e) => (
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
                    View Report
                  </Link>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
