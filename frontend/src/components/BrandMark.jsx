import { cn } from "../lib/format";

export default function BrandMark({ className }) {
  return (
    <span
      aria-hidden="true"
      className={cn(
        "flex size-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-base font-bold text-white shadow-lg shadow-indigo-500/30",
        className,
      )}
    >
      M
    </span>
  );
}
