import React from "react";
import { Navigate, Route, Routes, Outlet } from "react-router-dom";
import AppShell from "./layout/AppShell";
import useDarkMode from "./hooks/useDarkMode";
import Landing from "./pages/Landing";
import Dashboard from "./pages/Dashboard";
import Analyze from "./pages/Analyze";
import History from "./pages/History";
import Settings from "./pages/Settings";

const AppLayout = ({ darkMode, onToggleDark }) => {
  return (
    <AppShell darkMode={darkMode} onToggleDark={onToggleDark}>
      <Outlet />
    </AppShell>
  );
};

const App = () => {
  const [darkMode, setDarkMode] = useDarkMode();

  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<AppLayout darkMode={darkMode} onToggleDark={() => setDarkMode((prev) => !prev)} />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analyze" element={<Analyze />} />
        <Route path="/history" element={<History />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
};

export default App;
