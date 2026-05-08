import React from "react";

const VARIANTS = {
  primary:
    "bg-[#18181b] text-white shadow-sm focus:ring-2 focus:ring-[#e7e5e4] dark:focus:ring-slate-700",
  secondary:
    "bg-white text-[#18181b] border border-[#e7e5e4] shadow-sm dark:bg-slate-900 dark:border-slate-700 dark:text-slate-100",
  ghost: "bg-transparent text-[#52525b] dark:text-slate-300"
};

const SIZES = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2 text-sm",
  lg: "px-5 py-2.5 text-sm"
};

const Button = ({
  children,
  className = "",
  variant = "primary",
  size = "md",
  type = "button",
  disabled,
  ...props
}) => {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-md font-medium ${
        VARIANTS[variant] || VARIANTS.primary
      } ${SIZES[size] || SIZES.md} disabled:cursor-not-allowed disabled:opacity-60 ${className}`}
      type={type}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};

export default Button;
