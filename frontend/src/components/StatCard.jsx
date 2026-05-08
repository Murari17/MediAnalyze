import React from "react";

const StatCard = ({ label, value, helper, icon }) => {
  return (
    <div className="rounded-xl border border-[#e7e5e4] bg-white p-5 shadow-sm dark:border-slate-800 dark:bg-[#111827]">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium text-[#52525b] dark:text-slate-400">
          {label}
        </p>
        {icon ? <span className="text-slate-400">{icon}</span> : null}
      </div>
      <p className="mt-2 text-2xl font-semibold text-[#18181b] dark:text-white">
        {value}
      </p>
      {helper ? (
        <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">{helper}</p>
      ) : null}
    </div>
  );
};

export default StatCard;
