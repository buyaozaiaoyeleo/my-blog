import { useEffect, useRef } from "react";

export type Weather = "calm" | "storm" | "aurora";

export function Starfield({ weather, interactive = false }: { weather: Weather; interactive?: boolean }) {
  const ref = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = ref.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const count = weather === "storm" ? 120 : 78;
    const stars = Array.from({ length: count }, () => ({
      x: Math.random(),
      y: Math.random(),
      z: Math.random() * 0.85 + 0.2,
      v: Math.random() * 0.00028 + 0.00004,
    }));
    const pointer = { x: 0.72, y: 0.38, on: false };
    let frame = 0;
    let raf = 0;

    const resize = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.max(1, rect.width * dpr);
      canvas.height = Math.max(1, rect.height * dpr);
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    resize();

    const onMove = (event: PointerEvent) => {
      const rect = canvas.getBoundingClientRect();
      pointer.x = (event.clientX - rect.left) / Math.max(rect.width, 1);
      pointer.y = (event.clientY - rect.top) / Math.max(rect.height, 1);
      pointer.on = true;
    };
    if (interactive) canvas.addEventListener("pointermove", onMove);

    const color = weather === "aurora" ? "143, 208, 198" : "240, 162, 2";
    const draw = () => {
      const rect = canvas.getBoundingClientRect();
      context.clearRect(0, 0, rect.width, rect.height);
      const speed = weather === "storm" ? 3.4 : weather === "aurora" ? 1.5 : 0.55;
      const reach = weather === "storm" ? 190 : 130;
      for (const star of stars) {
        if (!reduce) {
          star.y -= star.v * speed * (0.6 + star.z);
          if (star.y < 0) star.y += 1;
        }
        const px = star.x * rect.width;
        const py = star.y * rect.height;
        context.beginPath();
        context.fillStyle = `rgba(${color}, ${0.28 + star.z * 0.7})`;
        context.arc(px, py, star.z * 1.7, 0, Math.PI * 2);
        context.fill();
        if (interactive && pointer.on) {
          const dx = px - pointer.x * rect.width;
          const dy = py - pointer.y * rect.height;
          const dist = Math.hypot(dx, dy);
          if (dist < reach) {
            context.strokeStyle = `rgba(${color}, ${(1 - dist / reach) * 0.5})`;
            context.lineWidth = 1;
            context.beginPath();
            context.moveTo(px, py);
            context.lineTo(pointer.x * rect.width, pointer.y * rect.height);
            context.stroke();
          }
        }
      }
      frame += 1;
      if (!reduce || frame < 2) raf = requestAnimationFrame(draw);
    };
    draw();
    window.addEventListener("resize", resize);
    return () => {
      cancelAnimationFrame(raf);
      window.removeEventListener("resize", resize);
      canvas.removeEventListener("pointermove", onMove);
    };
  }, [weather, interactive]);

  return <canvas ref={ref} className="starfield" aria-hidden="true" />;
}
