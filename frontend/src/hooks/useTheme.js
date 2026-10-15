import { useEffect, useState } from "react";

const STORAGE_KEY = "mm-theme";

function readSaved() {
  try {
    return localStorage.getItem(STORAGE_KEY) || "system";
  } catch {
    return "system";
  }
}

/** theme is "light" | "dark" | "system" */
export function useTheme() {
  const [theme, setTheme] = useState(readSaved);

  useEffect(() => {
    const root = document.documentElement;
    const media = window.matchMedia("(prefers-color-scheme: dark)");

    function apply() {
      const dark = theme === "dark" || (theme === "system" && media.matches);
      root.classList.toggle("dark", dark);
      root.style.colorScheme = dark ? "dark" : "light";
    }

    apply();
    media.addEventListener("change", apply);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      /* storage unavailable: the choice just won't persist */
    }
    return () => media.removeEventListener("change", apply);
  }, [theme]);

  return { theme, setTheme };
}
