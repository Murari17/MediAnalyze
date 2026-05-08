import React from "react";
import { Link } from "react-router-dom";
import { Activity, AlertTriangle, Clock, FileText, ShieldCheck } from "lucide-react";
import Button from "../components/Button";
import Card from "../components/Card";
import StatCard from "../components/StatCard";

const stats = [
  {
    label: "Documents analyzed",
    value: "0",
    helper: "Last 30 days",
    icon: <FileText className="h-4 w-4" />
  },
  {
    label: "High severity",
    value: "0",
    helper: "Awaiting review",
    icon: <AlertTriangle className="h-4 w-4" />
  },
  {
    label: "Avg confidence",
    value: "--",
    helper: "Across analyses",
    icon: <Activity className="h-4 w-4" />
  },
  {
    label: "Decision latency",
    value: "--",
    helper: "Median response",
    icon: <Clock className="h-4 w-4" />
  }
];

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <h2 className="text-2xl font-semibold tracking-tight text-[#18181b] dark:text-white">
            Operational overview
          </h2>
          <p className="text-sm text-[#52525b] dark:text-slate-400">
            Track regulatory analysis volume, severity, and decision readiness.
          </p>
        </div>
        <Link to="/analyze">
          <Button>Analyze document</Button>
        </Link>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <StatCard key={stat.label} {...stat} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Getting started" icon={<ShieldCheck className="h-4 w-4" />}>
          <div className="space-y-3 text-sm text-[#52525b] dark:text-slate-300">
            <div>1. Upload or paste a clinical or regulatory document.</div>
            <div>2. Run the AI analysis to extract key fields and severity.</div>
            <div>3. Review the decision recommendation and evidence.</div>
          </div>
        </Card>
        <Card title="Recent analyses" icon={<Clock className="h-4 w-4" />}>
          <p className="text-sm text-[#52525b] dark:text-slate-400">
            No activity yet. Run your first analysis to populate this feed.
          </p>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
