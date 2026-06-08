import { useEffect, useRef } from 'react';

export default function LandingCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return undefined;

    const ctx = canvas.getContext('2d');
    let animationId = 0;
    let width = 0;
    let height = 0;

    const mouse = { x: 0.5, y: 0.5, targetX: 0.5, targetY: 0.5 };
    const parallax = { x: 0, y: 0 };

    const particles = Array.from({ length: 72 }, () => ({
      x: Math.random(),
      y: Math.random(),
      vx: (Math.random() - 0.5) * 0.00035,
      vy: (Math.random() - 0.5) * 0.00035,
      r: 1 + Math.random() * 1.8,
      depth: 0.3 + Math.random() * 0.7,
    }));

    const resize = () => {
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = width;
      canvas.height = height;
    };

    const onMouseMove = (e) => {
      mouse.targetX = e.clientX / width;
      mouse.targetY = e.clientY / height;
    };

    const onMouseLeave = () => {
      mouse.targetX = 0.5;
      mouse.targetY = 0.5;
    };

    const draw = () => {
      mouse.x += (mouse.targetX - mouse.x) * 0.06;
      mouse.y += (mouse.targetY - mouse.y) * 0.06;

      const offsetX = (mouse.x - 0.5) * width;
      const offsetY = (mouse.y - 0.5) * height;
      parallax.x += (offsetX * 0.12 - parallax.x) * 0.08;
      parallax.y += (offsetY * 0.12 - parallax.y) * 0.08;

      ctx.clearRect(0, 0, width, height);

      const gradient = ctx.createRadialGradient(
        width * 0.5 + parallax.x * 1.4,
        height * 0.35 + parallax.y * 1.4,
        0,
        width * 0.5 + parallax.x * 0.6,
        height * 0.35 + parallax.y * 0.6,
        width * 0.75,
      );
      gradient.addColorStop(0, 'rgba(14, 116, 144, 0.22)');
      gradient.addColorStop(0.5, 'rgba(15, 23, 42, 0.55)');
      gradient.addColorStop(1, 'rgba(2, 6, 23, 0.95)');
      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, width, height);

      const mousePxX = mouse.x * width;
      const mousePxY = mouse.y * height;

      const cursorGlow = ctx.createRadialGradient(
        mousePxX, mousePxY, 0,
        mousePxX, mousePxY, Math.min(width, height) * 0.35,
      );
      cursorGlow.addColorStop(0, 'rgba(56, 189, 248, 0.14)');
      cursorGlow.addColorStop(0.45, 'rgba(99, 102, 241, 0.06)');
      cursorGlow.addColorStop(1, 'rgba(56, 189, 248, 0)');
      ctx.fillStyle = cursorGlow;
      ctx.fillRect(0, 0, width, height);

      particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;

        const px = p.x * width + parallax.x * p.depth;
        const py = p.y * height + parallax.y * p.depth;
        const dx = mousePxX - px;
        const dy = mousePxY - py;
        const dist = Math.hypot(dx, dy);

        if (dist < 220 && dist > 0) {
          const force = (1 - dist / 220) * 0.00018;
          p.vx -= (dx / dist) * force;
          p.vy -= (dy / dist) * force;
        }

        p.vx *= 0.995;
        p.vy *= 0.995;

        if (p.x < 0 || p.x > 1) p.vx *= -1;
        if (p.y < 0 || p.y > 1) p.vy *= -1;
        p.x = Math.min(1, Math.max(0, p.x));
        p.y = Math.min(1, Math.max(0, p.y));
      });

      const px = particles.map((p) => ({
        x: p.x * width + parallax.x * p.depth,
        y: p.y * height + parallax.y * p.depth,
        r: p.r,
      }));

      for (let i = 0; i < px.length; i += 1) {
        for (let j = i + 1; j < px.length; j += 1) {
          const dx = px[i].x - px[j].x;
          const dy = px[i].y - px[j].y;
          const dist = Math.hypot(dx, dy);
          if (dist < 140) {
            ctx.strokeStyle = `rgba(56, 189, 248, ${0.14 * (1 - dist / 140)})`;
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(px[i].x, px[i].y);
            ctx.lineTo(px[j].x, px[j].y);
            ctx.stroke();
          }
        }

        const dxMouse = mousePxX - px[i].x;
        const dyMouse = mousePxY - px[i].y;
        const distMouse = Math.hypot(dxMouse, dyMouse);
        if (distMouse < 180) {
          ctx.strokeStyle = `rgba(125, 211, 252, ${0.22 * (1 - distMouse / 180)})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(px[i].x, px[i].y);
          ctx.lineTo(mousePxX, mousePxY);
          ctx.stroke();
        }
      }

      px.forEach((p) => {
        ctx.fillStyle = 'rgba(125, 211, 252, 0.75)';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fill();
      });

      animationId = requestAnimationFrame(draw);
    };

    resize();
    draw();
    window.addEventListener('resize', resize);
    window.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseleave', onMouseLeave);

    return () => {
      cancelAnimationFrame(animationId);
      window.removeEventListener('resize', resize);
      window.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseleave', onMouseLeave);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 -z-10 h-full w-full bg-slate-950 pointer-events-none"
      aria-hidden="true"
    />
  );
}
