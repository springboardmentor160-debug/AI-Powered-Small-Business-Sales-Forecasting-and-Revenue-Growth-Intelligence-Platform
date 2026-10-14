import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ComponentType, type KeyboardEvent } from "react";

export interface NavTabItem { id: string; label: string; icon: ComponentType<{ size?: number }> }
interface NavTabsProps { items: NavTabItem[]; active: string; onSelect: (id: string) => void }

/** Horizontal tab bar: sliding indicator, cursor glow, per-icon micro-animations, arrow-key support. */
export default function NavTabs({ items, active, onSelect }: NavTabsProps) {
  const bar = useRef<HTMLElement>(null);
  const refs = useRef<Record<string, HTMLButtonElement | null>>({});
  const [ind, setInd] = useState({ left: 0, width: 0, ready: false });

  const place = useCallback(() => {
    const el = refs.current[active];
    if (el) setInd({ left: el.offsetLeft, width: el.offsetWidth, ready: true });
  }, [active, items.length]);

  useLayoutEffect(() => { place(); }, [place]);
  useEffect(() => {
    const ro = new ResizeObserver(place);
    if (bar.current) ro.observe(bar.current);
    window.addEventListener("resize", place);
    return () => { ro.disconnect(); window.removeEventListener("resize", place); };
  }, [place]);
  useEffect(() => { refs.current[active]?.scrollIntoView({ inline: "center", block: "nearest", behavior: "smooth" }); }, [active]);

  const onKey = (e: KeyboardEvent) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    const i = items.findIndex((t) => t.id === active);
    const next = items[(i + (e.key === "ArrowRight" ? 1 : items.length - 1)) % items.length];
    onSelect(next.id);
    refs.current[next.id]?.focus();
  };

  return (
    <nav className="page-navigation nt-bar" aria-label="Main navigation" ref={bar} onKeyDown={onKey}>
      <span className="nt-ind" style={{ transform: `translateX(${ind.left}px)`, width: ind.width, opacity: ind.ready ? 1 : 0 }} />
      {items.map(({ id, label, icon: Icon }, i) => (
        <button
          key={id}
          ref={(el) => { refs.current[id] = el; }}
          type="button"
          data-tab={id}
          className={`nt-tab ${active === id ? "on" : ""}`}
          style={{ animationDelay: `${i * 45}ms` }}
          aria-current={active === id ? "page" : undefined}
          onClick={() => onSelect(id)}
          onMouseMove={(e) => {
            const r = e.currentTarget.getBoundingClientRect();
            e.currentTarget.style.setProperty("--tx", `${e.clientX - r.left}px`);
            e.currentTarget.style.setProperty("--ty", `${e.clientY - r.top}px`);
          }}
        >
          <span className="nt-icon"><Icon size={18} /></span>
          <span className="nt-label">{label}</span>
        </button>
      ))}
    </nav>
  );
}
