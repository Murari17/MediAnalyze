import React from "react";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

const AppShell = ({ children, darkMode, onToggleDark }) => {
  return (
    <div className="min-h-screen bg-[#f5f5f4] text-[#18181b] dark:bg-[#0b1220] dark:text-slate-100">
      <div className="flex">
        <Sidebar />
        <div className="flex min-h-screen w-full flex-col">
          <Topbar darkMode={darkMode} onToggleDark={onToggleDark} />
          <main className="flex-1 bg-[#f5f5f4] px-6 py-6 dark:bg-[#0b1220] md:px-8">
            <div className="mx-auto w-full max-w-[1200px]">{children}</div>
          </main>
        </div>
      </div>
    </div>
  );
};

export default AppShell;
