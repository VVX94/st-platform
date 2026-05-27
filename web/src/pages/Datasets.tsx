import { useEffect, useState } from "react";
import { Table, Button, Card, Modal, Form, Input, Space, message } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
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
  const { t } = useTranslation();
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [error, setError] = useState("");
  const [showRealForm, setShowRealForm] = useState(false);
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const loadDatasets = () => {
    api.get<Dataset[]>("/api/datasets").then(setDatasets).catch((e) => setError(String(e)));
  };

  useEffect(() => { loadDatasets(); }, []);

  const handleRegisterDemo = () => {
    api.registerDemoDataset().then(() => { message.success(t("common.success")); loadDatasets(); }).catch((e) => setError(String(e)));
  };

  const handleRegisterAllDemos = () => {
    api.registerAllDemoDatasets().then(() => { message.success(t("common.success")); loadDatasets(); }).catch((e) => setError(String(e)));
  };

  const handleRegisterReal = async () => {
    try {
      const values = await form.validateFields();
      setLoading(true);
      await api.post("/api/datasets/register-real", {
        name: values.name,
        path: values.path,
        label_column: values.labelColumn || null,
      });
      message.success(t("common.success"));
      setShowRealForm(false);
      form.resetFields();
      loadDatasets();
    } catch (e) {
      if (e && typeof e === "object" && "errorFields" in e) return;
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  const columns = [
    { title: t("common.id"), dataIndex: "dataset_id", key: "id", render: (v: string) => v.slice(0, 8) + "..." },
    { title: t("common.name"), dataIndex: "name", key: "name" },
    { title: t("common.platform"), dataIndex: "platform", key: "platform" },
    { title: t("common.sample"), dataIndex: "sample_id", key: "sample" },
    { title: t("datasets.nObs"), key: "n_obs", render: (_: unknown, d: Dataset) => d.metadata.n_obs !== undefined ? String(d.metadata.n_obs) : "-" },
    { title: t("datasets.nVars"), key: "n_vars", render: (_: unknown, d: Dataset) => d.metadata.n_vars !== undefined ? String(d.metadata.n_vars) : "-" },
    { title: t("datasets.labelColumn"), key: "label", render: (_: unknown, d: Dataset) => d.metadata.label_column ? String(d.metadata.label_column) : "-" },
  ];

  return (
    <div>
      <h2 style={{ fontFamily: "Poppins, sans-serif", fontWeight: 600, marginBottom: 24 }}>{t("datasets.title")}</h2>
      {error && <div style={{ color: "#DC2626", marginBottom: 16 }}>{error}</div>}

      <Space style={{ marginBottom: 16 }}>
        <Button type="primary" onClick={handleRegisterDemo}>{t("datasets.registerDemo")}</Button>
        <Button onClick={handleRegisterAllDemos}>{t("datasets.registerAllDemos")}</Button>
        <Button icon={<PlusOutlined />} onClick={() => setShowRealForm(true)}>{t("datasets.registerReal")}</Button>
      </Space>

      <Modal
        title={t("datasets.registerReal")}
        open={showRealForm}
        onCancel={() => { setShowRealForm(false); form.resetFields(); }}
        onOk={handleRegisterReal}
        confirmLoading={loading}
        okText={t("common.register")}
        cancelText={t("common.cancel")}
      >
        <Form form={form} layout="vertical" style={{ marginTop: 16 }}>
          <Form.Item name="name" label={t("common.name")} rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="path" label={t("datasets.filePath")} rules={[{ required: true }]}>
            <Input placeholder="/path/to/data.h5ad" />
          </Form.Item>
          <Form.Item name="labelColumn" label={t("datasets.labelColumn")}>
            <Input placeholder={t("datasets.labelColumnHint")} />
          </Form.Item>
        </Form>
      </Modal>

      <Card size="small">
        <Table dataSource={datasets} columns={columns} rowKey="dataset_id" size="small" />
      </Card>
      {datasets.length === 0 && !error && <p>{t("datasets.noDatasets")}</p>}
    </div>
  );
}
