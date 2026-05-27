import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { Card, Table, Descriptions, Image, Button, Space, Empty, Row, Col } from "antd";
import { ArrowLeftOutlined, DownloadOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { api, type ExperimentReport } from "../api/client";
import StatusTag from "../components/StatusTag";

interface Experiment {
  experiment_id: string;
  name: string;
  status: string;
  run_count: number;
}

export default function Reports() {
  const { t } = useTranslation();
  const { experimentId } = useParams<{ experimentId: string }>();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [report, setReport] = useState<ExperimentReport | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (experimentId) {
      api.getExperimentReport(experimentId).then(setReport).catch((e) => setError(String(e)));
    } else {
      api.get<Experiment[]>("/api/experiments").then(setExperiments).catch((e) => setError(String(e)));
    }
  }, [experimentId]);

  // Experiment detail view
  if (experimentId && report) {
    const algos = report.runs.map((r) => r.algorithm_id);
    const metricNames = Object.keys(report.comparison_summary);
    const barSeries = metricNames.map((metric) => ({
      name: t(`metrics.${metric}`, metric),
      type: "bar" as const,
      data: algos.map((algo) => report.comparison_summary[metric]?.[algo] ?? 0),
    }));

    const barOption = {
      tooltip: { trigger: "axis" as const },
      legend: { top: 0 },
      grid: { top: 40, bottom: 30 },
      xAxis: { type: "category" as const, data: algos },
      yAxis: { type: "value" as const },
      series: barSeries,
    };

    // Radar chart (max 8 metrics)
    const radarMetrics = metricNames.slice(0, 8);
    const radarOption = {
      tooltip: {},
      legend: { top: 0, data: algos },
      radar: {
        indicator: radarMetrics.map((m) => ({
          name: t(`metrics.${m}`, m),
          max: 1,
        })),
      },
      series: [{
        type: "radar" as const,
        data: algos.map((algo) => ({
          name: algo,
          value: radarMetrics.map((m) => report.comparison_summary[m]?.[algo] ?? 0),
        })),
      }],
    };

    const domainGridArtifact = report.artifacts.find((a) => a.kind === "domain_grid_plot");
    const metricsBarArtifact = report.artifacts.find((a) => a.kind === "metrics_bar_plot");
    const metricsCsvArtifact = report.artifacts.find((a) => a.kind === "metrics_csv");
    const domainCsvArtifact = report.artifacts.find((a) => a.kind === "domain_predictions_csv");

    const runColumns = [
      { title: "Run ID", dataIndex: "run_id", key: "id", render: (v: string) => v.slice(0, 12) + "..." },
      { title: t("dashboard.algorithm"), dataIndex: "algorithm_id", key: "algo" },
      { title: t("common.status"), dataIndex: "status", key: "status", render: (s: string) => <StatusTag status={s} /> },
      {
        title: t("reports.metric"), key: "metrics",
        render: (_: unknown, r: { metrics: Record<string, number> }) =>
          Object.entries(r.metrics).map(([k, v]) => `${t(`metrics.${k}`, k)}=${v.toFixed(3)}`).join(", ") || "-",
      },
      { title: t("common.details"), key: "details", render: (_: unknown, r: { run_id: string }) => <Link to={`/runs/${r.run_id}`}>{t("common.view")}</Link> },
    ];

    const summaryColumns = [
      { title: t("reports.metric"), dataIndex: "name", key: "name", render: (v: string) => t(`metrics.${v}`, v) },
      { title: "Avg", dataIndex: "avg", key: "avg", render: (v: number) => v.toFixed(4) },
      { title: "Min", dataIndex: "min", key: "min", render: (v: number) => v.toFixed(4) },
      { title: "Max", dataIndex: "max", key: "max", render: (v: number) => v.toFixed(4) },
      { title: "Count", dataIndex: "count", key: "count" },
    ];

    const summaryData = Object.entries(report.metrics_summary).map(([name, stats]) => ({ name, ...stats }));

    return (
      <div>
        <Link to="/reports">
          <Button icon={<ArrowLeftOutlined />} type="link" style={{ padding: 0, marginBottom: 16 }}>
            {t("common.back")}
          </Button>
        </Link>
        <h2 style={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, marginBottom: 24 }}>{report.name}</h2>

        <Descriptions size="small" bordered column={3} style={{ marginBottom: 24 }}>
          <Descriptions.Item label={t("common.id")}>{report.experiment_id}</Descriptions.Item>
          <Descriptions.Item label={t("common.status")}><StatusTag status={report.status} /></Descriptions.Item>
          <Descriptions.Item label={t("algorithms.taskType")}>{report.task_type}</Descriptions.Item>
        </Descriptions>

        {metricNames.length > 0 && (
          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={16}>
              <Card size="small" title={t("reports.metricsComparison")}>
                <ReactECharts option={barOption} style={{ height: 320 }} />
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" title={t("reports.radarChart")}>
                <ReactECharts option={radarOption} style={{ height: 320 }} />
              </Card>
            </Col>
          </Row>
        )}

        {summaryData.length > 0 && (
          <Card size="small" title={t("reports.metricsComparison")} style={{ marginBottom: 24 }}>
            <Table dataSource={summaryData} columns={summaryColumns} rowKey="name" pagination={false} size="small" />
          </Card>
        )}

        {report.runs.length > 0 && (
          <Card size="small" title={t("reports.runDetails")} style={{ marginBottom: 24 }}>
            <Table dataSource={report.runs} columns={runColumns} rowKey="run_id" pagination={false} size="small" />
          </Card>
        )}

        {(domainGridArtifact || metricsBarArtifact) && (
          <Card size="small" title={t("reports.artifacts")} style={{ marginBottom: 24 }}>
            <Space size="large" wrap>
              {domainGridArtifact && (
                <div>
                  <div style={{ marginBottom: 8, fontWeight: 500 }}>Domain Grid Plot</div>
                  <Image
                    src={`/api/artifacts/file?path=${encodeURIComponent(domainGridArtifact.uri)}`}
                    width={400}
                    fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
                  />
                </div>
              )}
              {metricsBarArtifact && (
                <div>
                  <div style={{ marginBottom: 8, fontWeight: 500 }}>Metrics Bar Chart</div>
                  <Image
                    src={`/api/artifacts/file?path=${encodeURIComponent(metricsBarArtifact.uri)}`}
                    width={400}
                    fallback="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAACklEQVR4nGMAAQAABQABDQottAAAAABJRU5ErkJggg=="
                  />
                </div>
              )}
            </Space>
          </Card>
        )}

        {(metricsCsvArtifact || domainCsvArtifact) && (
          <Card size="small" title={t("reports.download")} style={{ marginBottom: 24 }}>
            <Space>
              {metricsCsvArtifact && (
                <Button icon={<DownloadOutlined />} href={`/api/artifacts/file?path=${encodeURIComponent(metricsCsvArtifact.uri)}`}>
                  Metrics CSV
                </Button>
              )}
              {domainCsvArtifact && (
                <Button icon={<DownloadOutlined />} href={`/api/artifacts/file?path=${encodeURIComponent(domainCsvArtifact.uri)}`}>
                  Domain Predictions CSV
                </Button>
              )}
            </Space>
          </Card>
        )}
      </div>
    );
  }

  // Experiment list view
  const expColumns = [
    { title: t("common.id"), dataIndex: "experiment_id", key: "id", render: (v: string) => v.slice(0, 8) + "..." },
    { title: t("common.name"), dataIndex: "name", key: "name" },
    { title: t("common.status"), dataIndex: "status", key: "status", render: (s: string) => <StatusTag status={s} /> },
    { title: t("dashboard.runs"), dataIndex: "run_count", key: "runs" },
    { title: t("dashboard.report"), key: "report", render: (_: unknown, e: Experiment) => <Link to={`/reports/${e.experiment_id}`}>{t("common.view")}</Link> },
  ];

  return (
    <div>
      <h2 style={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, marginBottom: 24 }}>{t("reports.title")}</h2>
      {error && <div style={{ color: "#DC2626", marginBottom: 16 }}>{error}</div>}
      {experiments.length === 0 && !error ? (
        <Empty description={t("reports.noReports")} />
      ) : (
        <Card size="small">
          <Table dataSource={experiments} columns={expColumns} rowKey="experiment_id" size="small" />
        </Card>
      )}
    </div>
  );
}
