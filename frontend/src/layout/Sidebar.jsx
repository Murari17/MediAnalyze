import React from "react";
import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FileText,
  History,
  Settings,
  ShieldCheck
} from "lucide-react";

const navItems = [
  { label: "Dashboard", icon: LayoutDashboard, to: "/dashboard" },
  { label: "Analyze Document", icon: FileText, to: "/analyze" },
  { label: "History", icon: History, to: "/history" },
  { label: "Settings", icon: Settings, to: "/settings" }
];

const Sidebar = () => {
  return (
    <aside className="hidden min-h-screen w-64 flex-col bg-[#18181b] px-6 py-6 text-slate-100 lg:flex">
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white/10 text-slate-200">
          <ShieldCheck className="h-5 w-5" />
        </div>
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.32em] text-slate-400">
            Workspace
          </p>
          <span className="text-base font-semibold">MedIntel AI</span>
        </div>
      </div>

      <div className="my-6 h-px w-full bg-white/10" />

      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.label}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium ${
                  isActive ? "bg-white/10 text-white" : "text-slate-300"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <div className="mt-auto border-t border-white/10 pt-6 text-xs text-slate-400">
        AI-powered regulatory intelligence
      </div>
    </aside>
  );
};

export default Sidebar;
