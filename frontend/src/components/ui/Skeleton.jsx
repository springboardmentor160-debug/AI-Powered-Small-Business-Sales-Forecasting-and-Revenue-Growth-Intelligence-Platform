import { cn } from "../../lib/format";

export default function Skeleton({ className }) {
  return (
    <div
      aria-hidden="true"
      className={cn(
        "animate-pulse rounded-md bg-slate-200/80 motion-reduce:animate-none dark:bg-white/10",
        className,
      )}
    />
  );
}
