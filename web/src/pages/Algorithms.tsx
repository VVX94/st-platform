import { useEffect, useState } from "react";
import { Table, Tag, Card, Tooltip } from "antd";
import { CheckCircleOutlined, CloseCircleOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { api } from "../api/client";

interface Algorithm {
  algorithm_id: string;
  name: string;
  task_type: string;
  runtime: string;
  version: string;
  description: string;
  tags: string[];
  available: boolean;
}

const familyColors: Record<string, string> = {
  spagcn: "blue",
  stagate: "purple",
  spaceflow: "cyan",
  ccst: "green",
  const: "orange",
  deepst: "magenta",
  graphst: "geekblue",
  sedr: "volcano",
  mock: "default",
};

function getAlgoColor(id: string): string {
  for (const [family, color] of Object.entries(familyColors)) {
    if (id.toLowerCase().includes(family)) return color;
  }
  return "default";
}

export default function Algorithms() {
  const { t } = useTranslation();
  const [algorithms, setAlgorithms] = useState<Algorithm[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get<Algorithm[]>("/api/algorithms").then(setAlgorithms).catch((e) => setError(String(e)));
  }, []);

  const taskTypeGroups = algorithms.reduce<Record<string, Algorithm[]>>((acc, algo) => {
    if (!acc[algo.task_type]) acc[algo.task_type] = [];
    acc[algo.task_type].push(algo);
    return acc;
  }, {});

  const columns = [
    { title: t("common.id"), dataIndex: "algorithm_id", key: "id" },
    {
      title: t("common.name"), dataIndex: "name", key: "name",
      render: (name: string, record: Algorithm) => (
        <span>
          <Tag color={getAlgoColor(record.algorithm_id)}>{name}</Tag>
          {record.available ? (
            <Tooltip title="Available"><CheckCircleOutlined style={{ color: "#16A34A", fontSize: 14 }} /></Tooltip>
          ) : (
            <Tooltip title="Missing dependencies"><CloseCircleOutlined style={{ color: "#DC2626", fontSize: 14 }} /></Tooltip>
          )}
        </span>
      ),
    },
    { title: t("algorithms.taskType"), dataIndex: "task_type", key: "task_type" },
    { title: t("algorithms.runtime"), dataIndex: "runtime", key: "runtime" },
    { title: t("common.version"), dataIndex: "version", key: "version" },
    {
      title: t("common.tags"), dataIndex: "tags", key: "tags",
      render: (tags: string[]) => tags.map((tag) => <Tag key={tag} style={{ marginRight: 4 }}>{tag}</Tag>),
    },
  ];

  return (
    <div>
      <h2 style={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, marginBottom: 24 }}>{t("algorithms.title")}</h2>
      {error && <div style={{ color: "#DC2626", marginBottom: 16 }}>{error}</div>}

      {Object.keys(taskTypeGroups).length > 0 && (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
          {Object.entries(taskTypeGroups).map(([taskType, algos]) => {
            const available = algos.filter((a) => a.available).length;
            return (
              <Tag key={taskType} color="blue">
                {taskType}: {available}/{algos.length} available
              </Tag>
            );
          })}
        </div>
      )}

      <Card size="small">
        <Table
          dataSource={algorithms}
          columns={columns}
          rowKey="algorithm_id"
          size="small"
          expandable={{
            expandedRowRender: (record) => (
              <div style={{ padding: "8px 0" }}>
                <p><strong>{t("common.description")}:</strong> {record.description || t("algorithms.noDescription")}</p>
                <p><strong>{t("algorithms.supportsTask")}:</strong> {record.task_type}</p>
                {!record.available && <p style={{ color: "#DC2626" }}>Dependencies not installed. Install the required package to enable this algorithm.</p>}
              </div>
            ),
          }}
        />
      </Card>
      {algorithms.length === 0 && !error && <p>{t("common.loading")}</p>}
    </div>
  );
}
