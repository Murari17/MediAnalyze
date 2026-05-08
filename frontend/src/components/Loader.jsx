import React from "react";

const Loader = ({ label = "Analyzing document..." }) => {
  const base = "h-3 rounded-full bg-slate-200 dark:bg-slate-700";
  return (
    <div className="space-y-4">
      <p className="text-sm text-[#52525b] dark:text-slate-400">{label}</p>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <div className="col-span-full space-y-3 rounded-xl border border-[#e7e5e4] bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-[#111827]">
          <div className={`${base} w-1/3`} />
          <div className={base} />
          <div className={base} />
        </div>
        {[0, 1, 2, 3].map((item) => (
          <div
            key={item}
            className="space-y-3 rounded-xl border border-[#e7e5e4] bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-[#111827]"
          >
            <div className={`${base} w-1/2`} />
            <div className={base} />
            <div className={base} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default Loader;
