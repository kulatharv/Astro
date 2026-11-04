'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { RotateCcw, Play, Pause, Orbit } from 'lucide-react';

interface PlanetConfig {
  id: string;
  glyph: string;
  r: number;
  lat: number;
  speed: number;
  color: string;
  glowColor: string;
  size: number;
}

const PLANETS_CONFIG: PlanetConfig[] = [
  { id: 'surya', glyph: '☉', r: 152, lat: 0.10, speed: 0.007, color: '#D97706', glowColor: 'rgba(217, 119, 6, 0.35)', size: 8.5 },
  { id: 'chandra', glyph: '☽', r: 124, lat: 0.22, speed: 0.013, color: '#C58342', glowColor: 'rgba(197, 131, 66, 0.35)', size: 7.5 },
  { id: 'mangala', glyph: '♂', r: 174, lat: -0.18, speed: 0.005, color: '#943F28', glowColor: 'rgba(148, 63, 40, 0.35)', size: 7.0 },
  { id: 'budha', glyph: '☿', r: 96, lat: 0.08, speed: 0.015, color: '#4D6A42', glowColor: 'rgba(77, 106, 66, 0.35)', size: 6.5 },
  { id: 'guru', glyph: '♃', r: 202, lat: 0.30, speed: 0.003, color: '#D9943B', glowColor: 'rgba(217, 148, 59, 0.35)', size: 9.0 },
  { id: 'shukra', glyph: '♀', r: 138, lat: -0.15, speed: 0.009, color: '#D4A359', glowColor: 'rgba(212, 163, 89, 0.35)', size: 7.5 },
  { id: 'shani', glyph: '♄', r: 226, lat: -0.26, speed: 0.002, color: '#58170C', glowColor: 'rgba(88, 23, 12, 0.35)', size: 8.5 },
  { id: 'rahu', glyph: '☊', r: 184, lat: 0.36, speed: -0.004, color: '#6B5547', glowColor: 'rgba(107, 85, 71, 0.35)', size: 6.5 },
  { id: 'ketu', glyph: '☋', r: 184, lat: -0.36, speed: -0.004, color: '#791412', glowColor: 'rgba(121, 20, 18, 0.35)', size: 6.5 },
];

const RASHIS_KEYS = [
  'mesha', 'vrishabha', 'mithuna', 'karka',
  'simha', 'kanya', 'tula', 'vrishchika',
  'dhanu', 'makara', 'kumbha', 'meena',
];

