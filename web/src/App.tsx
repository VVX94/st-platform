import { BrowserRouter, Link, Route, Routes } from "react-router-dom";
import Algorithms from "./pages/Algorithms";
import Dashboard from "./pages/Dashboard";
import Datasets from "./pages/Datasets";
import Experiments from "./pages/Experiments";
import RunDetail from "./pages/RunDetail";

const navStyle: React.CSSProperties = {
  display: "flex",
  gap: "1.5rem",
  padding: "1rem 2rem",
  backgroundColor: "#1a1a2e",
  color: "#fff",
  alignItems: "center",
};

const linkStyle: React.CSSProperties = {
  color: "#e0e0e0",
  textDecoration: "none",
  fontSize: "0.95rem",
};

const bodyStyle: React.CSSProperties = {
  maxWidth: "960px",
  margin: "2rem auto",
  padding: "0 1rem",
  fontFamily: "system-ui, -apple-system, sans-serif",
};

export default function App() {
  return (
    <BrowserRouter>
      <nav style={navStyle}>
        <strong style={{ fontSize: "1.1rem", marginRight: "1rem" }}>ST Platform</strong>
        <Link to="/" style={linkStyle}>Dashboard</Link>
        <Link to="/datasets" style={linkStyle}>Datasets</Link>
        <Link to="/algorithms" style={linkStyle}>Algorithms</Link>
        <Link to="/experiments" style={linkStyle}>Experiments</Link>
      </nav>
      <div style={bodyStyle}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/datasets" element={<Datasets />} />
          <Route path="/algorithms" element={<Algorithms />} />
          <Route path="/experiments" element={<Experiments />} />
          <Route path="/runs/:runId" element={<RunDetail />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}
