import { useState } from "react";
import { BrowserRouter, Link, Route, Routes, useLocation } from "react-router-dom";
import { ConfigProvider, Layout, Menu, Button, Space, theme } from "antd";
import {
  DashboardOutlined,
  DatabaseOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  AppstoreOutlined,
  GlobalOutlined,
} from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import zhCN from "antd/locale/zh_CN";
import enUS from "antd/locale/en_US";
import Algorithms from "./pages/Algorithms";
import Dashboard from "./pages/Dashboard";
import Datasets from "./pages/Datasets";
import Experiments from "./pages/Experiments";
import Reports from "./pages/Reports";
import RunDetail from "./pages/RunDetail";

const { Header, Content, Sider } = Layout;

function AppLayout() {
  const { t, i18n } = useTranslation();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const isZh = i18n.language.startsWith("zh");

  const toggleLang = () => {
    const next = isZh ? "en" : "zh";
    i18n.changeLanguage(next);
  };

  const menuItems = [
    { key: "/", icon: <DashboardOutlined />, label: <Link to="/">{t("nav.dashboard")}</Link> },
    { key: "/datasets", icon: <DatabaseOutlined />, label: <Link to="/datasets">{t("nav.datasets")}</Link> },
    { key: "/algorithms", icon: <AppstoreOutlined />, label: <Link to="/algorithms">{t("nav.algorithms")}</Link> },
    { key: "/experiments", icon: <ExperimentOutlined />, label: <Link to="/experiments">{t("nav.experiments")}</Link> },
    { key: "/reports", icon: <BarChartOutlined />, label: <Link to="/reports">{t("nav.reports")}</Link> },
  ];

  const selectedKey = location.pathname.startsWith("/reports/")
    ? "/reports"
    : location.pathname.startsWith("/runs/")
      ? "/experiments"
      : location.pathname;

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        style={{ background: "#1E3A8A" }}
        width={220}
      >
        <div
          style={{
            height: 56,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderBottom: "1px solid rgba(255,255,255,0.1)",
          }}
        >
          <span
            style={{
              color: "#fff",
              fontSize: collapsed ? 16 : 18,
              fontWeight: 700,
              fontFamily: "Poppins, sans-serif",
              letterSpacing: "-0.02em",
            }}
          >
            {collapsed ? "ST" : "ST Platform"}
          </span>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          style={{ background: "transparent", borderRight: 0 }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            display: "flex",
            alignItems: "center",
            justifyContent: "flex-end",
            borderBottom: "1px solid #E5E7EB",
            height: 56,
          }}
        >
          <Space>
            <Button
              icon={<GlobalOutlined />}
              onClick={toggleLang}
              size="small"
            >
              {isZh ? "EN" : "中文"}
            </Button>
          </Space>
        </Header>
        <Content
          style={{
            margin: 24,
            padding: 24,
            background: "#fff",
            borderRadius: 8,
            minHeight: 280,
            maxWidth: 1360,
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/datasets" element={<Datasets />} />
            <Route path="/algorithms" element={<Algorithms />} />
            <Route path="/experiments" element={<Experiments />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/reports/:experimentId" element={<Reports />} />
            <Route path="/runs/:runId" element={<RunDetail />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
}

export default function App() {
  return (
    <ConfigProvider
      locale={undefined}
      theme={{
        algorithm: theme.defaultAlgorithm,
        token: {
          colorPrimary: "#1E40AF",
          borderRadius: 8,
          fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        },
      }}
    >
      <BrowserRouter>
        <AppLayout />
      </BrowserRouter>
    </ConfigProvider>
  );
}
