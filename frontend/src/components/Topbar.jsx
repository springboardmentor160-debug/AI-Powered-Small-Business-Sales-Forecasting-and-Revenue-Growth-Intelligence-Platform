import { LogOut } from "lucide-react";
import { initials, prettyRole } from "../lib/format";
import BrandMark from "./BrandMark";
import ThemeToggle from "./ThemeToggle";
import Badge from "./ui/Badge";
import Button from "./ui/Button";
import Skeleton from "./ui/Skeleton";
import Tooltip from "./ui/Tooltip";

export default function Topbar({ user, signedIn, loadingUser, theme, onThemeChange, onSignOut }) {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur-xl dark:border-white/10 dark:bg-slate-950/70">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <BrandMark />
          <h1 className="text-base font-semibold tracking-tight text-slate-900 dark:text-white">
            MarketMind AI
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <ThemeToggle theme={theme} onChange={onThemeChange} />

          {signedIn && (
            <>
              <span aria-hidden="true" className="hidden h-6 w-px bg-slate-200 dark:bg-white/10 sm:block" />
              {user ? (
                <div className="flex items-center gap-2.5">
                  <span
                    aria-hidden="true"
                    className="flex size-9 items-center justify-center rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 text-xs font-bold text-white"
                  >
                    {initials(user.name)}
                  </span>
                  <div className="hidden min-w-0 sm:block">
                    <p className="truncate text-sm font-semibold leading-tight text-slate-900 dark:text-white">
                      {user.name}
                    </p>
                    <Badge tone="brand" className="mt-0.5 px-1.5 py-0 text-[11px]">
                      {prettyRole(user.role)}
                    </Badge>
                  </div>
                </div>
              ) : (
                loadingUser && (
                  <div className="flex items-center gap-2.5" aria-hidden="true">
                    <Skeleton className="size-9 rounded-full" />
                    <Skeleton className="hidden h-8 w-28 sm:block" />
                  </div>
                )
              )}
              <Tooltip content="Sign out" side="bottom" align="end">
                <Button variant="secondary" size="icon" aria-label="Sign out" onClick={onSignOut}>
                  <LogOut aria-hidden="true" className="size-4" />
                </Button>
              </Tooltip>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
