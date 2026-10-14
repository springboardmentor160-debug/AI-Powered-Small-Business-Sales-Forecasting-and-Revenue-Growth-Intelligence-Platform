import { useEffect, useState, type FormEvent } from "react";
import {
  Activity, ArrowRight, BarChart3, Eye, EyeOff, LockKeyhole, Mail, ShieldCheck, ShoppingBag, Sparkles, TrendingUp, User, UserMinus, ShieldAlert, Users,
} from "lucide-react";
import ParticleField from "./ParticleField";
import { ApiRequestError, login, register, type LoginResponse, type PublicRegistrationRole } from "./lib/api";

interface LoginScreenProps {
  onLoggedIn: (result: LoginResponse, email: string) => void;
  initialMessage?: string;
}

const WORDS = ["forecast demand", "predict churn", "spot anomalies", "recommend products", "segment customers"];
const ROLES: { value: PublicRegistrationRole; label: string }[] = [
  { value: "business_owner", label: "Business owner" },
  { value: "store_manager", label: "Store manager" },
  { value: "sales_executive", label: "Sales executive" },
];
const FEATURES = [
  { icon: TrendingUp, label: "Forecasting" },
  { icon: Users, label: "Segments" },
  { icon: ShoppingBag, label: "Recommendations" },
  { icon: UserMinus, label: "Churn risk" },
  { icon: ShieldAlert, label: "Anomaly alerts" },
  { icon: BarChart3, label: "Executive summary" },
];

export default function LoginScreen({ onLoggedIn, initialMessage = "" }: LoginScreenProps) {
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<PublicRegistrationRole>("business_owner");
  const [show, setShow] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(initialMessage);
  const [notice, setNotice] = useState("");
  const [word, setWord] = useState(0);

  useEffect(() => {
    const t = window.setInterval(() => setWord((w) => (w + 1) % WORDS.length), 2400);
    return () => window.clearInterval(t);
  }, []);

  function switchMode(next: "signin" | "signup") {
    setMode(next); setError(""); setNotice("");
  }

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError(""); setNotice("");

    if (mode === "signup") {
      if (name.trim().length < 2) return setError("Please enter your full name (at least 2 characters).");
      if (password.length < 4) return setError("Password must be at least 4 characters.");
    }
    setBusy(true);
    try {
      if (mode === "signup") {
        await register({ name: name.trim(), email: email.trim(), password, role });
        setNotice("Account created. Signing you in…");
      }
      const result = await login({ email: email.trim(), password });
      onLoggedIn(result, email.trim());
    } catch (err: unknown) {
      if (err instanceof ApiRequestError) {
        setError(mode === "signin" && err.status === 401 ? "Invalid email or password. Please try again." : err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
      setNotice("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-layout">
      <section className="login-showcase">
        <ParticleField />
        <span className="mm-orb mm-orb-a" /><span className="mm-orb mm-orb-b" /><span className="mm-orb mm-orb-c" />
        <div className="showcase-top">
          <a className="brand brand-light" href="/" aria-label="MarketMindAI home">
            <span className="brand-mark"><Activity size={21} /></span>
            <span><strong>MarketMind</strong><small>AI BUSINESS INTELLIGENCE</small></span>
          </a>
          <span className="showcase-badge"><Sparkles size={14} /> Built for smarter decisions</span>
        </div>

        <div className="showcase-content">
          <p className="eyebrow eyebrow-light">SALES INTELLIGENCE PLATFORM</p>
          <h1>
            Turn sales history into decisions. <br />
            <span className="mm-rotator">
              <span key={word} className="mm-word">{WORDS[word]}</span>
            </span>
          </h1>
          <p className="showcase-copy">
            One secure workspace for forecasts, customer segments, churn risk, recommendations and anomaly alerts.
          </p>
          <div className="mm-chips">
            {FEATURES.map(({ icon: I, label }, i) => (
              <span key={label} className="mm-chip" style={{ animationDelay: `${0.4 + i * 0.1}s` }}><I size={15} /> {label}</span>
            ))}
          </div>
        </div>
      </section>

      <section className="login-panel">
        <div className="login-form-wrap">
          <div className="mm-tabs" role="tablist">
            <button type="button" role="tab" aria-selected={mode === "signin"} className={mode === "signin" ? "on" : ""} onClick={() => switchMode("signin")}>Sign in</button>
            <button type="button" role="tab" aria-selected={mode === "signup"} className={mode === "signup" ? "on" : ""} onClick={() => switchMode("signup")}>Create account</button>
            <span className="mm-tab-ind" style={{ transform: `translateX(${mode === "signin" ? 0 : 100}%)` }} />
          </div>

          <div className="login-heading">
            <span className="login-icon"><LockKeyhole size={22} /></span>
            <p className="eyebrow">{mode === "signin" ? "WELCOME BACK" : "GET STARTED"}</p>
            <h2>{mode === "signin" ? "Sign in to MarketMind" : "Create your account"}</h2>
            <p>{mode === "signin" ? "Use your registered business email to continue." : "Join in a minute. Your role decides what you can see."}</p>
          </div>

          <form className="login-form" onSubmit={submit} key={mode}>
            {mode === "signup" && (
              <label>Full name
                <span className="input-wrap"><User size={17} />
                  <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Anubhav Kumar Gupta" autoComplete="name" required />
                </span>
              </label>
            )}
            <label>Business email
              <span className="input-wrap"><Mail size={17} />
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@company.com" autoComplete="email" required />
              </span>
            </label>
            <label>Password
              <span className="input-wrap"><LockKeyhole size={17} />
                <input type={show ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter your password"
                  autoComplete={mode === "signin" ? "current-password" : "new-password"} required />
                <button type="button" className="password-toggle" onClick={() => setShow((s) => !s)} aria-label={show ? "Hide password" : "Show password"}>
                  {show ? <EyeOff size={17} /> : <Eye size={17} />}
                </button>
              </span>
            </label>
            {mode === "signup" && (
              <label>Your role
                <span className="mm-roles">
                  {ROLES.map((r) => (
                    <button key={r.value} type="button" className={role === r.value ? "on" : ""} onClick={() => setRole(r.value)}>{r.label}</button>
                  ))}
                </span>
              </label>
            )}

            {error && <p className="login-error" role="alert">{error}</p>}
            {notice && <p className="mm-notice" role="status">{notice}</p>}

            <button type="submit" className="button button-primary submit-button" disabled={busy}>
              {busy ? "Please wait…" : mode === "signin" ? "Sign in" : "Create account"} <ArrowRight size={17} />
            </button>
          </form>

          <p className="mm-switch">
            {mode === "signin" ? "New to MarketMind?" : "Already have an account?"}{" "}
            <button type="button" onClick={() => switchMode(mode === "signin" ? "signup" : "signin")}>
              {mode === "signin" ? "Create an account" : "Sign in"}
            </button>
          </p>

          <div className="login-security"><ShieldCheck size={16} /> Secured with role-based access and encrypted passwords.</div>
        </div>
        <footer className="login-footer">MarketMind AI · Small business sales intelligence</footer>
      </section>
    </main>
  );
}
