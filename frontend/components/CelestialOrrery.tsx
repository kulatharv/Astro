'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { Link } from '@/i18n/routing';

interface OrreryPlanet {
  id: string;
  glyph: string;
  r: number;
  lat: number;
  speed: number;
  color: string;
  glowColor: string;
  size: number;
}

const ORRERY_PLANETS: OrreryPlanet[] = [
  { id: 'surya', glyph: '☉', r: 140, lat: 0.08, speed: 0.005, color: '#E49D4B', glowColor: 'rgba(228, 157, 75, 0.35)', size: 9 },
  { id: 'chandra', glyph: '☽', r: 110, lat: 0.18, speed: 0.012, color: '#F3C387', glowColor: 'rgba(243, 195, 135, 0.40)', size: 7.5 },
  { id: 'mangala', glyph: '♂', r: 165, lat: -0.15, speed: 0.004, color: '#C46B1E', glowColor: 'rgba(196, 107, 30, 0.40)', size: 7.5 },
  { id: 'budha', glyph: '☿', r: 85, lat: 0.06, speed: 0.014, color: '#C46B1E', glowColor: 'rgba(196, 107, 30, 0.35)', size: 6.5 },
  { id: 'guru', glyph: '♃', r: 195, lat: 0.24, speed: 0.0025, color: '#E49D4B', glowColor: 'rgba(228, 157, 75, 0.45)', size: 9.5 },
  { id: 'shukra', glyph: '♀', r: 125, lat: -0.12, speed: 0.008, color: '#F3C387', glowColor: 'rgba(243, 195, 135, 0.35)', size: 7.5 },
  { id: 'shani', glyph: '♄', r: 225, lat: -0.22, speed: 0.0018, color: '#821C17', glowColor: 'rgba(130, 28, 23, 0.35)', size: 8.5 },
  { id: 'rahu', glyph: '☊', r: 178, lat: 0.28, speed: -0.003, color: '#421A10', glowColor: 'rgba(66, 26, 16, 0.35)', size: 6.5 },
  { id: 'ketu', glyph: '☋', r: 178, lat: -0.28, speed: -0.003, color: '#821C17', glowColor: 'rgba(130, 28, 23, 0.35)', size: 6.5 },
];

const RASHIS_GLYPHS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓'];

