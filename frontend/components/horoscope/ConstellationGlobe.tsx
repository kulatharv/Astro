'use client';

import React, { useState, useRef, useCallback, useMemo } from 'react';
import { Sparkles } from 'lucide-react';

interface StarNode {
  x: number;
  y: number;
  r: number;
  name?: string;
  mag?: number;
}

interface ConstellationData {
  stars: StarNode[];
  edges: [number, number][];
}

// 12 Astrological Constellation Star Patterns (Normalized 0..200 viewBox)
const CONSTELLATIONS: Record<string, ConstellationData> = {
  // Aries (Mesha)
  mesha: {
    stars: [
      { x: 45, y: 135, r: 3, name: 'Mesarthim' },
      { x: 95, y: 105, r: 4, name: 'Sheratan' },
      { x: 155, y: 70, r: 5.5, name: 'Hamal (Alpha Arietis)' },
      { x: 175, y: 85, r: 2.8, name: '41 Arietis' },
    ],
    edges: [[0, 1], [1, 2], [2, 3]],
  },
  // Taurus (Vrishabha)
  vrishabha: {
    stars: [
      { x: 50, y: 140, r: 3, name: 'Hyadum I' },
      { x: 95, y: 110, r: 6, name: 'Aldebaran (Rohini)' },
      { x: 115, y: 85, r: 3.5, name: 'Ain' },
      { x: 165, y: 45, r: 4.5, name: 'Elnath' },
      { x: 175, y: 115, r: 4, name: 'Zeta Tauri' },
      { x: 65, y: 55, r: 4, name: 'Pleiades (Krittika)' },
    ],
    edges: [[0, 1], [1, 2], [2, 3], [1, 4], [2, 5]],
  },
  // Gemini (Mithuna)
  mithuna: {
    stars: [
      { x: 60, y: 45, r: 5, name: 'Castor' },
      { x: 95, y: 55, r: 5.5, name: 'Pollux (Punarvasu)' },
      { x: 50, y: 115, r: 3.5, name: 'Mebsuta' },
      { x: 90, y: 125, r: 3.8, name: 'Wasat' },
      { x: 40, y: 165, r: 4, name: 'Tejat' },
      { x: 85, y: 170, r: 4.2, name: 'Alhena' },
    ],
    edges: [[0, 2], [2, 4], [1, 3], [3, 5], [0, 1], [2, 3]],
  },
  // Cancer (Karka)
  karka: {
    stars: [
      { x: 100, y: 60, r: 4, name: 'Tegmine' },
      { x: 100, y: 105, r: 5, name: 'Asellus Borealis' },
      { x: 60, y: 155, r: 4, name: 'Acubens' },
      { x: 140, y: 160, r: 4.5, name: 'Al Tarf' },
      { x: 100, y: 120, r: 4, name: 'Praesepe (Pushya)' },
    ],
    edges: [[0, 1], [1, 2], [1, 3], [1, 4]],
  },
  // Leo (Simha)
  simha: {
    stars: [
      { x: 55, y: 155, r: 6, name: 'Regulus (Magha)' },
      { x: 75, y: 120, r: 4, name: 'Eta Leonis' },
      { x: 85, y: 85, r: 4.5, name: 'Algieba' },
      { x: 70, y: 60, r: 3.8, name: 'Adhafera' },
      { x: 95, y: 45, r: 3.5, name: 'Ras Elased' },
      { x: 145, y: 95, r: 4.2, name: 'Zosma' },
      { x: 170, y: 115, r: 5, name: 'Denebola' },
      { x: 135, y: 140, r: 4, name: 'Chertan' },
    ],
    edges: [[0, 1], [1, 2], [2, 3], [3, 4], [2, 5], [5, 6], [6, 7], [7, 0]],
  },
  // Virgo (Kanya)
  kanya: {
    stars: [
      { x: 50, y: 65, r: 4, name: 'Zavijava' },
      { x: 80, y: 90, r: 4.5, name: 'Porrima' },
      { x: 110, y: 115, r: 4, name: 'Auva' },
      { x: 145, y: 145, r: 6.5, name: 'Spica (Chitra)' },
      { x: 105, y: 55, r: 4.2, name: 'Vindemiatrix' },
      { x: 165, y: 115, r: 3.8, name: 'Heze' },
    ],
    edges: [[0, 1], [1, 2], [2, 3], [1, 4], [2, 5], [5, 3]],
  },
  // Libra (Tula)
  tula: {
    stars: [
      { x: 65, y: 60, r: 5, name: 'Zubeneschamali' },
      { x: 65, y: 145, r: 5, name: 'Zubenelgenubi' },
      { x: 140, y: 130, r: 4.5, name: 'Brachium' },
      { x: 135, y: 75, r: 4, name: 'Zubenelhakrabi' },
    ],
    edges: [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]],
  },
  // Scorpio (Vrishchika)
  vrishchika: {
    stars: [
      { x: 45, y: 65, r: 4.2, name: 'Graffias' },
      { x: 55, y: 85, r: 4.5, name: 'Dschubba' },
      { x: 85, y: 105, r: 6.5, name: 'Antares (Jyeshtha)' },
      { x: 105, y: 130, r: 4, name: 'Larawag' },
      { x: 125, y: 155, r: 4.2, name: 'Sargas' },
      { x: 155, y: 145, r: 5, name: 'Shaula (Mula)' },
      { x: 165, y: 125, r: 4.5, name: 'Lesath' },
    ],
    edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6]],
  },
  // Sagittarius (Dhanu)
  dhanu: {
    stars: [
      { x: 60, y: 140, r: 4.5, name: 'Alnasl' },
      { x: 85, y: 115, r: 5, name: 'Kaus Media' },
      { x: 95, y: 150, r: 5.5, name: 'Kaus Australis' },
      { x: 80, y: 80, r: 4.5, name: 'Kaus Borealis' },
      { x: 125, y: 95, r: 5, name: 'Nunki' },
      { x: 145, y: 125, r: 4.5, name: 'Ascella' },
    ],
    edges: [[0, 1], [1, 2], [2, 0], [1, 3], [3, 4], [4, 5], [5, 2], [1, 5]],
  },
  // Capricorn (Makara)
  makara: {
    stars: [
      { x: 50, y: 65, r: 4.5, name: 'Algedi' },
      { x: 65, y: 85, r: 4.5, name: 'Dabih' },
      { x: 115, y: 155, r: 4, name: 'Oculus' },
      { x: 165, y: 105, r: 4.5, name: 'Nashira' },
      { x: 175, y: 85, r: 5, name: 'Deneb Algedi' },
    ],
    edges: [[0, 1], [1, 2], [2, 3], [3, 4], [4, 0]],
  },
  // Aquarius (Kumbha)
  kumbha: {
    stars: [
      { x: 65, y: 60, r: 5, name: 'Sadalmelik' },
      { x: 110, y: 55, r: 5.5, name: 'Sadalsuud' },
      { x: 145, y: 85, r: 4.2, name: 'Sadachbia' },
      { x: 85, y: 115, r: 4, name: 'Ancha' },
      { x: 125, y: 160, r: 5, name: 'Skat' },
    ],
    edges: [[0, 1], [1, 2], [0, 3], [3, 4], [2, 4]],
  },
  // Pisces (Meena)
  meena: {
    stars: [
      { x: 45, y: 70, r: 4.5, name: 'Fumalsamakah' },
      { x: 85, y: 95, r: 4, name: 'Linteum' },
      { x: 130, y: 140, r: 5.5, name: 'Alrescha (Revati)' },
      { x: 155, y: 100, r: 4, name: 'Torcular' },
      { x: 170, y: 60, r: 4.5, name: 'Kullat Nunu' },
    ],
    edges: [[0, 1], [1, 2], [2, 3], [3, 4]],
  },
};

