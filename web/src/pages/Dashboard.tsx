import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Row, Col, Card, Statistic, Table, Tag } from "antd";
import {
  CheckCircleOutlined,
  ExperimentOutlined,
  DatabaseOutlined,
  AppstoreOutlined,
  RocketOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { api, type Run } from "../api/client";
import StatusTag from "../components/StatusTag";

interface Health { status: string; version: string; }
interface Algorithm { algorithm_id: string; name: string; task_type: string; }
interface Dataset { dataset_id: string; name: string; platform: string; }
interface Experiment { experiment_id: string; name: string; status: string; run_count: number; created_at: string | null; }

export default function Dashboard() {
  const { t } = useTranslation();
  const [health, setHealth] = useState<Health | null>(null);
  const [algoCount, setAlgoCount] = useState(0);
  const [dsCount, setDsCount] = useState(0);
  const [expCount, setExpCount] = useState(0);
  const [runCount, setRunCount] = useState(0);
  const [recentExps, setRecentExps] = useState<Experiment[]>([]);
  const [recentRuns, setRecentRuns] = useState<Run[]>([]);
  const [runStatusCounts, setRunStatusCounts] = useState<Record<string, number>>({});
  const [error, setError] = useState("");

  useEffect(() => {
    api.get<Health>("/api/health").then(setHealth).catch((e) => setError(String(e)));
    api.get<Algorithm[]>("/api/algorithms").then((d) => setAlgoCount(d.length)).catch(() => {});
    api.get<Dataset[]>("/api/datasets").then((d) => setDsCount(d.length)).catch(() => {});
    api.get<Experiment[]>("/api/experiments").then((d) => { setExpCount(d.length); setRecentExps(d.slice(0, 5)); }).catch(() => {});
    api.get<Run[]>("/api/runs").then((d) => {
      setRunCount(d.length);
      setRecentRuns(d.slice(0, 5));
      const counts: Record<string, number> = {};
      d.forEach((r) => { counts[r.status] = (counts[r.status] || 0) + 1; });
      setRunStatusCounts(counts);
    }).catch(() => {});
  }, []);

  const pieOption = {
    tooltip: { trigger: "item" as const },
    series: [{
      type: "pie",
      radius: ["40%", "70%"],
      itemStyle: { borderRadius: 6 },
      label: { show: true, formatter: "{b}: {c}" },
      data: Object.entries(runStatusCounts).map(([name, value]) => ({ name: t(`status.${name}`, name), value })),
    }],
  };

  const expColumns = [
    { title: t("common.id"), dataIndex: "experiment_id", key: "id", render: (v: string) => v.slice(0, 8) + "..." },
    { title: t("common.name"), dataIndex: "name", key: "name" },
    { title: t("common.status"), dataIndex: "status", key: "status", render: (s: string) => <StatusTag status={s} /> },
    { title: t("dashboard.runs"), dataIndex: "run_count", key: "runs" },
    { title: t("dashboard.report"), key: "report", render: (_: unknown, r: Experiment) => <Link to={`/reports/${r.experiment_id}`}>{t("common.view")}</Link> },
  ];

  const runColumns = [
    { title: t("dashboard.runId"), dataIndex: "run_id", key: "id", render: (v: string) => v.slice(0, 12) + "..." },
    { title: t("dashboard.algorithm"), dataIndex: "algorithm_id", key: "algo" },
    { title: t("common.status"), dataIndex: "status", key: "status", render: (s: string) => <StatusTag status={s} /> },
    { title: t("common.details"), key: "details", render: (_: unknown, r: Run) => <Link to={`/runs/${r.run_id}`}>{t("common.view")}</Link> },
  ];

  return (
    <div>
      <h2 style={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, marginBottom: 24 }}>{t("dashboard.title")}</h2>
      {error && <div style={{ color: "#DC2626", marginBottom: 16 }}>{t("common.error")}: {error}</div>}

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={4}>
          <Card size="small">
            <Statistic title={t("dashboard.apiStatus")} value={health ? health.status : "..."} prefix={<CheckCircleOutlined style={{ color: "#16A34A" }} />} />
            {health && <div style={{ fontSize: 12, color: "#94A3B8" }}>v{health.version}</div>}
          </Card>
        </Col>
        <Col xs={12} sm={6} lg={5}>
          <Card size="small"><Statistic title={t("dashboard.algorithms")} value={algoCount} prefix={<AppstoreOutlined />} /></Card>
        </Col>
        <Col xs={12} sm={6} lg={5}>
          <Card size="small"><Statistic title={t("dashboard.datasets")} value={dsCount} prefix={<DatabaseOutlined />} /></Card>
        </Col>
        <Col xs={12} sm={6} lg={5}>
          <Card size="small"><Statistic title={t("dashboard.experiments")} value={expCount} prefix={<ExperimentOutlined />} /></Card>
        </Col>
        <Col xs={12} sm={6} lg={5}>
          <Card size="small"><Statistic title={t("dashboard.totalRuns")} value={runCount} prefix={<RocketOutlined />} /></Card>
        </Col>
      </Row>

      {Object.keys(runStatusCounts).length > 0 && (
        <Card size="small" style={{ marginTop: 24 }} title={t("dashboard.totalRuns")}>
          <ReactECharts option={pieOption} style={{ height: 280 }} />
        </Card>
      )}

      {recentExps.length > 0 && (
        <Card size="small" style={{ marginTop: 24 }} title={t("dashboard.recentExperiments")}>
          <Table dataSource={recentExps} columns={expColumns} rowKey="experiment_id" pagination={false} size="small" />
        </Card>
      )}

      {recentRuns.length > 0 && (
        <Card size="small" style={{ marginTop: 24 }} title={t("dashboard.recentRuns")}>
          <Table dataSource={recentRuns} columns={runColumns} rowKey="run_id" pagination={false} size="small" />
        </Card>
      )}
    </div>
  );
}