export default function CelestialSphere() {
  const t = useTranslations('hero');
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);

  const [viewMode, setViewMode] = useState<'3d' | '2d'>('3d');
  const [isAutoRotating, setIsAutoRotating] = useState(true);
  const [selectedPlanetId, setSelectedPlanetId] = useState<string>('shani');
  const [selectedRashiId, setSelectedRashiId] = useState<string | null>(null);
  const [isHovering, setIsHovering] = useState(false);

  // 3D Rotation Angles & State
  const anglesRef = useRef({
    x: 0.35,
    y: 0.45,
    targetX: 0.35,
    targetY: 0.45,
    isDragging: false,
    lastX: 0,
    lastY: 0,
  });

  const animStateRef = useRef({
    globalTime: 0,
    isVisible: true,
    projectedPlanets: [] as {
      id: string;
      x: number;
      y: number;
      z: number;
      size: number;
      scale: number;
    }[],
    projectedRashis: [] as {
      id: string;
      x: number;
      y: number;
      z: number;
      scale: number;
    }[],
  });

  // Reset View to original classical viewing angle
  const handleResetView = useCallback(() => {
    anglesRef.current.targetX = 0.35;
    anglesRef.current.targetY = 0.45;
  }, []);

  // 3D mathematical perspective projection
  const project3D = useCallback((x: number, y: number, z: number, cx: number, cy: number, fov: number) => {
    const cosY = Math.cos(anglesRef.current.y);
    const sinY = Math.sin(anglesRef.current.y);
    const x1 = x * cosY + z * sinY;
    const z1 = -x * sinY + z * cosY;

    const cosX = Math.cos(anglesRef.current.x);
    const sinX = Math.sin(anglesRef.current.x);
    const y2 = y * cosX - z1 * sinX;
    const z2 = y * sinX + z1 * cosX;

    const distance = 440;
    const scale = fov / (distance + z2);
    return {
      x: cx + x1 * scale,
      y: cy + y2 * scale,
      scale: Math.max(0.25, scale),
      z: z2,
    };
  }, []);

  // Main Canvas render loop for 3D Armillary Model
  useEffect(() => {
    if (viewMode !== '3d') return;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Handle high DPI display
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

    // Pause animation when scrolled out of viewport (0% GPU/CPU penalty)
    const observer = new IntersectionObserver(([entry]) => {
      animStateRef.current.isVisible = entry.isIntersecting;
    }, { threshold: 0.1 });

    if (containerRef.current) {
      observer.observe(containerRef.current);
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
      const fov = 390;

      ctx.clearRect(0, 0, width, height);

      // Smooth damping interpolation
      anglesRef.current.x += (anglesRef.current.targetX - anglesRef.current.x) * 0.08;
      anglesRef.current.y += (anglesRef.current.targetY - anglesRef.current.y) * 0.08;

      if (!prefersReducedMotion && isAutoRotating && !anglesRef.current.isDragging) {
        anglesRef.current.targetY += 0.0014;
        animStateRef.current.globalTime += 0.012;
      }

      // ── 1. BACKGROUND DETAILS (Sacred Almanac Parchment surface) ──
      // Soft radial warm glow behind the central reference point
      const centerGlow = ctx.createRadialGradient(cx, cy, 3, cx, cy, 210);
      centerGlow.addColorStop(0, 'rgba(239, 199, 146, 0.42)');
      centerGlow.addColorStop(0.35, 'rgba(247, 235, 215, 0.22)');
      centerGlow.addColorStop(0.7, 'rgba(250, 243, 231, 0.10)');
      centerGlow.addColorStop(1, 'rgba(250, 243, 231, 0)');
      ctx.fillStyle = centerGlow;
      ctx.fillRect(0, 0, width, height);

      // Small antique-gold decorative points at cardinal & intercardinal perimeters
      const pointDist = 205;
      for (let i = 0; i < 8; i++) {
        const rad = (i * Math.PI) / 4;
        const px = cx + Math.cos(rad) * pointDist;
        const py = cy + Math.sin(rad) * pointDist;
        ctx.beginPath();
        ctx.arc(px, py, 1.4, 0, Math.PI * 2);
        ctx.fillStyle = i % 2 === 0 ? 'rgba(220, 153, 85, 0.45)' : 'rgba(121, 20, 18, 0.25)';
        ctx.fill();
      }

      // Fine concentric reference background construction circles
      ctx.beginPath();
      ctx.arc(cx, cy, 190, 0, Math.PI * 2);
      ctx.arc(cx, cy, 148, 0, Math.PI * 2);
      ctx.arc(cx, cy, 105, 0, Math.PI * 2);
      ctx.arc(cx, cy, 60, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(220, 153, 85, 0.12)';
      ctx.lineWidth = 0.8;
      ctx.stroke();

      // Subtle dashed division circle
      ctx.save();
      ctx.setLineDash([2, 4]);
      ctx.beginPath();
      ctx.arc(cx, cy, 126, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(220, 153, 85, 0.15)';
      ctx.lineWidth = 0.7;
      ctx.stroke();
      ctx.restore();

      // Light geometric celestial construction lines (equinoctial and solstitial axes)
      ctx.beginPath();
      for (let i = 0; i < 8; i++) {
        const rad = (i * Math.PI) / 4;
        ctx.moveTo(cx + Math.cos(rad) * 35, cy + Math.sin(rad) * 35);
        ctx.lineTo(cx + Math.cos(rad) * 192, cy + Math.sin(rad) * 192);
      }
      ctx.strokeStyle = 'rgba(121, 20, 18, 0.04)';
      ctx.lineWidth = 0.6;
      ctx.stroke();

      // ── 2. CELESTIAL ARMILLARY SPHERE (3D Depth-Layered Rendering) ──
      // Helper function to render 3D rings with depth-based opacity
      const renderRingSegments = (
        radius: number,
        tiltAngle: number,
        isSecondary: boolean = false,
        isVertical: boolean = false
      ) => {
        const steps = 72;
        for (let i = 0; i < steps; i++) {
          const theta1 = (i / steps) * Math.PI * 2;
          const theta2 = ((i + 1) / steps) * Math.PI * 2;

          let x1 = 0, y1 = 0, z1 = 0;
          let x2 = 0, y2 = 0, z2 = 0;

          if (isVertical) {
            // Polar vertical meridian
            y1 = radius * Math.sin(theta1);
            z1 = radius * Math.cos(theta1);
            y2 = radius * Math.sin(theta2);
            z2 = radius * Math.cos(theta2);
          } else {
            // Horizontal or inclined ring
            const zRaw1 = radius * Math.sin(theta1);
            const zRaw2 = radius * Math.sin(theta2);
            x1 = radius * Math.cos(theta1);
            x2 = radius * Math.cos(theta2);
            y1 = Math.sin(tiltAngle) * zRaw1;
            y2 = Math.sin(tiltAngle) * zRaw2;
            z1 = Math.cos(tiltAngle) * zRaw1;
            z2 = Math.cos(tiltAngle) * zRaw2;
          }

          const p1 = project3D(x1, y1, z1, cx, cy, fov);
          const p2 = project3D(x2, y2, z2, cx, cy, fov);
          const avgZ = (p1.z + p2.z) / 2;

          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);

          // Front arcs are richer and crisper, rear arcs are softer
          if (avgZ > 0) {
            ctx.strokeStyle = isSecondary
              ? 'rgba(239, 199, 146, 0.70)'
              : 'rgba(220, 153, 85, 0.85)';
            ctx.lineWidth = isSecondary ? 1.0 : 1.6;
          } else {
            ctx.strokeStyle = isSecondary
              ? 'rgba(239, 199, 146, 0.20)'
              : 'rgba(220, 153, 85, 0.28)';
            ctx.lineWidth = isSecondary ? 0.7 : 1.0;
          }
          ctx.stroke();
        }
      };

      // 1. Secondary Horizontal Equator Ring
      renderRingSegments(140, 0, true, false);

      // 2. Inclined Orbital Colure Ring (-23.4° tilt)
      renderRingSegments(170, -0.41, true, false);

      // 3. Polar Vertical Meridian Reference Ring
      renderRingSegments(175, 0, false, true);

      // 4. Main Outer Ecliptic Zodiac Band (Inclined at 23.4° / 0.41 rad)
      const eclipticRadius = 196;
      renderRingSegments(eclipticRadius, 0.41, false, false);
      renderRingSegments(eclipticRadius - 7, 0.41, true, false);

      // Ecliptic graduation ticks along the band
      const numTicks = 36;
      for (let i = 0; i < numTicks; i++) {
        const theta = (i / numTicks) * Math.PI * 2;
        const zRaw1 = eclipticRadius * Math.sin(theta);
        const zRaw2 = (eclipticRadius - 7) * Math.sin(theta);
        const x1 = eclipticRadius * Math.cos(theta);
        const x2 = (eclipticRadius - 7) * Math.cos(theta);
        const y1 = Math.sin(0.41) * zRaw1;
        const y2 = Math.sin(0.41) * zRaw2;
        const z1 = Math.cos(0.41) * zRaw1;
        const z2 = Math.cos(0.41) * zRaw2;

        const p1 = project3D(x1, y1, z1, cx, cy, fov);
        const p2 = project3D(x2, y2, z2, cx, cy, fov);

        ctx.beginPath();
        ctx.moveTo(p1.x, p1.y);
        ctx.lineTo(p2.x, p2.y);
        ctx.strokeStyle = p1.z > 0 ? 'rgba(220, 153, 85, 0.75)' : 'rgba(220, 153, 85, 0.22)';
        ctx.lineWidth = 0.8;
        ctx.stroke();
      }

      // 5. 12 Zodiac Rashi Markers along the Ecliptic Ring
      animStateRef.current.projectedRashis = [];
      RASHIS_KEYS.forEach((key, idx) => {
        const theta = (idx / 12) * Math.PI * 2;
        const rPos = eclipticRadius - 3.5;
        const zRaw = rPos * Math.sin(theta);
        const x0 = rPos * Math.cos(theta);
        const y0 = Math.sin(0.41) * zRaw;
        const zActual = Math.cos(0.41) * zRaw;

        const p = project3D(x0, y0, zActual, cx, cy, fov);
        const isSelected = selectedRashiId === key;

        animStateRef.current.projectedRashis.push({
          id: key,
          x: p.x,
          y: p.y,
          z: p.z,
          scale: p.scale,
        });

        // Tick bead along ring
        ctx.beginPath();
        ctx.arc(p.x, p.y, isSelected ? 4.5 : 2.5, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? '#791412' : '#DC9955';
        ctx.fill();
        ctx.strokeStyle = '#FAF3E7';
        ctx.lineWidth = 1;
        ctx.stroke();

        // Rashi glyph when facing forward
        if (p.z > -40 && p.scale > 0.75) {
          ctx.beginPath();
          ctx.arc(p.x, p.y - 12, 8 * p.scale, 0, Math.PI * 2);
          ctx.fillStyle = isSelected ? '#791412' : '#F7EBD7';
          ctx.fill();
          ctx.strokeStyle = isSelected ? '#FAF3E7' : '#DC9955';
          ctx.lineWidth = 0.8;
          ctx.stroke();

          ctx.fillStyle = isSelected ? '#FAF3E7' : '#30221A';
          ctx.font = isSelected ? 'bold 10px serif' : '9px serif';
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          const glyph = t(`rashis.${key}.glyph` as any);
          ctx.fillText(glyph, p.x, p.y - 12);
        }
      });

      // 6. Navagrahas (Planetary bodies) with depth sorting
      const sortedPlanets: any[] = [];
      animStateRef.current.projectedPlanets = [];

      PLANETS_CONFIG.forEach((cfg, idx) => {
        const theta =
          animStateRef.current.globalTime * cfg.speed * 8 +
          (idx * ((Math.PI * 2) / PLANETS_CONFIG.length));
        const r = cfg.r * 0.72;
        const x = r * Math.cos(theta);
        const z = r * Math.sin(theta);
        const y = cfg.lat * r * 0.42 + Math.sin(theta * 2) * 8;

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

      // Depth sort (farther planets render first, nearer render on top)
      sortedPlanets.sort((a, b) => a.z - b.z);

      sortedPlanets.forEach((item) => {
        const isSelected = selectedPlanetId === item.cfg.id && !selectedRashiId;
        animStateRef.current.projectedPlanets.push({
          id: item.cfg.id,
          x: item.x,
          y: item.y,
          z: item.z,
          size: item.size,
          scale: item.scale,
        });

        // Subtle orbital path trace
        ctx.beginPath();
        ctx.arc(cx, cy, item.cfg.r * 0.72 * item.scale * 0.98, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(220, 153, 85, 0.07)';
        ctx.lineWidth = 0.6;
        ctx.stroke();

        // Controlled ambient glow
        ctx.beginPath();
        const aura = ctx.createRadialGradient(item.x, item.y, 1, item.x, item.y, item.size * 2.2);
        aura.addColorStop(0, item.cfg.glowColor);
        aura.addColorStop(1, 'transparent');
        ctx.fillStyle = aura;
        ctx.arc(item.x, item.y, item.size * 2.2, 0, Math.PI * 2);
        ctx.fill();

        // Planet body
        ctx.beginPath();
        ctx.arc(item.x, item.y, item.size, 0, Math.PI * 2);
        ctx.fillStyle = isSelected ? '#791412' : item.cfg.color;
        ctx.fill();
        ctx.strokeStyle = '#FAF3E7';
        ctx.lineWidth = 1.3;
        ctx.stroke();

        // Outer delicate sandstone ring
        ctx.beginPath();
        ctx.arc(item.x, item.y, item.size + 1.2, 0, Math.PI * 2);
        ctx.strokeStyle = 'rgba(220, 153, 85, 0.4)';
        ctx.lineWidth = 0.8;
        ctx.stroke();

        // Selected halo ring
        if (isSelected) {
          ctx.beginPath();
          ctx.arc(item.x, item.y, item.size + 4.5, 0, Math.PI * 2);
          ctx.strokeStyle = '#791412';
          ctx.lineWidth = 1.6;
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(item.x, item.y, item.size + 7, 0, Math.PI * 2);
          ctx.strokeStyle = 'rgba(220, 153, 85, 0.5)';
          ctx.lineWidth = 1;
          ctx.stroke();
        }

        // Planet glyph symbol
        if (item.scale > 0.72) {
          ctx.fillStyle = isSelected ? '#791412' : '#30221A';
          ctx.font = `${Math.round(10.5 * item.scale)}px sans-serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(item.cfg.glyph, item.x, item.y - item.size - 9.5);
        }
      });

      // ── 3. CENTRAL OM SYMBOL (Vedic ॐ Focal Medallion) ──
      // Subtle radiant aura
      ctx.beginPath();
      const omGlow = ctx.createRadialGradient(cx, cy, 3, cx, cy, 34);
      omGlow.addColorStop(0, 'rgba(239, 199, 146, 0.6)');
      omGlow.addColorStop(0.7, 'rgba(220, 153, 85, 0.15)');
      omGlow.addColorStop(1, 'transparent');
      ctx.fillStyle = omGlow;
      ctx.arc(cx, cy, 34, 0, Math.PI * 2);
      ctx.fill();

      // Outer Ivory circular medallion
      ctx.beginPath();
      ctx.arc(cx, cy, 17, 0, Math.PI * 2);
      ctx.fillStyle = '#FAF3E7';
      ctx.fill();
      ctx.strokeStyle = '#DC9955';
      ctx.lineWidth = 1.8;
      ctx.stroke();

      // Inner Kumkum concentric circle
      ctx.beginPath();
      ctx.arc(cx, cy, 13, 0, Math.PI * 2);
      ctx.strokeStyle = 'rgba(121, 20, 18, 0.35)';
      ctx.lineWidth = 1;
      ctx.stroke();

      // Central Devanagari ॐ in Deep Kumkum
      ctx.fillStyle = '#791412';
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
  }, [viewMode, isAutoRotating, selectedPlanetId, selectedRashiId, project3D, t]);

  // Pointer & Drag Interactions
  const handlePointerDown = (clientX: number, clientY: number) => {
    anglesRef.current.isDragging = true;
    anglesRef.current.lastX = clientX;
    anglesRef.current.lastY = clientY;
  };

  const handlePointerMove = (clientX: number, clientY: number) => {
    if (anglesRef.current.isDragging) {
      const dx = clientX - anglesRef.current.lastX;
      const dy = clientY - anglesRef.current.lastY;
      anglesRef.current.targetY += dx * 0.008;
      anglesRef.current.targetX -= dy * 0.008;
      anglesRef.current.lastX = clientX;
      anglesRef.current.lastY = clientY;
    } else if (canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;

      const hoveredPlanet = animStateRef.current.projectedPlanets.find(
        (p) => Math.hypot(p.x - mx, p.y - my) < p.size + 10
      );
      const hoveredRashi = animStateRef.current.projectedRashis.find(
        (r) => Math.hypot(r.x - mx, r.y - my) < 14
      );
      setIsHovering(Boolean(hoveredPlanet || hoveredRashi));
    }
  };

  const handlePointerUp = (clientX?: number, clientY?: number) => {
    anglesRef.current.isDragging = false;
    if (clientX !== undefined && clientY !== undefined && canvasRef.current) {
      const rect = canvasRef.current.getBoundingClientRect();
      const mx = clientX - rect.left;
      const my = clientY - rect.top;

      // Check planet click
      const clickedPlanet = animStateRef.current.projectedPlanets.find(
        (p) => Math.hypot(p.x - mx, p.y - my) < p.size + 12
      );

      if (clickedPlanet) {
        setSelectedPlanetId(clickedPlanet.id);
        setSelectedRashiId(null);
        return;
      }

      // Check rashi click
      const clickedRashi = animStateRef.current.projectedRashis.find(
        (r) => Math.hypot(r.x - mx, r.y - my) < 15
      );

      if (clickedRashi) {
        setSelectedRashiId(clickedRashi.id);
      }
    }
  };

  return (
    <div ref={containerRef} className="w-full flex flex-col items-center">
      {/* ── MAIN SACRED ALMANAC VISUALIZATION PANEL (Sacred Ivory & Kumkum) ── */}
      <div className="relative w-full max-w-[530px] rounded-[26px] bg-[#FAF3E7] border border-[#E8D5B9] ring-1 ring-[#EFC792]/40 shadow-[0_16px_40px_-8px_rgba(88,23,12,0.08),0_4px_16px_rgba(220,153,85,0.06)] overflow-hidden flex flex-col p-5 sm:p-6 transition-all">
        {/* Subtle radial parchment inner texture */}
        <div className="absolute inset-0 pointer-events-none opacity-40 bg-[radial-gradient(#DC9955_0.75px,transparent_0.75px)] [background-size:24px_24px]" />

        {/* ── TOP CONTROL BAR ── */}
        <div className="relative z-20 flex items-center justify-between pb-3.5 border-b border-[#E8D5B9]/80 gap-2">
          {/* Left Pill: Model description with celestial icon */}
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#FAF3E7] border border-[#E8D5B9] text-[11px] font-medium text-[#791412] shadow-2xs">
            <Orbit className="w-3.5 h-3.5 text-[#DC9955] shrink-0" />
            <span className="truncate">{t('controls.modelNotice')}</span>
          </div>

          {/* Right Segmented 3D / 2D Selector */}
          <div className="inline-flex p-1 rounded-full bg-[#FAF3E7] border border-[#E8D5B9] shadow-2xs shrink-0">
            <button
              type="button"
              onClick={() => setViewMode('3d')}
              className={`px-3.5 py-1 text-xs font-semibold rounded-full transition-all duration-200 ${
                viewMode === '3d'
                  ? 'bg-[#791412] text-[#FFFFFF] shadow-xs'
                  : 'text-[#30221A] hover:text-[#791412]'
              }`}
            >
              {t('controls.view3D')}
            </button>
            <button
              type="button"
              onClick={() => setViewMode('2d')}
              className={`px-3.5 py-1 text-xs font-semibold rounded-full transition-all duration-200 ${
                viewMode === '2d'
                  ? 'bg-[#791412] text-[#FFFFFF] shadow-xs'
                  : 'text-[#30221A] hover:text-[#791412]'
              }`}
            >
              {t('controls.view2D')}
            </button>
          </div>
        </div>

        {/* ── VISUAL CANVAS / MANDALA STAGE ── */}
        <div className="relative w-full aspect-square my-2 flex items-center justify-center">
          {viewMode === '3d' ? (
            <canvas
              ref={canvasRef}
              className={`w-full h-full relative z-10 touch-none ${
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
              aria-label="Vedic Armillary Celestial Sphere in Sacred Almanac design"
            />
          ) : (
            /* 2D Clean SVG Celestial Mandala Mode */
            <div className="w-full h-full relative z-10 flex items-center justify-center p-3">
              <svg viewBox="0 0 440 440" className="w-full h-full" fill="none">
                {/* Radial warm background glow */}
                <circle cx="220" cy="220" r="210" fill="url(#mandalaGlow)" />
                <defs>
                  <radialGradient id="mandalaGlow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="#EFC792" stopOpacity="0.35" />
                    <stop offset="50%" stopColor="#F7EBD7" stopOpacity="0.20" />
                    <stop offset="100%" stopColor="#FAF3E7" stopOpacity="0" />
                  </radialGradient>
                </defs>

                {/* Concentric Astronomical Mandala Rings */}
                <circle cx="220" cy="220" r="200" stroke="#DC9955" strokeWidth="1.8" />
                <circle cx="220" cy="220" r="192" stroke="#DC9955" strokeWidth="0.8" strokeOpacity="0.6" />
                <circle cx="220" cy="220" r="168" stroke="#791412" strokeWidth="1" strokeDasharray="3 4" strokeOpacity="0.4" />
                <circle cx="220" cy="220" r="138" stroke="#DC9955" strokeWidth="1" strokeOpacity="0.5" />
                <circle cx="220" cy="220" r="95" stroke="#943F28" strokeWidth="1.2" strokeOpacity="0.6" />

                {/* 12 Rashi Sectors, Rays and Glyphs */}
                {RASHIS_KEYS.map((key, i) => {
                  const angle = (i * 30 * Math.PI) / 180;
                  const x1 = 220 + 38 * Math.cos(angle);
                  const y1 = 220 + 38 * Math.sin(angle);
                  const x2 = 220 + 192 * Math.cos(angle);
                  const y2 = 220 + 192 * Math.sin(angle);
                  const isSelected = selectedRashiId === key;

                  const beadX = 220 + 180 * Math.cos(angle + 0.26);
                  const beadY = 220 + 180 * Math.sin(angle + 0.26);

                  return (
                    <g key={key} onClick={() => setSelectedRashiId(key)} className="cursor-pointer group">
                      <line x1={x1} y1={y1} x2={x2} y2={y2} stroke="#DC9955" strokeWidth="0.8" strokeOpacity="0.4" />
                      <circle
                        cx={beadX}
                        cy={beadY}
                        r={isSelected ? 11 : 9}
                        fill={isSelected ? '#791412' : '#FAF3E7'}
                        stroke={isSelected ? '#FAF3E7' : '#DC9955'}
                        strokeWidth="1.2"
                      />
                      <text
                        x={beadX}
                        y={beadY + 3.5}
                        textAnchor="middle"
                        fill={isSelected ? '#FAF3E7' : '#791412'}
                        fontSize="10"
                        fontWeight="bold"
                        fontFamily="serif"
                      >
                        {t(`rashis.${key}.glyph` as any)}
                      </text>
                    </g>
                  );
                })}

                {/* 9 Planetary Orbits & Nodes */}
                {PLANETS_CONFIG.map((p, idx) => {
                  const angle = (idx * 40 * Math.PI) / 180 + 0.2;
                  const dist = 52 + idx * 13;
                  const px = 220 + dist * Math.cos(angle);
                  const py = 220 + dist * Math.sin(angle);
                  const isSelected = selectedPlanetId === p.id && !selectedRashiId;

                  return (
                    <g
                      key={p.id}
                      onClick={() => {
                        setSelectedPlanetId(p.id);
                        setSelectedRashiId(null);
                      }}
                      className="cursor-pointer"
                    >
                      <circle cx="220" cy="220" r={dist} stroke="#DC9955" strokeWidth="0.6" strokeOpacity="0.25" />
                      {/* Ambient Glow */}
                      <circle cx={px} cy={py} r={isSelected ? 15 : 10} fill={p.glowColor} />
                      {/* Body */}
                      <circle
                        cx={px}
                        cy={py}
                        r={isSelected ? 10 : 7.5}
                        fill={isSelected ? '#791412' : p.color}
                        stroke="#FAF3E7"
                        strokeWidth="1.5"
                      />
                      <text x={px} y={py + 3} textAnchor="middle" fill="#FFFFFF" fontSize="8" fontWeight="bold">
                        {p.glyph}
                      </text>
                    </g>
                  );
                })}

                {/* Central Om Emblem */}
                <circle cx="220" cy="220" r="24" fill="#FAF3E7" stroke="#DC9955" strokeWidth="2" />
                <circle cx="220" cy="220" r="19" stroke="#791412" strokeWidth="1" strokeOpacity="0.4" />
                <text x="220" y="226" textAnchor="middle" fill="#791412" fontSize="19" fontWeight="bold" fontFamily="serif">
                  ॐ
                </text>
              </svg>
            </div>
          )}
        </div>

        {/* ── REFINED SELECTION INFORMATION CARD ── */}
        <div className="relative z-20 mt-1 p-4 rounded-xl bg-[#F7EBD7] border border-[#E8D5B9] shadow-2xs">
          {selectedRashiId ? (
            /* Selected Rashi Inspection */
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono tracking-wider font-bold text-[#791412] uppercase">
                  {t('controls.selectedSign')}
                </span>
                <button
                  type="button"
                  onClick={() => setSelectedRashiId(null)}
                  className="text-[10px] text-[#5A4438] hover:text-[#791412] underline"
                >
                  {t('controls.clearSelection')}
                </button>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-9 h-9 rounded-full bg-[#FAF3E7] border border-[#DC9955] flex items-center justify-center text-base font-bold text-[#791412] shadow-2xs shrink-0">
                  {t(`rashis.${selectedRashiId}.glyph` as any)}
                </span>
                <div>
                  <h4 className="font-serif text-base font-bold text-[#30221A]">
                    {t(`rashis.${selectedRashiId}.sanskrit` as any)} · {t(`rashis.${selectedRashiId}.english` as any)}
                  </h4>
                  <p className="text-xs text-[#5A4438]">
                    {t('controls.lord')}: <strong className="text-[#30221A]">{t(`rashis.${selectedRashiId}.lord` as any)}</strong> · {t('controls.element')}: {t(`rashis.${selectedRashiId}.element` as any)}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            /* Selected Celestial Body Inspection (Default Shani or chosen Graha) */
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono tracking-wider font-bold text-[#791412] uppercase">
                  {t('controls.selectedBody')}
                </span>
                <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-[#FAF3E7] border border-[#E8D5B9] text-[#791412] font-semibold">
                  {t(`planets.${selectedPlanetId}.role` as any)}
                </span>
              </div>
              <div className="flex items-center gap-3">
                <span className="w-9 h-9 rounded-full bg-[#FAF3E7] border border-[#DC9955] flex items-center justify-center text-lg font-bold text-[#791412] shadow-2xs shrink-0">
                  {t(`planets.${selectedPlanetId}.glyph` as any)}
                </span>
                <div>
                  <h4 className="font-serif text-base font-bold text-[#30221A]">
                    {t(`planets.${selectedPlanetId}.sanskrit` as any)} · {t(`planets.${selectedPlanetId}.name` as any)}
                  </h4>
                  <p className="text-xs text-[#5A4438] line-clamp-2">
                    {t(`planets.${selectedPlanetId}.significance` as any)}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* ── BOTTOM INTERACTION CONTROLS ── */}
        <div className="relative z-20 mt-3 pt-3 border-t border-[#E8D5B9]/80 flex flex-col sm:flex-row items-center justify-between gap-3">
          {/* Left Buttons: Pause/Resume & Reset */}
          <div className="flex items-center gap-2 w-full sm:w-auto justify-start">
            <button
              type="button"
              onClick={() => setIsAutoRotating(!isAutoRotating)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FAF3E7] border border-[#E8D5B9] text-xs font-medium text-[#30221A] hover:text-[#791412] hover:bg-[#F7EBD7] transition-colors shadow-2xs"
            >
              {isAutoRotating ? <Pause className="w-3.5 h-3.5 text-[#791412]" /> : <Play className="w-3.5 h-3.5 text-[#DC9955]" />}
              <span>{isAutoRotating ? t('controls.pauseRotate') : t('controls.resumeRotate')}</span>
            </button>

            <button
              type="button"
              onClick={handleResetView}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#FAF3E7] border border-[#E8D5B9] text-xs font-medium text-[#30221A] hover:text-[#791412] hover:bg-[#F7EBD7] transition-colors shadow-2xs"
            >
              <RotateCcw className="w-3.5 h-3.5 text-[#791412]" />
              <span>{t('controls.resetView')}</span>
            </button>
          </div>

          {/* Right Instruction Notice */}
          <span className="text-[11px] text-[#5A4438] text-center sm:text-right">
            {t('controls.dragPrompt')}
          </span>
        </div>
      </div>

      {/* ── ACCESSIBLE SELECTION CHIPS (Below main visualization) ── */}
      <div className="w-full max-w-[530px] mt-3.5 space-y-2">
        <div className="flex flex-wrap gap-1.5 justify-center sm:justify-start">
          {PLANETS_CONFIG.map((p) => {
            const isSelected = selectedPlanetId === p.id && !selectedRashiId;
            return (
              <button
                key={p.id}
                type="button"
                onClick={() => {
                  setSelectedPlanetId(p.id);
                  setSelectedRashiId(null);
                }}
                className={`px-2.5 py-1 rounded-md text-xs font-serif flex items-center gap-1 transition-all ${
                  isSelected
                    ? 'bg-[#791412] text-[#FAF3E7] font-bold shadow-xs scale-105'
                    : 'bg-[#FAF3E7] text-[#30221A] hover:bg-[#F7EBD7] border border-[#E8D5B9]'
                }`}
                aria-pressed={isSelected}
              >
                <span>{p.glyph}</span>
                <span>{t(`planets.${p.id}.sanskrit` as any)}</span>
              </button>
            );
          })}
        </div>

        <div className="flex flex-wrap gap-1 justify-center sm:justify-start">
          {RASHIS_KEYS.map((key) => {
            const isSelected = selectedRashiId === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => setSelectedRashiId(key)}
                className={`px-2 py-0.5 rounded text-[11px] font-serif transition-colors ${
                  isSelected
                    ? 'bg-[#943F28] text-[#FAF3E7] font-bold shadow-xs'
                    : 'bg-[#FAF3E7] text-[#5A4438] hover:text-[#791412] border border-[#E8D5B9]'
                }`}
                aria-pressed={isSelected}
              >
                <span>{t(`rashis.${key}.glyph` as any)}</span> {t(`rashis.${key}.sanskrit` as any)}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