interface ConstellationGlobeProps {
  signId: string;
  signName: string;
  glyph: string;
  element?: string;
  rulingPlanet?: string;
}

export default function ConstellationGlobe({
  signId,
  signName,
  glyph,
  element = 'Fire',
  rulingPlanet = 'Surya',
}: ConstellationGlobeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [tilt, setTilt] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredStar, setHoveredStar] = useState<StarNode | null>(null);

  const constellation = useMemo(() => {
    return CONSTELLATIONS[signId.toLowerCase()] || CONSTELLATIONS.mesha;
  }, [signId]);

  // Mouse Parallax 3D Tilt
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const px = (x / rect.width) * 2 - 1;
    const py = (y / rect.height) * 2 - 1;
    setTilt({ x: -py * 12, y: px * 12 });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setTilt({ x: 0, y: 0 });
    setHoveredStar(null);
  }, []);

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{ perspective: '800px' }}
      className="relative w-28 h-28 sm:w-32 sm:h-32 shrink-0 select-none cursor-pointer group"
    >
      <div
        style={{
          transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
          transformStyle: 'preserve-3d',
          transition: 'transform 0.15s ease-out',
        }}
        className="w-full h-full rounded-2xl bg-linear-to-br from-[#24120B] via-[#4A100B] to-[#7A1612] border-2 border-[#C5A059] shadow-[0_10px_25px_-5px_rgba(122,22,18,0.35)] relative flex items-center justify-center p-2 overflow-hidden"
      >
        {/* Ambient Nebula Radial Aura */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(197,160,89,0.35)_0%,transparent_75%)] pointer-events-none" />

        {/* Delicate background celestial alignment grid */}
        <div className="absolute inset-0 opacity-20 bg-[radial-gradient(#FAF6F0_1px,transparent_1px)] [background-size:12px_12px] pointer-events-none" />

        {/* SVG Constellation Astrolabe */}
        <svg viewBox="0 0 200 200" className="w-full h-full relative z-10 overflow-visible">
          <defs>
            <filter id="starTwinkleGlow" x="-30%" y="-30%" width="160%" height="160%">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Golden Outer Reticle Ring */}
          <circle cx="100" cy="100" r="92" fill="none" stroke="#C5A059" strokeWidth="0.8" strokeDasharray="3 4" strokeOpacity="0.5" />
          <circle cx="100" cy="100" r="86" fill="none" stroke="#C5A059" strokeWidth="0.5" strokeOpacity="0.3" />

          {/* Constellation Golden Interconnect Beams */}
          {constellation.edges.map(([fromIdx, toIdx], edgeIdx) => {
            const p1 = constellation.stars[fromIdx];
            const p2 = constellation.stars[toIdx];
            if (!p1 || !p2) return null;
            return (
              <line
                key={edgeIdx}
                x1={p1.x}
                y1={p1.y}
                x2={p2.x}
                y2={p2.y}
                stroke="#FAF6F0"
                strokeWidth="1.2"
                strokeOpacity="0.65"
                strokeDasharray="2 1"
              />
            );
          })}

          {/* Twinkling Star Vertices */}
          {constellation.stars.map((star, idx) => {
            const isHovered = hoveredStar?.name === star.name;
            return (
              <g
                key={idx}
                onMouseEnter={() => setHoveredStar(star)}
                className="cursor-pointer"
              >
                {/* Ambient pulse halo */}
                <circle
                  cx={star.x}
                  cy={star.y}
                  r={star.r * 2.2}
                  fill="#C5A059"
                  fillOpacity="0.3"
                  className="animate-pulse"
                />
                {/* Specular White Core */}
                <circle
                  cx={star.x}
                  cy={star.y}
                  r={star.r}
                  fill="#FAF6F0"
                  stroke="#C5A059"
                  strokeWidth="1"
                  filter="url(#starTwinkleGlow)"
                />
              </g>
            );
          })}

          {/* Subtle Central Zodiac Glyph Watermark */}
          <text
            x="100"
            y="112"
            textAnchor="middle"
            fill="#FAF6F0"
            fillOpacity="0.12"
            fontSize="54"
            fontFamily="serif"
            className="select-none pointer-events-none"
          >
            {glyph}
          </text>
        </svg>

        {/* Bottom Astrological Glyph Tag */}
        <div className="absolute bottom-1.5 left-2 right-2 flex items-center justify-between pointer-events-none z-20">
          <span className="text-[10px] font-mono text-[#FAF6F0]/80 font-bold">
            {glyph}
          </span>
          <span className="text-[8px] font-mono tracking-wider text-[#C5A059] uppercase">
            3D Globe
          </span>
        </div>
      </div>

      {/* Floating Star Name Tooltip */}
      {hoveredStar?.name && (
        <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 bg-[#24120B] text-[#FAF6F0] border border-[#C5A059] px-2 py-0.5 rounded text-[10px] whitespace-nowrap shadow-md z-30 pointer-events-none">
          ✦ {hoveredStar.name}
        </div>
      )}
    </div>
  );
}