export default function CelestialOrrery() {
  const t = useTranslations('hero');
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [selectedPlanetId, setSelectedPlanetId] = useState<string>('mangala');
  const [isHovering, setIsHovering] = useState(false);

  // 3D Rotation Angles & Inertial Drag State
  const anglesRef = useRef({
    x: 0.42,
    y: 0.38,
    targetX: 0.42,
    targetY: 0.38,
    isDragging: false,
    lastX: 0,
    lastY: 0,
  });

  const animStateRef = useRef({
    globalTime: 0,
    counterTime: 0,
    isVisible: true,
    projectedPlanets: [] as {
      id: string;
      x: number;
      y: number;
      z: number;
      size: number;
      scale: number;
    }[],
  });

  // Perspective 3D mathematical projection
  const project3D = useCallback((x: number, y: number, z: number, cx: number, cy: number, fov: number) => {
    const cosY = Math.cos(anglesRef.current.y);
    const sinY = Math.sin(anglesRef.current.y);
    const x1 = x * cosY + z * sinY;
    const z1 = -x * sinY + z * cosY;

    const cosX = Math.cos(anglesRef.current.x);
    const sinX = Math.sin(anglesRef.current.x);
    const y2 = y * cosX - z1 * sinX;
    const z2 = y * sinX + z1 * cosX;

    const distance = 460;
    const scale = fov / (distance + z2);
    return {
      x: cx + x1 * scale,
      y: cy + y2 * scale,
      scale: Math.max(0.2, scale),
      z: z2,
    };
  }, []);

  // Main Canvas render loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // High-DPI canvas backing store scaling
    const resizeCanvas = () => {
      const rect = canvas.getBoundingClientRect();
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
    };

    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Battery & performance safeguard: pauses when scrolled away
    const observer = new IntersectionObserver(([entry]) => {
      animStateRef.current.isVisible = entry.isIntersecting;
    }, { threshold: 0.08 });

    if (containerRef.current) {
      observer.observe(containerRef.current);
    }

    // Static starfield background seed
    const stars: { x: number; y: number; r: number; alpha: number; speed: number }[] = [];
    for (let i = 0; i < 48; i++) {
      stars.push({
        x: Math.random() * 560,
        y: Math.random() * 560,
        r: 0.6 + Math.random() * 0.9,
        alpha: 0.2 + Math.random() * 0.5,
        speed: 0.02 + Math.random() * 0.03,
      });
    }

    const render = () => {
      if (!animStateRef.current.isVisible) {
        animationFrameId = requestAnimationFrame(render);
        return;
      }

      const width = canvas.clientWidth;
      const height = canvas.clientHeight;
      const cx = width / 2;
      const cy = height / 2;
      const fov = 410;

      ctx.clearRect(0, 0, width, height);

      // Smooth damping interpolation
      anglesRef.current.x += (anglesRef.current.targetX - anglesRef.current.x) * 0.08;
      anglesRef.current.y += (anglesRef.current.targetY - anglesRef.current.y) * 0.08;

      if (!prefersReducedMotion && !anglesRef.current.isDragging) {
        anglesRef.current.targetY += 0.0011;
        animStateRef.current.globalTime += 0.009;
        animStateRef.current.counterTime -= 0.006;
      }

      // ── 1. AMBIENT BACKGROUND GLOW (Sacred Ivory & Parchment warmth) ──
      const centerGlow = ctx.createRadialGradient(cx, cy, 5, cx, cy, 230);
      centerGlow.addColorStop(0, 'rgba(243, 195, 135, 0.45)');
      centerGlow.addColorStop(0.35, 'rgba(252, 235, 210, 0.22)');
      centerGlow.addColorStop(0.7, 'rgba(253, 245, 230, 0)');
      ctx.fillStyle = centerGlow;
      ctx.fillRect(0, 0, width, height);

      // Celestial stars / particles with subtle twinkling
      stars.forEach((star, sIdx) => {
        const pulse = 0.5 + 0.5 * Math.sin(animStateRef.current.globalTime * 3 + sIdx);
        ctx.beginPath();
        ctx.arc(star.x * (width / 560), star.y * (height / 560), star.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(228, 157, 75, ${star.alpha * pulse * 0.5})`;
        ctx.fill();
      });

      // ── 2. CELESTIAL YANTRA GEOMETRY & CONCENTRIC AXES ──
      // Concentric guide rings (Temple Gold & Warm Sandstone)
      [65, 115, 160, 205].forEach((r) => {
        ctx.beginPath();
        ctx.arc(cx, cy, r, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(228, 157, 75, 0.16)';
        ctx.lineWidth = 0.75;
        ctx.stroke();
      });

      // 8-directional celestial meridian rays
      ctx.beginPath();
      for (let i = 0; i < 8; i++) {
        const rad = (i * Math.PI) / 4;
        ctx.moveTo(cx + Math.cos(rad) * 45, cy + Math.sin(rad) * 45);
        ctx.lineTo(cx + Math.cos(rad) * 215, cy + Math.sin(rad) * 215);
      }
      ctx.strokeStyle = 'rgba(196, 107, 30, 0.08)';
      ctx.lineWidth = 0.6;
      ctx.stroke();

      // ── 3. 3D ORRERY ARMS & ORBITAL RINGS ──
      const draw3DRing = (
        radius: number,
        tiltAngle: number,
        colorFront: string,
        colorBack: string,
        lineWidth: number,
        rotationOffset: number = 0
      ) => {
        const steps = 64;
        for (let i = 0; i < steps; i++) {
          const theta1 = (i / steps) * Math.PI * 2 + rotationOffset;
          const theta2 = ((i + 1) / steps) * Math.PI * 2 + rotationOffset;

          const zRaw1 = radius * Math.sin(theta1);
          const zRaw2 = radius * Math.sin(theta2);
          const x1 = radius * Math.cos(theta1);
          const x2 = radius * Math.cos(theta2);
          const y1 = Math.sin(tiltAngle) * zRaw1;
          const y2 = Math.sin(tiltAngle) * zRaw2;
          const z1 = Math.cos(tiltAngle) * zRaw1;
          const z2 = Math.cos(tiltAngle) * zRaw2;

          const p1 = project3D(x1, y1, z1, cx, cy, fov);
          const p2 = project3D(x2, y2, z2, cx, cy, fov);
          const avgZ = (p1.z + p2.z) / 2;

          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = avgZ > 0 ? colorFront : colorBack;
          ctx.lineWidth = avgZ > 0 ? lineWidth : lineWidth * 0.7;
          ctx.stroke();
        }
      };

      // 1. Outer Ecliptic Zodiac Ring (with 12 Rashi divisions)
      const eclipticR = 210;
      draw3DRing(
        eclipticR,
        0.38,
        'rgba(228, 157, 75, 0.85)',
        'rgba(228, 157, 75, 0.28)',
        1.5,
        animStateRef.current.globalTime * 0.1
      );
      draw3DRing(
        eclipticR - 6,
        0.38,
        'rgba(228, 157, 75, 0.40)',
        'rgba(228, 157, 75, 0.15)',
        0.8,
        animStateRef.current.globalTime * 0.1
      );

      // Graduation ticks on Ecliptic band
      for (let i = 0; i < 36; i++) {
        const theta = (i / 36) * Math.PI * 2 + animStateRef.current.globalTime * 0.1;
        const zRaw1 = eclipticR * Math.sin(theta);
        const zRaw2 = (eclipticR - 6) * Math.sin(theta);
        const x1 = eclipticR * Math.cos(theta);
        const x2 = (eclipticR - 6) * Math.cos(theta);
        const y1 = Math.sin(0.38) * zRaw1;
        const y2 = Math.sin(0.38) * zRaw2;
        const z1 = Math.cos(0.38) * zRaw1;
        const z2 = Math.cos(0.38) * zRaw2;

        const p1 = project3D(x1, y1, z1, cx, cy, fov);
        const p2 = project3D(x2, y2, z2, cx, cy, fov);

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = p1.z > 0 ? 'rgba(228, 157, 75, 0.75)' : 'rgba(228, 157, 75, 0.20)';
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }

      // 12 Zodiac Rashi Glyphs along the Ecliptic Ring
      RASHIS_GLYPHS.forEach((glyph, idx) => {
        const theta = (idx / 12) * Math.PI * 2 + animStateRef.current.globalTime * 0.1;
        const rPos = eclipticR - 3;
        const zRaw = rPos * Math.sin(theta);
        const x0 = rPos * Math.cos(theta);
        const y0 = Math.sin(0.38) * zRaw;
        const zActual = Math.cos(0.38) * zRaw;

        const p = project3D(x0, y0, zActual, cx, cy, fov);

        if (p.z > -30 && p.scale > 0.7) {
          ctx.beginPath();
          ctx.arc(p.x, p.y - 10, 7.5 * p.scale, 0, Math.PI * 2);
          ctx.fillStyle = '#FCEBD2';
          ctx.fill();
          ctx.strokeStyle = '#E49D4B';
          ctx.lineWidth = 0.8;
          ctx.stroke();

          ctx.fillStyle = '#821C17';
          ctx.font = `bold ${Math.round(8.5 * p.scale)}px serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(glyph, p.x, p.y - 10);
        }
      });

      // 2. Secondary Horizontal Equator Ring (Antique Champagne)
      draw3DRing(
        155,
        0,
        'rgba(243, 195, 135, 0.75)',
        'rgba(243, 195, 135, 0.20)',
        1.1,
        animStateRef.current.counterTime * 0.12
      );

      // 3. Counter-Rotating Inclined Colure Ring (Sacred Copper)
      draw3DRing(
        180,
        -0.38,
        'rgba(196, 107, 30, 0.65)',
        'rgba(196, 107, 30, 0.20)',
        1.0,
        animStateRef.current.counterTime * 0.15
      );

      // 4. Polar Vertical Meridian Reference Ring (Royal Kumkum)
      ctx.beginPath();
      for (let i = 0; i <= 48; i++) {
        const theta = (i / 48) * Math.PI * 2;
        const x0 = 0;
        const y0 = 185 * Math.sin(theta);
        const z0 = 185 * Math.cos(theta);
        const p = project3D(x0, y0, z0, cx, cy, fov);
        if (i === 0) ctx.moveTo(p.x, p.y);
        else ctx.lineTo(p.x, p.y);
      }
      ctx.strokeStyle = 'rgba(130, 28, 23, 0.28)';
      ctx.lineWidth = 0.9;
      ctx.stroke();

      // ── 4. NAVAGRAHAS (9 PLANETARY BODIES) ──
      const sortedPlanets: any[] = [];
      animStateRef.current.projectedPlanets = [];

      ORRERY_PLANETS.forEach((cfg, idx) => {
        const theta =
          animStateRef.current.globalTime * cfg.speed * 8 +
          (idx * ((Math.PI * 2) / ORRERY_PLANETS.length));
        const r = cfg.r * 0.76;
        const x = r * Math.cos(theta);
        const z = r * Math.sin(theta);
        const y = cfg.lat * r * 0.45 + Math.sin(theta * 2) * 7;

        const proj = project3D(x, y, z, cx, cy, fov);
        sortedPlanets.push({
          cfg,
          x: proj.x,
          y: proj.y,
          z: proj.z,
          scale: proj.scale,
          size: cfg.size * proj.scale,
        });
      });

      // Depth sort
      sortedPlanets.sort((a, b) => a.z - b.z);

      sortedPlanets.forEach((item) => {
        const isSelected = selectedPlanetId === item.cfg.id;
        animStateRef.current.projectedPlanets.push({
          id: item.cfg.id,
          x: item.x,
          y: item.y,
          z: item.z,
          size: item.size,
          scale: item.scale,
        });

        // Orbital track trace
        ctx.beginPath();
        ctx.arc(cx, cy, item.cfg.r * 0.76 * item.scale * 0.98, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(228, 157, 75, 0.10)';
        ctx.lineWidth = 0.6;
        ctx.stroke();

        // Controlled ambient glow
        ctx.beginPath();
        const aura = ctx.createRadialGradient(item.x, item.y, 1, item.x, item.y, item.size * 2.4);
        aura.addColorStop(0, item.cfg.glowColor);
        aura.addColorStop(1, 'transparent');
        ctx.fillStyle = aura;
        ctx.arc(item.x, item.y, item.size * 2.4, 0, Math.PI * 2);
        ctx.fill();

        // Planet body
        ctx.beginPath();
        ctx.arc(item.x, item.y, item.size, 0, Math.PI * 2);
        ctx.fillStyle = item.cfg.color;
        ctx.fill();
        ctx.strokeStyle = '#FDF5E6';
        ctx.lineWidth = 1.6;
        ctx.stroke();

        // Outer delicate Sandstone rim
        ctx.beginPath();
        ctx.arc(item.x, item.y, item.size + 1.2, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(249, 218, 181, 0.6)';
        ctx.lineWidth = 0.8;
        ctx.stroke();

        // Selected halo indicator (Royal Kumkum + Temple Gold)
        if (isSelected) {
          ctx.beginPath();
          ctx.arc(item.x, item.y, item.size + 4.5, 0, Math.PI * 2);
          ctx.strokeStyle = '#821C17';
          ctx.lineWidth = 1.8;
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(item.x, item.y, item.size + 7.5, 0, Math.PI * 2);
          ctx.strokeStyle = 'rgba(228, 157, 75, 0.6)';
          ctx.lineWidth = 1.0;
          ctx.stroke();
        }

        // Planet glyph symbol
        if (item.scale > 0.72) {
          ctx.fillStyle = isSelected ? '#821C17' : '#421A10';
          ctx.font = `bold ${Math.round(11 * item.scale)}px sans-serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(item.cfg.glyph, item.x, item.y - item.size - 9.5);
        }
      });

      // ── 5. CENTRAL ILLUMINATED OM (ॐ) SYMBOL (Stationary) ──
      // Breathing aura (Antique Champagne)
      const breath = 0.5 + 0.5 * Math.sin(animStateRef.current.globalTime * 2);
      ctx.beginPath();
      const omGlow = ctx.createRadialGradient(cx, cy, 3, cx, cy, 38);
      omGlow.addColorStop(0, `rgba(243, 195, 135, ${0.5 + breath * 0.2})`);
      omGlow.addColorStop(0.6, 'rgba(228, 157, 75, 0.20)');
      omGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = omGlow;
      ctx.arc(cx, cy, 38, 0, Math.PI * 2);
      ctx.fill();

      // Outer Sacred Ivory medallion disc
      ctx.beginPath();
      ctx.arc(cx, cy, 18, 0, Math.PI * 2);
      ctx.fillStyle = '#FDF5E6';
      ctx.fill();
      ctx.strokeStyle = '#E49D4B';
      ctx.lineWidth = 2.0;
      ctx.stroke();

      // Inner Royal Kumkum hairline ring
      ctx.beginPath();
      ctx.arc(cx, cy, 14, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(130, 28, 23, 0.35)';
      ctx.lineWidth = 1.0;
      ctx.stroke();

      // Stationary Devanagari ॐ in Royal Kumkum
      ctx.fillStyle = '#821C17';
      ctx.font = 'bold 16px serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText('ॐ', cx, cy + 0.5);

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', resizeCanvas);
      observer.disconnect();
    };
  }, [selectedPlanetId, project3D]);

  // Pointer & Drag Interactions (Non-blocking on mobile page scroll)
  const handlePointerDown = (clientX: number, clientY: number) => {
    anglesRef.current.isDragging = true;
    anglesRef.current.lastX = clientX;
    anglesRef.current.lastY = clientY;
  };

  const handlePointerMove = (clientX: number, clientY: number) => {
    if (anglesRef.current.isDragging) {
      const dx = clientX - anglesRef.current.lastX;
      const dy = clientY - anglesRef.current.lastY;
      anglesRef.current.targetY += dx * 0.007;
      anglesRef.current.targetX -= dy * 0.007;
      anglesRef.current.lastX = clientX;
      anglesRef.current.lastY = clientY;
    } else if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;

      const hovered = animStateRef.current.projectedPlanets.find(
        (p) => Math.hypot(p.x - mx, p.y - my) < p.size + 12
      );
      setIsHovering(Boolean(hovered));
    }
  };

  const handlePointerUp = (clientX?: number, clientY?: number) => {
    anglesRef.current.isDragging = false;
    if (clientX !== undefined && clientY !== undefined && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;

      const clicked = animStateRef.current.projectedPlanets.find(
        (p) => Math.hypot(p.x - mx, p.y - my) < p.size + 14
      );

      if (clicked) {
        setSelectedPlanetId(clicked.id);
      }
    }
  };

  // Selected Planet Details
  const activePlanet = ORRERY_PLANETS.find((p) => p.id === selectedPlanetId) || ORRERY_PLANETS[2];

  return (
    <div ref={containerRef} className="w-full relative flex flex-col items-center select-none">
      {/* ── CELESTIAL ORRERY MAIN STAGE ── */}
      <div className="relative w-full max-w-[530px] aspect-square rounded-[32px] bg-radial from-[#FFFFFF] via-[#FAF6F0] to-[#F5EFE6] border border-[#C5A059]/40 ring-1 ring-[#C5A059]/20 shadow-[0_24px_50px_-12px_rgba(36,18,11,0.12),0_4px_16px_rgba(197,160,89,0.08)] overflow-hidden flex items-center justify-center p-3 sm:p-5">
        {/* Subtle radial parchment inner texture */}
        <div className="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,rgba(245,239,230,0.75)_0%,rgba(250,246,240,0.95)_100%)]" />

        {/* ── FLOATING CARD 1: EXPLORE A GRAHA (Top-Left) ── */}
        <div className="absolute top-4 left-4 z-30 pointer-events-auto">
          <div className="px-3.5 py-2.5 rounded-2xl bg-[#FFFFFF]/90 border border-[#C5A059]/35 shadow-md backdrop-blur-md transition-all duration-300 hover:border-[#7A1612] max-w-[210px]">
            <span className="block text-[9.5px] font-mono tracking-widest text-[#7A1612] uppercase font-bold">
              {t('card1Eyebrow')}
            </span>
            <div className="flex items-center gap-2 mt-0.5">
              <span className="w-6 h-6 rounded-full bg-[#FAF6F0] border border-[#C5A059] flex items-center justify-center text-xs font-bold text-[#7A1612] shrink-0 shadow-2xs">
                {activePlanet.glyph}
              </span>
              <div className="truncate">
                <span className="font-serif text-sm font-bold text-[#24120B] block truncate">
                  {t(`planets.${activePlanet.id}.sanskrit` as any)} · {t(`planets.${activePlanet.id}.name` as any)}
                </span>
                <span className="text-[11px] text-[#A85A1E] block truncate font-medium">
                  {t(`planetsShort.${activePlanet.id}` as any)}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* ── FLOATING CARD 2: YOUR STARTING POINT (Bottom-Right) ── */}
        <div className="absolute bottom-4 right-4 z-30 pointer-events-auto">
          <Link
            href="/kundali"
            className="block px-3.5 py-2.5 rounded-2xl bg-[#FFFFFF]/90 border border-[#C5A059]/35 shadow-md backdrop-blur-md transition-all duration-300 hover:border-[#7A1612] hover:bg-[#F5EFE6]/80 group text-right max-w-[200px]"
          >
            <span className="block text-[9.5px] font-mono tracking-widest text-[#7A1612] uppercase font-bold group-hover:text-[#24120B] transition-colors">
              {t('card2Eyebrow')}
            </span>
            <span className="font-serif text-sm font-bold text-[#24120B] block group-hover:text-[#7A1612] transition-colors">
              {t('card2Title')}
            </span>
            <span className="text-[11px] text-[#A85A1E] block font-medium">
              {t('card2Desc')}
            </span>
          </Link>
        </div>

        {/* ── INTERACTIVE CANVAS ── */}
        <canvas
          ref={canvasRef}
          className={`w-full h-full relative z-20 touch-none ${
            isHovering ? 'cursor-pointer' : 'cursor-grab active:cursor-grabbing'
          }`}
          onMouseDown={(e) => handlePointerDown(e.clientX, e.clientY)}
          onMouseMove={(e) => handlePointerMove(e.clientX, e.clientY)}
          onMouseUp={(e) => handlePointerUp(e.clientX, e.clientY)}
          onTouchStart={(e) => {
            if (e.touches[0]) handlePointerDown(e.touches[0].clientX, e.touches[0].clientY);
          }}
          onTouchMove={(e) => {
            if (e.touches[0]) handlePointerMove(e.touches[0].clientX, e.touches[0].clientY);
          }}
          onTouchEnd={() => handlePointerUp()}
          aria-label="Interactive Vedic Celestial Observatory Orrery"
        />
      </div>

      {/* ── CAPTION NOTICE (Below Orrery) ── */}
      <div className="mt-3 text-center">
        <span className="text-[10px] tracking-widest uppercase font-mono text-[#C46B1E] font-medium block">
          {t('captionNotice')}
        </span>
      </div>

      {/* ── QUICK PLANETARY CHIPS FOR TOUCH/KEYBOARD ACCESSIBILITY ── */}
      <div className="w-full max-w-[530px] mt-3 flex flex-wrap gap-1.5 justify-center">
        {ORRERY_PLANETS.map((p) => {
          const isSelected = selectedPlanetId === p.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => setSelectedPlanetId(p.id)}
              className={`px-2.5 py-1 rounded-lg text-xs font-serif flex items-center gap-1.5 transition-all ${
                isSelected
                  ? 'bg-[#821C17] text-[#FDF5E6] border border-[#E49D4B] shadow-xs font-bold scale-105'
                  : 'bg-[#FDF5E6] text-[#421A10] hover:text-[#821C17] hover:bg-[#FCEBD2] border border-[#F9DAB5]'
              }`}
              aria-pressed={isSelected}
            >
              <span className="text-xs">{p.glyph}</span>
              <span>{t(`planets.${p.id}.sanskrit` as any)}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
