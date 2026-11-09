import React, { useEffect, useRef } from 'react';

/**
 * High-performance animated canvas rendering floating luminous dots / dust motes.
 * Uses requestAnimationFrame, zero dependencies, pointer-events: none.
 */
export default function ParticleCanvas({ particleCount = 42, className = '' }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    const handleResize = () => {
      if (!canvas) return;
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    window.addEventListener('resize', handleResize);

    // Color palette: Warm golden dust (matching the lamp), radiant cyan & luminous violet
    const colorThemes = [
      { r: 253, g: 224, b: 71 },   // warm golden amber
      { r: 251, g: 191, b: 36 },   // warm honey yellow
      { r: 245, g: 158, b: 11 },   // amber glow
      { r: 192, g: 132, b: 252 },  // aurora violet
      { r: 56,  g: 189, b: 248 },  // aurora cyan
      { r: 255, g: 255, b: 255 }   // luminous star white
    ];

    // Initialize particles
    const particles = [];
    for (let i = 0; i < particleCount; i++) {
      const color = colorThemes[Math.floor(Math.random() * colorThemes.length)];
      particles.push({
        x: Math.random() * width,
        y: Math.random() * height,
        baseRadius: Math.random() * 2.2 + 1.2, // 1.2px to 3.4px
        radius: 1.5,
        color,
        baseAlpha: Math.random() * 0.45 + 0.35, // 0.35 to 0.8
        alpha: 0.5,
        vx: (Math.random() - 0.5) * 0.4,
        vy: -(Math.random() * 0.45 + 0.2), // gentle upward float
        oscillationSpeed: Math.random() * 0.02 + 0.01,
        oscillationDistance: Math.random() * 1.5 + 0.5,
        pulseSpeed: Math.random() * 0.025 + 0.015,
        phase: Math.random() * Math.PI * 2
      });
    }

    let time = 0;

    const render = () => {
      time += 1;
      ctx.clearRect(0, 0, width, height);

      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];

        // Motion physics: upward float + sine-wave horizontal drift
        p.y += p.vy;
        p.x += Math.sin(time * p.oscillationSpeed + p.phase) * p.oscillationDistance * 0.2 + p.vx;

        // Wrap around boundaries
        if (p.y < -15) {
          p.y = height + 10;
          p.x = Math.random() * width;
        }
        if (p.x < -15) p.x = width + 10;
        if (p.x > width + 15) p.x = -10;

        // Breathing glow alpha
        const breathing = Math.sin(time * p.pulseSpeed + p.phase);
        p.alpha = Math.max(0.1, p.baseAlpha + breathing * 0.25);
        p.radius = Math.max(0.8, p.baseRadius + breathing * 0.5);

        // Draw soft radiant glow halo
        const gradient = ctx.createRadialGradient(
          p.x, p.y, 0,
          p.x, p.y, p.radius * 3.5
        );
        gradient.addColorStop(0, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${p.alpha})`);
        gradient.addColorStop(0.35, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${p.alpha * 0.5})`);
        gradient.addColorStop(1, `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, 0)`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * 3.5, 0, Math.PI * 2);
        ctx.fill();

        // Draw solid core
        ctx.fillStyle = `rgba(${p.color.r}, ${p.color.g}, ${p.color.b}, ${Math.min(1, p.alpha * 1.3)})`;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius * 0.85, 0, Math.PI * 2);
        ctx.fill();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [particleCount]);

  return (
    <canvas
      ref={canvasRef}
      className={`particle-canvas ${className}`}
      style={{
        position: 'fixed',
        inset: 0,
        pointerEvents: 'none',
        zIndex: 1,
        width: '100%',
        height: '100%'
      }}
    />
  );
}
