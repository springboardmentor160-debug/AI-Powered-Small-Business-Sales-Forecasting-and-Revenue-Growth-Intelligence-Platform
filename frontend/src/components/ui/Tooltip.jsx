import { cn } from "../../lib/format";

const SIDES = {
  top: "bottom-full mb-2",
  bottom: "top-full mt-2",
};

const ALIGNS = {
  center: "left-1/2 -translate-x-1/2",
  start: "left-0",
  end: "right-0",
};

/**
 * CSS-only tooltip: shows on hover and on keyboard focus of the wrapped control.
 * Always give icon-only controls their own aria-label as well.
 */
export default function Tooltip({
  content,
  children,
  side = "top",
  align = "center",
  className,
}) {
  return (
    <span className={cn("group/tt relative inline-flex", className)}>
      {children}
      <span
        role="tooltip"
        className={cn(
          "pointer-events-none absolute z-50 w-max max-w-[16rem] rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs font-medium leading-snug text-white opacity-0 shadow-pop ring-1 ring-white/10 transition-opacity duration-150",
          "group-hover/tt:opacity-100 group-focus-within/tt:opacity-100",
          "dark:bg-slate-100 dark:text-slate-900 dark:ring-black/5",
          SIDES[side],
          ALIGNS[align],
        )}
      >
        {content}
      </span>
    </span>
  );
}
