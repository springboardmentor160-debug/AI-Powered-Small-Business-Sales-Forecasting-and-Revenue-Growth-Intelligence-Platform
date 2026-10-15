import { useEffect, useState } from "react";
import { Eye, EyeOff, Lock, Mail, ShieldCheck, Sparkles, TrendingUp } from "lucide-react";
import BrandMark from "./BrandMark";
import Alert from "./ui/Alert";
import Button from "./ui/Button";
import { Card } from "./ui/Card";
import { Field, Input } from "./ui/Field";

const FEATURES = [
  { icon: ShieldCheck, label: "Role-based access" },
  { icon: TrendingUp, label: "XGBoost forecasting" },
  { icon: Sparkles, label: "Smart recommendations" },
];

export default function AuthScreen({
  email,
  password,
  onEmailChange,
  onPasswordChange,
  onSubmit,
  error,
  notice,
  loading,
}) {
  const [showPassword, setShowPassword] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [slow, setSlow] = useState(false);

  // If sign-in is slow, tell people the server may just be waking up.
  useEffect(() => {
    if (!loading) {
      setSlow(false);
      return undefined;
    }
    const timer = setTimeout(() => setSlow(true), 4000);
    return () => clearTimeout(timer);
  }, [loading]);

  const emailInvalid = submitted && !email.trim();
  const passwordInvalid = submitted && !password;

  function handleSubmit(event) {
    setSubmitted(true);
    onSubmit(event);
  }

  return (
    <main className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-md flex-col justify-center px-4 py-10">
      <div className="mb-8 text-center">
        <BrandMark className="mx-auto mb-5 size-12 rounded-2xl text-xl" />
        <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
          Welcome back
        </h2>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Sign in to see your sales, stock and customer insights.
        </p>
      </div>

      <Card className="p-6 shadow-pop sm:p-8">
        <form onSubmit={handleSubmit} noValidate className="space-y-5">
          {notice && <Alert variant="warning">{notice}</Alert>}
          {error && (
            <Alert variant="error" title="Couldn't sign you in">
              {error}
            </Alert>
          )}

          <Field
            label="Email address"
            htmlFor="login-email"
            error={emailInvalid ? "Enter your email address." : undefined}
          >
            <Input
              id="login-email"
              type="email"
              autoComplete="email"
              icon={Mail}
              placeholder="you@company.com"
              value={email}
              invalid={emailInvalid}
              aria-describedby={emailInvalid ? "login-email-error" : undefined}
              onChange={(event) => onEmailChange(event.target.value)}
              autoFocus
            />
          </Field>

          <Field
            label="Password"
            htmlFor="login-password"
            error={passwordInvalid ? "Enter your password." : undefined}
          >
            <Input
              id="login-password"
              type={showPassword ? "text" : "password"}
              autoComplete="current-password"
              icon={Lock}
              placeholder="Your password"
              value={password}
              invalid={passwordInvalid}
              aria-describedby={passwordInvalid ? "login-password-error" : undefined}
              onChange={(event) => onPasswordChange(event.target.value)}
              trailing={
                <button
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                  aria-pressed={showPassword}
                  className="flex size-8 items-center justify-center rounded-md text-slate-400 transition-colors hover:text-slate-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-indigo-500 dark:hover:text-slate-200"
                >
                  {showPassword ? (
                    <EyeOff aria-hidden="true" className="size-4" />
                  ) : (
                    <Eye aria-hidden="true" className="size-4" />
                  )}
                </button>
              }
            />
          </Field>

          <Button type="submit" loading={loading} className="h-11 w-full">
            {loading ? "Signing in…" : "Sign in"}
          </Button>

          {slow && (
            <p role="status" className="text-center text-xs text-slate-500 dark:text-slate-400">
              Still working. The server may be waking up, which can take a few seconds.
            </p>
          )}
        </form>
      </Card>

      <ul className="mt-8 flex flex-wrap justify-center gap-x-5 gap-y-2 text-xs font-medium text-slate-500 dark:text-slate-400">
        {FEATURES.map(({ icon: Icon, label }) => (
          <li key={label} className="inline-flex items-center gap-1.5">
            <Icon aria-hidden="true" className="size-3.5 text-indigo-500 dark:text-indigo-300" />
            {label}
          </li>
        ))}
      </ul>
    </main>
  );
}
