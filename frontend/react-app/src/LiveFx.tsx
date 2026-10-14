import { useEffect, useMemo, useRef, useState, type ComponentType } from "react";
import { CornerDownLeft, Search } from "lucide-react";

export interface PaletteItem { id: string; label: string; icon: ComponentType<{ size?: number }> }
interface LiveFxProps { items: PaletteItem[]; onSelect: (id: string) => void }

const SPOT = ".feature-card, .lx-stat, .inventory-metrics article, .forecast-subsection, .lx-modal";

/** Global effects: scroll progress, cursor spotlight on cards, and a Ctrl/Cmd+K command palette. */
export default function LiveFx({ items, onSelect }: LiveFxProps) {
  const bar = useRef<HTMLDivElement>(null);
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [idx, setIdx] = useState(0);
  const [offline, setOffline] = useState(!navigator.onLine);

  useEffect(() => {
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      if (bar.current) bar.current.style.transform = `scaleX(${max > 0 ? window.scrollY / max : 0})`;
    };
    const onMove = (e: MouseEvent) => {
      const el = (e.target as HTMLElement | null)?.closest?.(SPOT) as HTMLElement | null;
      if (!el) return;
      const r = el.getBoundingClientRect();
      el.style.setProperty("--mx", `${e.clientX - r.left}px`);
      el.style.setProperty("--my", `${e.clientY - r.top}px`);
    };
    const onKey = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") { e.preventDefault(); setOpen((o) => !o); setQ(""); setIdx(0); }
      else if (e.key === "Escape") setOpen(false);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("mousemove", onMove, { passive: true });
    window.addEventListener("keydown", onKey);
    const goOff = () => setOffline(true);
    const goOn = () => setOffline(false);
    window.addEventListener("offline", goOff);
    window.addEventListener("online", goOn);
    return () => {
      window.removeEventListener("offline", goOff);
      window.removeEventListener("online", goOn);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  const results = useMemo(() => items.filter((i) => i.label.toLowerCase().includes(q.toLowerCase().trim())), [items, q]);
  const choose = (id: string) => { onSelect(id); setOpen(false); window.scrollTo({ top: 0, behavior: "smooth" }); };

  return (
    <>
      <div className="lx-progress" ref={bar} />
      {offline && <div className="lx-offline" role="status">You are offline. Changes will work again when your connection returns.</div>}
      <button type="button" className="lx-kbd-hint" onClick={() => { setOpen(true); setQ(""); setIdx(0); }} aria-label="Open command palette">
        <Search size={14} /> Jump to… <kbd>Ctrl</kbd><kbd>K</kbd>
      </button>
      {open && (
        <div className="lx-overlay lx-palette-wrap" onClick={() => setOpen(false)}>
          <div className="lx-palette" role="dialog" aria-label="Command palette" onClick={(e) => e.stopPropagation()}>
            <div className="lx-palette-input"><Search size={18} />
              <input autoFocus placeholder="Search pages…" value={q}
                onChange={(e) => { setQ(e.target.value); setIdx(0); }}
                onKeyDown={(e) => {
                  if (e.key === "ArrowDown") { e.preventDefault(); setIdx((i) => Math.min(i + 1, results.length - 1)); }
                  if (e.key === "ArrowUp") { e.preventDefault(); setIdx((i) => Math.max(i - 1, 0)); }
                  if (e.key === "Enter" && results[idx]) choose(results[idx].id);
                }} />
              <kbd>Esc</kbd>
            </div>
            <ul>
              {results.map((r, i) => { const I = r.icon; return (
                <li key={r.id}><button type="button" className={i === idx ? "on" : ""} onMouseEnter={() => setIdx(i)} onClick={() => choose(r.id)}>
                  <I size={18} /> <span>{r.label}</span>{i === idx && <CornerDownLeft size={14} />}
                </button></li>); })}
              {results.length === 0 && <li className="lx-empty">No matching page</li>}
            </ul>
          </div>
        </div>
      )}
    </>
  );
}
