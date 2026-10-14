import { useEffect, useState } from "react";
import { Activity } from "lucide-react";
import { getHealth } from "./lib/api";

const MAX = 28;

/** Real, live API heartbeat: pings /health every few seconds and charts the measured latency. */
export default function LiveStatus({ intervalMs = 5000 }: { intervalMs?: number }) {
  const [samples, setSamples] = useState<(number | null)[]>([]);
  const [lastOk, setLastOk] = useState<Date | null>(null);
  const [now, setNow] = useState(() => Date.now());

  useEffect(() => {
    let alive = true;
    const ping = async () => {
      const t0 = performance.now();
      try {
        await getHealth();
        if (!alive) return;
        setSamples((s) => [...s, Math.round(performance.now() - t0)].slice(-MAX));
        setLastOk(new Date());
      } catch {
        if (alive) setSamples((s) => [...s, null].slice(-MAX));
      }
    };
    void ping();
    const a = window.setInterval(() => void ping(), intervalMs);
    const b = window.setInterval(() => setNow(Date.now()), 1000);
    return () => { alive = false; window.clearInterval(a); window.clearInterval(b); };
  }, [intervalMs]);

  const valid = samples.filter((v): v is number => v !== null);
  const latest = samples.at(-1);
  const online = latest !== null && latest !== undefined;
  const max = Math.max(50, ...valid);
  const pts = samples
    .map((v, i) => (v === null ? null : `${(i * 120) / (MAX - 1)},${30 - (v / max) * 26}`))
    .filter(Boolean).join(" ");
  const ago = lastOk ? Math.max(0, Math.round((now - lastOk.getTime()) / 1000)) : null;
  const avg = valid.length ? Math.round(valid.reduce((a, b) => a + b, 0) / valid.length) : null;

  return (
    <div className={`lx-live ${online ? "ok" : "down"}`} title="Live API heartbeat">
      <div className="lx-live-top">
        <span className="lx-live-dot" />
        <b>{online ? "LIVE" : "OFFLINE"}</b>
        <Activity size={14} />
        <span>{online ? `${latest} ms` : "no response"}</span>
      </div>
      <svg viewBox="0 0 120 32" width="120" height="32" aria-hidden="true">
        <defs><linearGradient id="lxg" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#00A3A9" stopOpacity=".5" /><stop offset="1" stopColor="#00A3A9" stopOpacity="0" /></linearGradient></defs>
        {pts && <polyline points={`0,32 ${pts} 120,32`} fill="url(#lxg)" stroke="none" />}
        {pts && <polyline points={pts} fill="none" stroke="#4FD1D5" strokeWidth="1.8" strokeLinejoin="round" />}
      </svg>
      <small>{ago === null ? "connecting…" : `updated ${ago}s ago`}{avg !== null ? ` · avg ${avg} ms` : ""}</small>
    </div>
  );
}
