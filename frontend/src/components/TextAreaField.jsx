import React, { useEffect, useRef } from "react";

const TextAreaField = ({ label, value, onChange, placeholder, minRows = 6 }) => {
  const textareaRef = useRef(null);

  const resize = () => {
    if (!textareaRef.current) return;
    textareaRef.current.style.height = "auto";
    textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
  };

  useEffect(() => {
    resize();
  }, [value]);

  return (
    <label className="flex flex-col gap-2 text-sm font-medium text-[#52525b] dark:text-slate-300">
      <span>{label}</span>
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onInput={resize}
        placeholder={placeholder}
        rows={minRows}
        className="w-full resize-none rounded-lg border border-[#e7e5e4] bg-white p-3 text-sm text-[#18181b] shadow-sm outline-none focus:border-[#d6d3d1] dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
      />
    </label>
  );
};

export default TextAreaField;
