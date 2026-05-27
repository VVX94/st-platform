import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, Descriptions, Timeline, Button, Tag, Empty } from "antd";
import { ArrowLeftOutlined, ClockCircleOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { api, type Run } from "../api/client";
import StatusTag from "../components/StatusTag";

function formatDuration(started: string | null, finished: string | null): string {
  if (!started) return "-";
  const start = new Date(started).getTime();
  const end = finished ? new Date(finished).getTime() : Date.now();
  const seconds = ((end - start) / 1000).toFixed(1);
  return `${seconds}s`;
}

export default function RunDetail() {
  const { t } = useTranslation();
  const { runId } = useParams<{ runId: string }>();
  const [run, setRun] = useState<Run | null>(null);
  const [metrics, setMetrics] = useState<Record<string, number>>({});
  const [error, setError] = useState("");

  useEffect(() => {
    if (!runId) return;
    api.get<Run>(`/api/runs/${runId}`).then(setRun).catch((e) => setError(String(e)));
    api.getRunMetrics(runId).then((m) => {
      const map: Record<string, number> = {};
      m.forEach((metric) => { map[metric.name] = metric.value; });
      setMetrics(map);
    }).catch(() => {});
  }, [runId]);

  if (error) return <div style={{ color: "#DC2626" }}>{error}</div>;
  if (!run) return <Empty description={t("common.loading")} />;

  const allMetrics = { ...run.metrics, ...metrics };
  const metricNames = Object.keys(allMetrics);

  const barOption = metricNames.length > 0 ? {
    tooltip: { trigger: "axis" as const },
    grid: { left: 160, right: 60, top: 10, bottom: 10 },
    xAxis: { type: "value" as const },
    yAxis: {
      type: "category" as const,
      data: metricNames.map((m) => t(`metrics.${m}`, m)),
      axisLabel: { width: 140, overflow: "truncate" },
    },
    series: [{
      type: "bar" as const,
      data: metricNames.map((m) => allMetrics[m]),
      itemStyle: { color: "#1E40AF", borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: "right" as const, formatter: (p: { value: number }) => p.value.toFixed(4) },
    }],
  } : null;

  const timelineItems = [];
  if (run.created_at) {
    timelineItems.push({ color: "gray", children: <span>Created <ClockCircleOutlined /> {new Date(run.created_at).toLocaleString()}</span> });
  }
  if (run.started_at) {
    timelineItems.push({ color: "blue", children: <span>Started <ClockCircleOutlined /> {new Date(run.started_at).toLocaleString()}</span> });
  }
  if (run.finished_at) {
    timelineItems.push({
      color: run.status === "succeeded" ? "green" : "red",
      children: <span>{run.status === "succeeded" ? "Succeeded" : "Failed"} <ClockCircleOutlined /> {new Date(run.finished_at).toLocaleString()}</span>,
    });
  }

  return (
    <div>
      <Link to="/experiments">
        <Button icon={<ArrowLeftOutlined />} type="link" style={{ padding: 0, marginBottom: 16 }}>{t("common.back")}</Button>
      </Link>
      <h2 style={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, marginBottom: 24 }}>{t("runDetail.title")}</h2>

      <Descriptions size="small" bordered column={2} style={{ marginBottom: 24 }}>
        <Descriptions.Item label={t("common.id")}>{run.run_id}</Descriptions.Item>
        <Descriptions.Item label={t("common.status")}><StatusTag status={run.status} /></Descriptions.Item>
        <Descriptions.Item label={t("runDetail.algorithm")}>{run.algorithm_id}</Descriptions.Item>
        <Descriptions.Item label={t("algorithms.taskType")}>{run.task_type}</Descriptions.Item>
        <Descriptions.Item label={t("runDetail.startedAt")}>{run.started_at ? new Date(run.started_at).toLocaleString() : "-"}</Descriptions.Item>
        <Descriptions.Item label={t("runDetail.finishedAt")}>{run.finished_at ? new Date(run.finished_at).toLocaleString() : "-"}</Descriptions.Item>
        <Descriptions.Item label={t("runDetail.duration")}>{formatDuration(run.started_at, run.finished_at)}</Descriptions.Item>
        {run.experiment_id && (
          <Descriptions.Item label={t("runDetail.experiment")}>
            <Link to={`/reports/${run.experiment_id}`}>{run.experiment_id.slice(0, 8)}...</Link>
          </Descriptions.Item>
        )}
      </Descriptions>

      {timelineItems.length > 0 && (
        <Card size="small" title={t("runDetail.executionTimeline")} style={{ marginBottom: 24 }}>
          <Timeline items={timelineItems} />
        </Card>
      )}

      {metricNames.length > 0 && (
        <Card size="small" title={t("runDetail.metrics")} style={{ marginBottom: 24 }}>
          <ReactECharts option={barOption} style={{ height: Math.max(200, metricNames.length * 36 + 20) }} />
        </Card>
      )}

      {run.error && (
        <Card size="small" title={t("runDetail.errorLog")} style={{ marginBottom: 24 }}>
          <pre style={{ background: "#FEF2F2", padding: 12, borderRadius: 6, color: "#991B1B", whiteSpace: "pre-wrap", fontSize: 13 }}>{run.error}</pre>
        </Card>
      )}

      {run.artifacts && run.artifacts.length > 0 && (
        <Card size="small" title={t("runDetail.artifacts")} style={{ marginBottom: 24 }}>
          <ul style={{ paddingLeft: 20 }}>
            {run.artifacts.map((a, i) => (
              <li key={i} style={{ marginBottom: 4 }}>
                <Tag>{String(a.kind ?? "")}</Tag>
                {String(a.description ?? "")}
                {a.uri != null && (
                  <a href={`/api/artifacts/file?path=${encodeURIComponent(String(a.uri))}`} style={{ marginLeft: 8, color: "#1E40AF" }}>{t("reports.download")}</a>
                )}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
