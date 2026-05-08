import { useEffect, useState } from "react";

const useDarkMode = () => {
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    const root = document.documentElement;
    if (enabled) {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
  }, [enabled]);

  return [enabled, setEnabled];
};

export default useDarkMode;
