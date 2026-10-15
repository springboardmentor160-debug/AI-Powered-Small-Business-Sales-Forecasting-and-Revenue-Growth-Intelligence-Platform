import { useRef } from "react";
import { cn } from "../../lib/format";
import Badge from "./Badge";

/**
 * tabs: [{ id, label, icon?, count?, countTone? }]
 * Panels should use id={`panel-${id}`} and aria-labelledby={`tab-${id}`}.
 */
export default function Tabs({ tabs, value, onChange, label = "Dashboard sections" }) {
  const refs = useRef({});

  function onKeyDown(event, index) {
    const last = tabs.length - 1;
    const next = {
      ArrowRight: index === last ? 0 : index + 1,
      ArrowLeft: index === 0 ? last : index - 1,
      Home: 0,
      End: last,
    }[event.key];
    if (next === undefined) return;
    event.preventDefault();
    onChange(tabs[next].id);
    refs.current[tabs[next].id]?.focus();
  }

  return (
    <div
      role="tablist"
      aria-label={label}
      className="-mb-px flex gap-1 overflow-x-auto [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      {tabs.map((tab, index) => {
        const selected = tab.id === value;
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            ref={(el) => {
              refs.current[tab.id] = el;
            }}
            role="tab"
            id={`tab-${tab.id}`}
            type="button"
            aria-selected={selected}
            aria-controls={`panel-${tab.id}`}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(tab.id)}
            onKeyDown={(event) => onKeyDown(event, index)}
            className={cn(
              "relative inline-flex shrink-0 items-center gap-2 rounded-t-lg px-3.5 py-3 text-sm font-semibold transition-colors motion-reduce:transition-none",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-indigo-500",
              selected
                ? "text-indigo-600 dark:text-indigo-300"
                : "text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white",
            )}
          >
            {Icon && <Icon aria-hidden="true" className="size-4" />}
            {tab.label}
            {tab.count !== undefined && tab.count !== null && (
              <Badge tone={tab.countTone ?? "neutral"} className="px-1.5 py-0">
                {tab.count}
              </Badge>
            )}
            <span
              aria-hidden="true"
              className={cn(
                "absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500 transition-opacity motion-reduce:transition-none",
                selected ? "opacity-100" : "opacity-0",
              )}
            />
          </button>
        );
      })}
    </div>
  );
}
