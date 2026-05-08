import React from "react";
import SectionHeader from "./SectionHeader";

const TONE_STYLES = {
  neutral: "border-[#e7e5e4] bg-white dark:bg-[#111827] dark:border-[#1f2937]",
  success: "border-emerald-200 bg-white dark:bg-[#111827] dark:border-[#1f2937]",
  warning: "border-amber-200 bg-white dark:bg-[#111827] dark:border-[#1f2937]",
  danger: "border-red-200 bg-white dark:bg-[#111827] dark:border-[#1f2937]",
  info: "border-slate-200 bg-white dark:bg-[#111827] dark:border-[#1f2937]"
};

const Card = ({
  title,
  icon,
  children,
  badge,
  badgeVariant = "info",
  tone = "neutral",
  prominent = false,
  actions,
  className = ""
}) => {
  return (
    <section
      className={`rounded-xl border p-6 shadow-sm ${
        TONE_STYLES[tone] || TONE_STYLES.neutral
      } ${prominent ? "col-span-12" : ""} ${className}`}
    >
      {title ? (
        <SectionHeader
          icon={icon}
          title={title}
          badgeLabel={badge}
          badgeVariant={badgeVariant}
          actions={actions}
        />
      ) : null}
      {title ? <div className="my-4 h-px bg-slate-100 dark:bg-slate-800" /> : null}
      <div className="space-y-3">{children}</div>
    </section>
  );
};

export default Card;
