import { Tag } from "antd";
import { useTranslation } from "react-i18next";

const colorMap: Record<string, string> = {
  queued: "default",
  running: "processing",
  succeeded: "success",
  failed: "error",
  created: "default",
};

export default function StatusTag({ status }: { status: string }) {
  const { t } = useTranslation();
  return <Tag color={colorMap[status] || "default"}>{t(`status.${status}`, status)}</Tag>;
}
