import { cn } from "../../lib/format";

export default function EmptyState({ icon: Icon, title, description, action, className }) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center px-6 py-12 text-center",
        className,
      )}
    >
      {Icon && (
        <span className="mb-4 flex size-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-500 dark:bg-white/5 dark:text-slate-400">
          <Icon aria-hidden="true" className="size-6" />
        </span>
      )}
      <p className="text-sm font-semibold text-slate-900 dark:text-white">{title}</p>
      {description && (
        <p className="mt-1 max-w-sm text-sm text-slate-500 dark:text-slate-400">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
