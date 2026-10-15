import { cn } from "../../lib/format";

export function Card({ className, children, ...props }) {
  return (
    <section
      className={cn(
        "rounded-2xl border border-slate-200 bg-white shadow-card dark:border-white/10 dark:bg-slate-900/60 dark:shadow-none",
        className,
      )}
      {...props}
    >
      {children}
    </section>
  );
}

export function CardHeader({ title, description, icon: Icon, actions, className }) {
  return (
    <div
      className={cn(
        "flex flex-wrap items-start justify-between gap-3 px-5 pb-4 pt-5 sm:px-6",
        className,
      )}
    >
      <div className="flex min-w-0 items-start gap-3">
        {Icon && (
          <span className="mt-0.5 flex size-9 shrink-0 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 dark:bg-indigo-500/10 dark:text-indigo-300">
            <Icon aria-hidden="true" className="size-[18px]" />
          </span>
        )}
        <div className="min-w-0">
          <h2 className="text-base font-semibold tracking-tight text-slate-900 dark:text-white">
            {title}
          </h2>
          {description && (
            <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
              {description}
            </p>
          )}
        </div>
      </div>
      {actions && <div className="flex flex-wrap items-center gap-2">{actions}</div>}
    </div>
  );
}

export function CardBody({ className, children }) {
  return <div className={cn("px-5 pb-5 sm:px-6 sm:pb-6", className)}>{children}</div>;
}
