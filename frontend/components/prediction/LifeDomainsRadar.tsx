'use client';

import React, { useState, useRef, useEffect, useMemo, useCallback } from 'react';
import { Sparkles, Eye, Compass, ShieldCheck } from 'lucide-react';
import { DOMAINS_LIST, type DomainMeta } from './predictionLocalization';

interface LifeDomainsRadarProps {
  domainsData: any;
  activeDomainKey: string;
  onSelectDomain: (key: string) => void;
  locale: string;
}

export default function LifeDomainsRadar({
  domainsData,
  activeDomainKey,
  onSelectDomain,
  locale,
}: LifeDomainsRadarProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [is3DActive, setIs3DActive] = useState<boolean>(true);
  const [hoveredDomainKey, setHoveredDomainKey] = useState<string | null>(null);
  const [tilt, setTilt] = useState<{ x: number; y: number; sheenX: number; sheenY: number }>({
    x: 0,
    y: 0,
    sheenX: 50,
    sheenY: 50,
  });

  // Reduced motion preference
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)');
    setPrefersReducedMotion(mq.matches);
    const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
    mq.addEventListener('change', handler);
    return () => mq.removeEventListener('change', handler);
  }, []);

  // Center & Radius geometry
  const cx = 210;
  const cy = 210;
  const radius = 135;
  const N = DOMAINS_LIST.length; // 10 domains

  // Calculate spoke angles (starting from 12 o'clock / -PI/2)
  const spokes = useMemo(() => {
    return DOMAINS_LIST.map((dm, idx) => {
      const angle = -Math.PI / 2 + (idx * 2 * Math.PI) / N;
      const cos = Math.cos(angle);
      const sin = Math.sin(angle);
      const domainData = domainsData?.domains?.[dm.key] || {};
      const rawScore = typeof domainData.score === 'number' ? domainData.score : 60;
      const score = Math.max(15, Math.min(100, rawScore));
      const dist = (score / 100) * radius;

      const title =
        locale === 'mr' ? dm.mrName : locale === 'hi' ? dm.hiName : dm.enName;

      return {
        meta: dm,
        idx,
        angle,
        cos,
        sin,
        score,
        status: domainData.status || 'Good',
        dashaActive: Boolean(domainData.dasha_active),
        lord: domainData.primary_lord || '—',
        // Coordinate on outer rim (100%)
        outerX: cx + radius * cos,
        outerY: cy + radius * sin,
        // Coordinate for label (further out)
        labelX: cx + (radius + 28) * cos,
        labelY: cy + (radius + 28) * sin,
        // Coordinate of user data point
        dataX: cx + dist * cos,
        dataY: cy + dist * sin,
        title,
      };
    });
  }, [domainsData, locale, N]);

  // Concentric polygon grids (20%, 40%, 60%, 80%, 100%)
  const gridPolygons = useMemo(() => {
    const levels = [0.2, 0.4, 0.6, 0.8, 1.0];
    return levels.map((lvl) => {
      const pts = spokes
        .map((sp) => `${cx + radius * lvl * sp.cos},${cy + radius * lvl * sp.sin}`)
        .join(' ');
      return { level: lvl, pts };
    });
  }, [spokes, cx, cy, radius]);

  // Score Polygon Path String
  const dataPolygonPts = useMemo(() => {
    return spokes.map((sp) => `${sp.dataX},${sp.dataY}`).join(' ');
  }, [spokes]);

  // Mouse Parallax 3D Perspective Tilt Handlers
  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLDivElement>) => {
      if (!is3DActive || prefersReducedMotion) return;
      const el = containerRef.current;
      if (!el) return;

      const rect = el.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const px = (x / rect.width) * 2 - 1; // -1 to 1
      const py = (y / rect.height) * 2 - 1; // -1 to 1

      setTilt({
        x: -py * 10, // Rotate around X axis
        y: px * 10,  // Rotate around Y axis
        sheenX: (x / rect.width) * 100,
        sheenY: (y / rect.height) * 100,
      });
    },
    [is3DActive, prefersReducedMotion]
  );

  const handleMouseLeave = useCallback(() => {
    setTilt({ x: 0, y: 0, sheenX: 50, sheenY: 50 });
    setHoveredDomainKey(null);
  }, []);

  const activeSpoke = spokes.find((s) => s.meta.key === (hoveredDomainKey || activeDomainKey));

  return (
    <div className="w-full flex flex-col items-center my-6">
      {/* ── CARD HEADER & 3D CONTROLS ── */}
      <div className="w-full max-w-[620px] flex items-center justify-between px-3 py-2 border-b border-[#F9DAB5]">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-[#821C17] animate-spin-slow" />
          <h4 className="font-serif text-sm font-bold text-[#821C17]">
            {locale === 'mr'
              ? '१० जीवन क्षेत्र जायरोस्कोप रडार'
              : locale === 'hi'
              ? '१० जीवन क्षेत्र जाइरोस्कोप रडार'
              : '10 Life Domains Gyroscopic Radar'}
          </h4>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setIs3DActive(!is3DActive)}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold transition-all shadow-2xs cursor-pointer ${
              is3DActive
                ? 'bg-[#821C17] text-[#FDF5E6]'
                : 'bg-[#FCEBD2] text-[#421A10] border border-[#F9DAB5]'
            }`}
            title="Toggle 3D gyroscopic perspective"
          >
            <Sparkles className="w-3 h-3" />
            <span>{is3DActive ? '3D Active' : 'Flat 2D'}</span>
          </button>
        </div>
      </div>

      {/* ── 3D PERSPECTIVE STAGE CONTAINER ── */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{
          perspective: is3DActive ? '1000px' : 'none',
        }}
        className="w-full max-w-[620px] p-4 flex flex-col items-center justify-center relative select-none"
      >
        <div
          style={{
            transform:
              is3DActive && !prefersReducedMotion
                ? `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`
                : 'none',
            transformStyle: 'preserve-3d',
            transition: 'transform 0.14s ease-out',
          }}
          className="relative w-full aspect-square max-w-[460px] rounded-3xl bg-[#FAF3E7] border border-[#F9DAB5] shadow-[0_16px_36px_-10px_rgba(130,28,23,0.14)] p-4 flex items-center justify-center overflow-visible"
        >
          {/* Specular Sheen Layer reacting to tilt */}
          {is3DActive && !prefersReducedMotion && (
            <div
              className="absolute inset-0 rounded-3xl pointer-events-none transition-opacity duration-300 z-20"
              style={{
                background: `radial-gradient(circle at ${tilt.sheenX}% ${tilt.sheenY}%, rgba(255,255,255,0.45) 0%, rgba(247,218,181,0.12) 40%, transparent 70%)`,
                mixBlendMode: 'overlay',
              }}
            />
          )}

          {/* SVG RADAR MANDALA */}
          <svg
            viewBox="0 0 420 420"
            className="w-full h-full relative z-10 overflow-visible"
          >
            <defs>
              {/* Radial warm background */}
              <radialGradient id="radarBgGlow" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#F7EBD7" stopOpacity="0.8" />
                <stop offset="70%" stopColor="#FAF3E7" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#FAF3E7" stopOpacity="0" />
              </radialGradient>

              {/* Data polygon gold/kumkum gradient */}
              <radialGradient id="dataPolyGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#C46B1E" stopOpacity="0.45" />
                <stop offset="60%" stopColor="#821C17" stopOpacity="0.32" />
                <stop offset="100%" stopColor="#791412" stopOpacity="0.18" />
              </radialGradient>

              {/* Active pulse glow filter */}
              <filter id="radarGlow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
              </filter>
            </defs>

            {/* Background Glow Circle */}
            <circle cx={cx} cy={cy} r={radius + 15} fill="url(#radarBgGlow)" />

            {/* Concentric 10-gon Grids */}
            {gridPolygons.map(({ level, pts }) => (
              <g key={level}>
                <polygon
                  points={pts}
                  fill="none"
                  stroke="#E8D5B9"
                  strokeWidth={level === 1.0 ? '1.5' : '0.8'}
                  strokeDasharray={level === 1.0 ? undefined : '2 3'}
                />
                {/* Level Percentage Label at 12 o'clock */}
                <text
                  x={cx + 3}
                  y={cy - radius * level - 2}
                  fontSize="8"
                  fill="#C46B1E"
                  opacity="0.6"
                  fontFamily="monospace"
                >
                  {Math.round(level * 100)}%
                </text>
              </g>
            ))}

            {/* 10 Spoke Lines */}
            {spokes.map((sp) => (
              <line
                key={sp.meta.key}
                x1={cx}
                y1={cy}
                x2={sp.outerX}
                y2={sp.outerY}
                stroke={sp.meta.key === activeDomainKey ? '#821C17' : '#E8D5B9'}
                strokeWidth={sp.meta.key === activeDomainKey ? '1.5' : '0.8'}
                strokeOpacity={sp.meta.key === activeDomainKey ? '0.9' : '0.6'}
              />
            ))}

            {/* Filled Data Polygon */}
            <polygon
              points={dataPolygonPts}
              fill="url(#dataPolyGrad)"
              stroke="#821C17"
              strokeWidth="2.2"
              strokeLinejoin="round"
              className="transition-all duration-300"
            />

            {/* Interactive Data Vertices & Rings */}
            {spokes.map((sp) => {
              const isSelected = sp.meta.key === activeDomainKey;
              const isHovered = sp.meta.key === hoveredDomainKey;
              const nodeColor =
                sp.score >= 75
                  ? '#15803D'
                  : sp.score >= 55
                  ? '#C46B1E'
                  : sp.score >= 35
                  ? '#EA580C'
                  : '#DC2626';

              return (
                <g
                  key={sp.meta.key}
                  className="cursor-pointer group"
                  onClick={() => onSelectDomain(sp.meta.key)}
                  onMouseEnter={() => setHoveredDomainKey(sp.meta.key)}
                >
                  {/* Outer pulsating ring for active domain */}
                  {isSelected && (
                    <circle
                      cx={sp.dataX}
                      cy={sp.dataY}
                      r="13"
                      fill="none"
                      stroke="#821C17"
                      strokeWidth="1.5"
                      strokeOpacity="0.5"
                      className="animate-ping"
                    />
                  )}

                  {/* Halo highlight */}
                  {(isSelected || isHovered) && (
                    <circle
                      cx={sp.dataX}
                      cy={sp.dataY}
                      r="10"
                      fill={nodeColor}
                      fillOpacity="0.25"
                    />
                  )}

                  {/* Node Bead */}
                  <circle
                    cx={sp.dataX}
                    cy={sp.dataY}
                    r={isSelected ? 6.5 : 4.5}
                    fill={nodeColor}
                    stroke="#FAF3E7"
                    strokeWidth="1.5"
                    filter="url(#radarGlow)"
                    className="transition-transform group-hover:scale-125"
                  />

                  {/* Outer Spoke Label Button */}
                  <g
                    transform={`translate(${sp.labelX}, ${sp.labelY})`}
                    className="transition-all duration-200"
                  >
                    <rect
                      x="-38"
                      y="-11"
                      width="76"
                      height="20"
                      rx="10"
                      fill={isSelected ? '#821C17' : '#FCEBD2'}
                      stroke={isSelected ? '#FAF3E7' : '#F9DAB5'}
                      strokeWidth="1"
                      className="shadow-2xs group-hover:fill-[#821C17]"
                    />
                    <text
                      x="0"
                      y="2.5"
                      textAnchor="middle"
                      fill={isSelected ? '#FAF3E7' : '#421A10'}
                      fontSize="9"
                      fontWeight={isSelected ? 'bold' : 'normal'}
                      fontFamily="sans-serif"
                      className="group-hover:fill-[#FAF3E7] select-none"
                    >
                      {sp.title.split(' ')[0]} {sp.score}%
                    </text>
                  </g>
                </g>
              );
            })}

            {/* Central Focal Emblem */}
            <circle cx={cx} cy={cy} r="16" fill="#FAF3E7" stroke="#C46B1E" strokeWidth="1.5" />
            <circle cx={cx} cy={cy} r="12" stroke="#821C17" strokeWidth="0.8" strokeOpacity="0.4" />
            <text
              x={cx}
              y={cy + 4.5}
              textAnchor="middle"
              fill="#821C17"
              fontSize="12"
              fontWeight="bold"
              fontFamily="serif"
            >
              ॐ
            </text>
          </svg>
        </div>
      </div>

      {/* ── ACTIVE SPOKE QUICK INSPECTION PILL ── */}
      {activeSpoke && (
        <div className="w-full max-w-[620px] mt-2 px-4 py-2.5 rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] flex items-center justify-between text-xs text-[#421A10]">
          <div className="flex items-center gap-2.5">
            <span
              className="w-3 h-3 rounded-full"
              style={{
                backgroundColor:
                  activeSpoke.score >= 75
                    ? '#15803D'
                    : activeSpoke.score >= 55
                    ? '#C46B1E'
                    : activeSpoke.score >= 35
                    ? '#EA580C'
                    : '#DC2626',
              }}
            />
            <span className="font-serif font-bold text-[#821C17]">
              {activeSpoke.title}
            </span>
            <span className="text-[11px] text-[#421A10]/70 font-mono">
              ({activeSpoke.meta.house})
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="font-mono font-bold text-sm text-[#821C17]">
              {activeSpoke.score}%
            </span>
            <span className="px-2 py-0.5 rounded-md bg-[#FAF3E7] text-[10px] font-semibold border border-[#F9DAB5]">
              {activeSpoke.status}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
