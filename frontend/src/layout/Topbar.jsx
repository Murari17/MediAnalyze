import React from "react";
import { Search } from "lucide-react";

const Topbar = () => {
  return (
    <header className="border-b border-[#e7e5e4] bg-[#fafaf9] px-6 py-4 dark:border-slate-800 dark:bg-[#0b1220]">
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div className="space-y-1">
          <h1 className="text-xl font-semibold tracking-tight text-[#18181b] dark:text-slate-100">
            Dashboard
          </h1>
          <p className="text-sm text-[#52525b] dark:text-slate-400">
            AI regulatory document analysis
          </p>
        </div>

        <div className="flex flex-1 items-center justify-between gap-3 md:justify-end">
          <div className="relative w-full max-w-xs">
            <span className="absolute inset-y-0 left-3 flex items-center">
              <Search className="h-4 w-4 text-slate-400" />
            </span>
            <input
              placeholder="Search documents"
              className="w-full rounded-full border border-[#e7e5e4] bg-[#f5f5f4] py-2 pl-10 pr-4 text-sm text-[#52525b] focus:border-[#d6d3d1] focus:outline-none dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200"
            />
          </div>
          <div className="h-9 w-9 rounded-full bg-slate-200 dark:bg-slate-800" />
        </div>
      </div>
    </header>
  );
};

export default Topbar;
