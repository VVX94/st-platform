import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Card, Table, Button, Form, Input, Select, Checkbox, Space, Progress, Badge, message } from "antd";
import { PlusOutlined, PlayCircleOutlined, SyncOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import ReactECharts from "echarts-for-react";
import { api, type Run, type WorkerPollResponse } from "../api/client";
import StatusTag from "../components/StatusTag";

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

export default function Experiments() {
  const { t } = useTranslation();
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [error, setError] = useState("");
  const [selectedExp, setSelectedExp] = useState<string | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [pollResult, setPollResult] = useState("");
  const [comparison, setComparison] = useState<Record<string, Record<string, number>>>({});
  const [showForm, setShowForm] = useState(false);
  const [form] = Form.useForm();
  const [selectedAlgos, setSelectedAlgos] = useState<string[]>([]);
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [creating, setCreating] = useState(false);

  const loadExperiments = useCallback(() => {
    api.get<Experiment[]>("/api/experiments").then(setExperiments).catch((e) => setError(String(e)));
  }, []);

  const loadRuns = useCallback((expId: string) => {
    setSelectedExp(expId);
    setComparison({});
    api.getExperimentRuns(expId).then((loadedRuns) => {
      setRuns(loadedRuns);
      const hasPending = loadedRuns.some((r) => r.status === "queued" || r.status === "running");
      setAutoRefresh(hasPending);
      const succeeded = loadedRuns.filter((r) => r.status === "succeeded");
      const uniqueAlgos = new Set(succeeded.map((r) => r.algorithm_id));
      if (uniqueAlgos.size > 1) {
        api.getExperimentReport(expId).then((report) => setComparison(report.comparison_summary || {})).catch(() => {});
      }
    }).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    api.get<Algorithm[]>("/api/algorithms").then(setAlgorithms).catch(() => {});
    api.get<Dataset[]>("/api/datasets").then(setDatasets).catch(() => {});
  }, []);

  useEffect(() => { loadExperiments(); }, [loadExperiments]);

  useEffect(() => {
    if (autoRefresh && selectedExp) {
      intervalRef.current = setInterval(() => {
        api.getExperimentRuns(selectedExp).then((loadedRuns) => {
          setRuns(loadedRuns);
          const hasPending = loadedRuns.some((r) => r.status === "queued" || r.status === "running");
          if (!hasPending) {
            setAutoRefresh(false);
            const succeeded = loadedRuns.filter((r) => r.status === "succeeded");
            const uniqueAlgos = new Set(succeeded.map((r) => r.algorithm_id));
            if (uniqueAlgos.size > 1) {
              api.getExperimentReport(selectedExp).then((report) => setComparison(report.comparison_summary || {})).catch(() => {});
            }
          }
          loadExperiments();
        }).catch(() => {});
      }, 3000);
    }
    return () => { if (intervalRef.current) { clearInterval(intervalRef.current); intervalRef.current = null; } };
  }, [autoRefresh, selectedExp, loadExperiments]);

  const handlePoll = () => {
    api.triggerWorkerPoll().then((r: WorkerPollResponse) => {
      setPollResult(`Processed ${r.processed} run(s)`);
      loadExperiments();
      if (selectedExp) loadRuns(selectedExp);
    }).catch((e) => setPollResult(`Error: ${String(e)}`));
  };

  const handleCreateExperiment = async () => {
    try {
      const values = await form.validateFields();
      if (selectedAlgos.length === 0) { message.error(t("experiments.selectAlgorithmsHint")); return; }
      setCreating(true);
      const exp = await api.post<{ experiment_id: string }>("/api/experiments", {
        name: values.name,
        task_type: values.taskType || "domain_detection",
        algorithm_ids: selectedAlgos,
        dataset_id: values.datasetId || undefined,
        parameters: {},
      });
      message.success(t("common.success"));
      setShowForm(false);
      form.resetFields();
      setSelectedAlgos([]);
      loadExperiments();
      loadRuns(exp.experiment_id);
    } catch (e) {
      if (e && typeof e === "object" && "errorFields" in e) return;
      setError(String(e));
    } finally {
      setCreating(false);
    }
  };

  const completedRuns = runs.filter((r) => r.status === "succeeded").length;
  const totalRuns = runs.length;
  const progressPercent = totalRuns > 0 ? Math.round((completedRuns / totalRuns) * 100) : 0;

  // Comparison chart
  const comparisonMetricNames = Array.from(new Set(Object.values(comparison).flatMap((m) => Object.keys(m)))).sort();
  const comparisonAlgos = Object.keys(comparison);
  const comparisonBarOption = comparisonMetricNames.length > 0 ? {
    tooltip: { trigger: "axis" as const },
    legend: { top: 0 },
    grid: { top: 40, bottom: 30 },
    xAxis: { type: "category" as const, data: comparisonAlgos },
    yAxis: { type: "value" as const },
    series: comparisonMetricNames.map((metric) => ({
      name: t(`metrics.${metric}`, metric),
      type: "bar" as const,
      data: comparisonAlgos.map((algo) => comparison[algo]?.[metric] ?? 0),
    })),
  } : null;

  const expColumns = [
    { title: t("common.id"), dataIndex: "experiment_id", key: "id", render: (v: string) => v.slice(0, 8) + "..." },
    { title: t("common.name"), dataIndex: "name", key: "name" },
    { title: t("algorithms.taskType"), dataIndex: "task_type", key: "task_type" },
    { title: t("common.status"), dataIndex: "status", key: "status", render: (s: string) => <StatusTag status={s} /> },
    { title: t("dashboard.runs"), dataIndex: "run_count", key: "runs" },
    {
      title: t("common.actions"), key: "actions",
      render: (_: unknown, e: Experiment) => (
        <Space>
          <Button size="small" type="primary" onClick={() => loadRuns(e.experiment_id)}>{t("common.view")}</Button>
          <Link to={`/reports/${e.experiment_id}`}><Button size="small">{t("dashboard.report")}</Button></Link>
        </Space>
      ),
    },
  ];

  const runColumns = [
    { title: t("dashboard.runId"), dataIndex: "run_id", key: "id", render: (v: string) => v.slice(0, 12) + "..." },
    { title: t("dashboard.algorithm"), dataIndex: "algorithm_id", key: "algo" },
    { title: t("common.status"), dataIndex: "status", key: "status", render: (s: string) => <StatusTag status={s} /> },
    { title: t("runDetail.startedAt"), dataIndex: "started_at", key: "started", render: (v: string | null) => v ? new Date(v).toLocaleTimeString() : "-" },
    { title: t("runDetail.finishedAt"), dataIndex: "finished_at", key: "finished", render: (v: string | null) => v ? new Date(v).toLocaleTimeString() : "-" },
    { title: t("common.details"), key: "details", render: (_: unknown, r: Run) => <Link to={`/runs/${r.run_id}`}>{t("common.view")}</Link> },
  ];

  return (
    <div>
      <h2 style={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, marginBottom: 24 }}>{t("experiments.title")}</h2>
      {error && <div style={{ color: "#DC2626", marginBottom: 16 }}>{error}</div>}

      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" icon={<PlayCircleOutlined />} onClick={handlePoll}>Run Worker</Button>
        <Button icon={<PlusOutlined />} onClick={() => setShowForm(!showForm)}>{showForm ? t("common.cancel") : t("experiments.create")}</Button>
        {datasets.length === 0 && <Button onClick={() => api.registerAllDemoDatasets().then(() => api.get<Dataset[]>("/api/datasets").then(setDatasets))}>Register Demo Datasets</Button>}
        {autoRefresh && <Badge status="processing" text={<span style={{ color: "#1E40AF" }}>Auto-refreshing...</span>} />}
        {pollResult && <span style={{ color: "#64748B" }}>{pollResult}</span>}
      </Space>

      {showForm && (
        <Card size="small" style={{ marginBottom: 16 }}>
          <Form form={form} layout="vertical" style={{ maxWidth: 500 }}>
            <Form.Item name="name" label={t("experiments.experimentName")} rules={[{ required: true }]}>
              <Input />
            </Form.Item>
            <Form.Item name="taskType" label={t("algorithms.taskType")} initialValue="domain_detection">
              <Select options={[{ value: "domain_detection", label: "Domain Detection" }, { value: "quality_control", label: "Quality Control" }, { value: "deconvolution", label: "Deconvolution" }]} />
            </Form.Item>
            <Form.Item name="datasetId" label={t("experiments.selectDataset")}>
              <Select allowClear placeholder={t("experiments.selectDatasetHint")} options={datasets.map((d) => ({ value: d.dataset_id, label: `${d.name} (${d.platform})` }))} />
            </Form.Item>
            <Form.Item label={t("experiments.selectAlgorithms")}>
              <Checkbox.Group value={selectedAlgos} onChange={(v) => setSelectedAlgos(v as string[])} style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {algorithms.map((a) => <Checkbox key={a.algorithm_id} value={a.algorithm_id}>{a.algorithm_id}</Checkbox>)}
              </Checkbox.Group>
            </Form.Item>
            <Button type="primary" onClick={handleCreateExperiment} loading={creating}>{t("experiments.create")}</Button>
          </Form>
        </Card>
      )}

      <Card size="small">
        <Table dataSource={experiments} columns={expColumns} rowKey="experiment_id" size="small" />
      </Card>
      {experiments.length === 0 && !error && <p style={{ marginTop: 16, color: "#64748B" }}>{t("experiments.noExperiments")}</p>}

      {selectedExp && runs.length > 0 && (
        <Card size="small" style={{ marginTop: 24 }} title={<span>Runs for Experiment {selectedExp.slice(0, 8)}...</span>}>
          {totalRuns > 0 && (
            <div style={{ marginBottom: 16 }}>
              <span style={{ marginRight: 16, color: "#64748B" }}>{t("experiments.progress")}</span>
              <Progress percent={progressPercent} format={() => t("experiments.completed", { completed: completedRuns, total: totalRuns })} />
            </div>
          )}
          <Table dataSource={runs} columns={runColumns} rowKey="run_id" pagination={false} size="small" />
        </Card>
      )}

      {comparisonBarOption && (
        <Card size="small" style={{ marginTop: 24 }} title={t("experiments.comparisonChart")}>
          <ReactECharts option={comparisonBarOption} style={{ height: 320 }} />
        </Card>
      )}
    </div>
  );
}
