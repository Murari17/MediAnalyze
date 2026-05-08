import React from "react";

const VARIANTS = {
  success:
    "bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-500/10 dark:text-emerald-300 dark:border-emerald-500/20",
  warning:
    "bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-500/10 dark:text-amber-300 dark:border-amber-500/20",
  danger:
    "bg-red-50 text-red-700 border border-red-200 dark:bg-red-500/10 dark:text-red-300 dark:border-red-500/20",
  info:
    "bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-700/30 dark:text-slate-200 dark:border-slate-600/30",
  neutral:
    "bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-700/30 dark:text-slate-200 dark:border-slate-600/30"
};

const Badge = ({ label, variant = "info", className = "" }) => {
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-medium ${
        VARIANTS[variant] || VARIANTS.info
      } ${className}`}
    >
      {label}
    </span>
  );
};

export default Badge;
