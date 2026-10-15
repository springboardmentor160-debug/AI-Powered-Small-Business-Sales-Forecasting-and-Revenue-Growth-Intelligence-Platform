import { AlertTriangle, CheckCircle2, Info, X, XCircle } from "lucide-react";
import { cn } from "../../lib/format";

const VARIANTS = {
  error: {
    icon: XCircle,
    box: "border-rose-200 bg-rose-50 text-rose-800 dark:border-rose-400/20 dark:bg-rose-500/10 dark:text-rose-200",
    icn: "text-rose-500 dark:text-rose-300",
  },
  success: {
    icon: CheckCircle2,
    box: "border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-400/20 dark:bg-emerald-500/10 dark:text-emerald-200",
    icn: "text-emerald-500 dark:text-emerald-300",
  },
  warning: {
    icon: AlertTriangle,
    box: "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-400/20 dark:bg-amber-500/10 dark:text-amber-200",
    icn: "text-amber-500 dark:text-amber-300",
  },
  info: {
    icon: Info,
    box: "border-indigo-200 bg-indigo-50 text-indigo-900 dark:border-indigo-400/20 dark:bg-indigo-500/10 dark:text-indigo-200",
    icn: "text-indigo-500 dark:text-indigo-300",
  },
};

export default function Alert({
  variant = "info",
  title,
  children,
  action,
  onDismiss,
  className,
}) {
  const { icon: Icon, box, icn } = VARIANTS[variant];
  return (
    <div
      role={variant === "error" ? "alert" : "status"}
      className={cn("flex items-start gap-3 rounded-xl border px-4 py-3 text-sm", box, className)}
    >
      <Icon aria-hidden="true" className={cn("mt-0.5 size-4 shrink-0", icn)} />
      <div className="min-w-0 flex-1">
        {title && <p className="font-semibold">{title}</p>}
        {children && <div className={title ? "mt-0.5 opacity-90" : ""}>{children}</div>}
      </div>
      {action}
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss"
          className="-m-1 rounded-md p-1 opacity-70 transition hover:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-current"
        >
          <X aria-hidden="true" className="size-4" />
        </button>
      )}
    </div>
  );
}
