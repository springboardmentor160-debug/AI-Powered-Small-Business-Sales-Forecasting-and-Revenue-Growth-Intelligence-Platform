import { Monitor, Moon, Sun } from "lucide-react";
import { cn } from "../lib/format";
import Tooltip from "./ui/Tooltip";

const OPTIONS = [
  { value: "light", label: "Light", icon: Sun },
  { value: "system", label: "Match system", icon: Monitor },
  { value: "dark", label: "Dark", icon: Moon },
];

export default function ThemeToggle({ theme, onChange }) {
  return (
    <div
      role="radiogroup"
      aria-label="Colour theme"
      className="flex items-center gap-0.5 rounded-lg border border-slate-200 bg-slate-100/70 p-0.5 dark:border-white/10 dark:bg-white/5"
    >
      {OPTIONS.map(({ value, label, icon: Icon }) => {
        const selected = theme === value;
        return (
          <Tooltip key={value} content={label} side="bottom">
            <button
              type="button"
              role="radio"
              aria-checked={selected}
              aria-label={label}
              onClick={() => onChange(value)}
              className={cn(
                "flex size-7 items-center justify-center rounded-md transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500",
                selected
                  ? "bg-white text-indigo-600 shadow-sm dark:bg-slate-700 dark:text-white"
                  : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white",
              )}
            >
              <Icon aria-hidden="true" className="size-4" />
            </button>
          </Tooltip>
        );
      })}
    </div>
  );
}
