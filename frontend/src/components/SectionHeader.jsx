import React from "react";
import Badge from "./Badge";

const SectionHeader = ({ icon, title, badgeLabel, badgeVariant = "info", actions }) => {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3">
      <div className="flex items-center gap-3">
        {icon ? <span className="text-base text-slate-500">{icon}</span> : null}
        <h3 className="text-base font-semibold tracking-tight text-[#18181b] dark:text-slate-100">
          {title}
        </h3>
      </div>
      <div className="flex items-center gap-2">
        {actions}
        {badgeLabel ? <Badge label={badgeLabel} variant={badgeVariant} /> : null}
      </div>
    </div>
  );
};

export default SectionHeader;
