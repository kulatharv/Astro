'use client';

import React, { useState, useRef, useCallback, useMemo } from 'react';
import { RASHI_NAMES_MAP, PLANET_NAMES_MAP } from './kundaliLocalization';
import { Eye, Sparkles, Orbit, RotateCcw } from 'lucide-react';

interface KundaliChartProps {
  style?: 'north' | 'south';
  varga?: 'd1' | 'd9';
  lagnaSign: string;
  housesData: Record<string | number, string[]>;
  planets?: Array<{
    name: string;
    sign: string;
    degree?: string;
    house?: number;
    retrograde?: boolean;
    strength?: string;
  }>;
  selectedHouse?: number | null;
  onSelectHouse?: (house: number) => void;
  locale?: string;
}

// North-Indian layout: Visual cell index (1..12) -> Astrological House (1..12)
const NORTH_POSITION_MAP: Record<number, number> = {
  1: 1, 2: 12, 3: 11, 4: 2, 5: 10, 6: 3, 7: 9, 8: 4, 9: 5, 10: 6, 11: 7, 12: 8
};

// Inverse map: Astrological House (1..12) -> Visual Cell Index (1..12)
const NORTH_HOUSE_TO_POS: Record<number, number> = {
  1: 1, 12: 2, 11: 3, 2: 4, 10: 5, 3: 6, 9: 7, 4: 8, 5: 9, 6: 10, 7: 11, 8: 12
};

// SVG geometry coordinates for North Indian chart visual positions
const NORTH_HOUSE_COORDS: Record<number, { nx: number; ny: number; px: number; py: number; polygon?: string }> = {
  1:  { nx: 300, ny: 155, px: 300, py: 105, polygon: "300,10 445,110 300,210 155,110" },      // H1 (Top Diamond)
  2:  { nx: 200, ny: 55,  px: 235, py: 75,  polygon: "10,10 155,110 300,10" },                 // H12 (Top Left Triangle)
  3:  { nx: 70,  ny: 95,  px: 75,  py: 115, polygon: "10,10 155,110 10,210" },                 // H11 (Far Top Left)
  4:  { nx: 400, ny: 55,  px: 365, py: 75,  polygon: "300,10 445,110 590,10" },                // H2 (Top Right Triangle)
  5:  { nx: 530, ny: 95,  px: 525, py: 115, polygon: "590,10 445,110 590,210" },               // H10 (Far Top Right)
  6:  { nx: 70,  ny: 320, px: 75,  py: 295, polygon: "10,210 155,310 10,410" },                // H3 (Far Bottom Left)
  7:  { nx: 200, ny: 360, px: 235, py: 335, polygon: "10,410 155,310 300,410" },               // H9 (Bottom Left Triangle)
  8:  { nx: 155, ny: 215, px: 220, py: 210, polygon: "155,110 300,210 155,310 10,210" },      // H4 (Left Diamond)
  9:  { nx: 445, ny: 215, px: 380, py: 210, polygon: "445,110 590,210 445,310 300,210" },      // H5 (Right Diamond)
  10: { nx: 530, ny: 320, px: 525, py: 295, polygon: "590,210 445,310 590,410" },               // H6 (Far Bottom Right)
  11: { nx: 400, ny: 360, px: 365, py: 335, polygon: "300,410 445,310 590,410" },               // H7 (Bottom Right Triangle)
  12: { nx: 300, ny: 260, px: 300, py: 310, polygon: "300,210 445,310 300,410 155,310" },      // H8 (Bottom Diamond)
};

// South Indian fixed signs in clockwise order starting from Pisces (top-left inner)
const SOUTH_SIGN_LAYOUT: Array<{ signNum: number; signKey: string; col: number; row: number }> = [
  { signNum: 12, signKey: 'Meena', col: 0, row: 0 },
  { signNum: 1,  signKey: 'Mesha', col: 1, row: 0 },
  { signNum: 2,  signKey: 'Vrishabha', col: 2, row: 0 },
  { signNum: 3,  signKey: 'Mithuna', col: 3, row: 0 },
  { signNum: 4,  signKey: 'Karka', col: 3, row: 1 },
  { signNum: 5,  signKey: 'Simha', col: 3, row: 2 },
  { signNum: 6,  signKey: 'Kanya', col: 3, row: 3 },
  { signNum: 7,  signKey: 'Tula', col: 2, row: 3 },
  { signNum: 8,  signKey: 'Vrischika', col: 1, row: 3 },
  { signNum: 9,  signKey: 'Dhanu', col: 0, row: 3 },
  { signNum: 10, signKey: 'Makara', col: 0, row: 2 },
  { signNum: 11, signKey: 'Kumbha', col: 0, row: 1 },
];

// Classical Parashara Jyotish Drishti (Aspect) Calculations
function getVedicAspects(sourceHouse: number, planetsInHouse: string[]): Array<{ targetHouse: number; rule: string; color: string }> {
  const aspects: Array<{ targetHouse: number; rule: string; color: string }> = [];
  const addAspect = (offset: number, rule: string, color: string) => {
    const target = ((sourceHouse + offset - 1) % 12) + 1;
    if (!aspects.some(a => a.targetHouse === target)) {
      aspects.push({ targetHouse: target, rule, color });
    }
  };

  // 1. All planets cast full 7th aspect (Saptama Drishti)
  if (planetsInHouse.length > 0) {
    addAspect(6, '7th Full Aspect (सप्तम दृष्टी)', '#C5A059');
  }

  // 2. Special Graha Drishti
  for (const p of planetsInHouse) {
    const name = p.toLowerCase();
    // Jupiter, Rahu, Ketu cast 5th and 9th aspects
    if (name.includes('jupiter') || name.includes('guru') || name.includes('rahu') || name.includes('ketu')) {
      addAspect(4, '5th Trine Aspect (पंचम दृष्टी)', '#A85A1E');
      addAspect(8, '9th Dharma Aspect (नवम दृष्टी)', '#A85A1E');
    }
    // Mars casts 4th and 8th aspects
    if (name.includes('mars') || name.includes('mangal') || name.includes('mangala')) {
      addAspect(3, '4th Quadrant Aspect (चतुर्थ दृष्टी)', '#7A1612');
      addAspect(7, '8th Occult Aspect (अष्टम दृष्टी)', '#7A1612');
    }
    // Saturn casts 3rd and 10th aspects
    if (name.includes('saturn') || name.includes('shani')) {
      addAspect(2, '3rd Effort Aspect (तृतीय दृष्टी)', '#24120B');
      addAspect(9, '10th Karma Aspect (दशम दृष्टी)', '#24120B');
    }
  }

  return aspects;
}

export default function KundaliChart({
  style = 'north',
  varga = 'd1',
  lagnaSign,
  housesData,
  planets = [],
  selectedHouse = null,
  onSelectHouse,
  locale = 'en',
}: KundaliChartProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [hoveredHouse, setHoveredHouse] = useState<number | null>(null);
  const [enable3D, setEnable3D] = useState<boolean>(true);
  const [tilt, setTilt] = useState<{ x: number; y: number; sheenX: number; sheenY: number }>({
    x: 0,
    y: 0,
    sheenX: 50,
    sheenY: 50,
  });

  const activeFocusHouse = hoveredHouse ?? selectedHouse;

  const lagnaRashiInfo = RASHI_NAMES_MAP[lagnaSign] || { num: 1 };
  const lagnaRashiNum = lagnaRashiInfo.num;

  const retroSet = useMemo(() => {
    return new Set(planets.filter((p) => p.retrograde).map((p) => p.name));
  }, [planets]);

  // Compute active Vedic aspects from focused house
  const activeAspects = useMemo(() => {
    if (!activeFocusHouse) return [];
    const planetsInFocused = (housesData[activeFocusHouse] || []).filter((p) => p !== 'Lagna');
    return getVedicAspects(activeFocusHouse, planetsInFocused);
  }, [activeFocusHouse, housesData]);

  // Interactive 3D cursor tracking
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    if (!enable3D || !containerRef.current) return;
    const rect = containerRef.current.getBoundingClientRect();
    const xRatio = (e.clientX - rect.left) / rect.width;
    const yRatio = (e.clientY - rect.top) / rect.height;

    // Constrain tilt to elegant, subtle horology perspective (-8deg to +8deg)
    const rotY = (xRatio - 0.5) * 14;
    const rotX = (0.5 - yRatio) * 14;

    setTilt({
      x: rotX,
      y: rotY,
      sheenX: xRatio * 100,
      sheenY: yRatio * 100,
    });
  }, [enable3D]);

  const handleMouseLeave = useCallback(() => {
    setHoveredHouse(null);
    setTilt({ x: 0, y: 0, sheenX: 50, sheenY: 50 });
  }, []);

  // -------------------------------------------------------------
  // SOUTH INDIAN FIXED-ZODIAC CHART (SQUARE PERIMETER)
  // -------------------------------------------------------------
  if (style === 'south') {
    const boxSize = 135;
    const padding = 10;
    const totalW = boxSize * 4 + padding * 2;
    const totalH = boxSize * 4 + padding * 2;

    return (
      <div className="relative w-full max-w-[560px] mx-auto select-none">
        {/* Controls Ribbon */}
        <div className="flex items-center justify-between mb-2 px-1">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-[#7A1612]">
            <Orbit className="w-3.5 h-3.5 text-[#C5A059]" />
            <span className="font-serif">दक्षिण भारतीय पद्धती</span>
          </div>
          <button
            type="button"
            onClick={() => setEnable3D(!enable3D)}
            className={`inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold rounded-lg border transition-all cursor-pointer ${
              enable3D
                ? 'bg-[#7A1612] text-[#FAF6F0] border-[#7A1612]'
                : 'bg-white text-[#24120B] border-[#C5A059]/40 hover:bg-[#FAF6F0]'
            }`}
          >
            <Sparkles className="w-3 h-3 text-[#C5A059]" />
            <span>{enable3D ? '3D Active' : 'Enable 3D'}</span>
          </button>
        </div>

        <div
          ref={containerRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          style={{
            transform: enable3D
              ? `perspective(1000px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale3d(1.01, 1.01, 1.01)`
              : 'none',
            transition: 'transform 0.15s ease-out',
            transformStyle: 'preserve-3d',
          }}
          className="relative transition-transform duration-100 ease-out"
        >
          <svg
            viewBox={`0 0 ${totalW} ${totalH}`}
            className="w-full h-auto drop-shadow-md rounded-xl transition-all"
          >
            <rect
              x={padding}
              y={padding}
              width={boxSize * 4}
              height={boxSize * 4}
              fill="#FDF5E6"
              stroke="#821C17"
              strokeWidth="2.5"
              rx="8"
            />
            <rect
              x={padding + boxSize}
              y={padding + boxSize}
              width={boxSize * 2}
              height={boxSize * 2}
              fill="#FCEBD2"
              stroke="#C46B1E"
              strokeWidth="1.5"
              rx="4"
            />
            <text
              x={totalW / 2}
              y={totalH / 2 - 12}
              textAnchor="middle"
              fill="#821C17"
              className="font-serif font-bold text-base tracking-widest"
            >
              {varga.toUpperCase()} — {varga === 'd1' ? 'RASHI' : 'NAVAMSHA'}
            </text>
            <text
              x={totalW / 2}
              y={totalH / 2 + 12}
              textAnchor="middle"
              fill="#C46B1E"
              className="text-xs font-mono tracking-wider uppercase"
            >
              SOUTH INDIAN STYLE
            </text>

            {SOUTH_SIGN_LAYOUT.map((item) => {
              const bx = padding + item.col * boxSize;
              const by = padding + item.row * boxSize;
              const isLagna = item.signNum === lagnaRashiNum;
              const houseNum = ((item.signNum - lagnaRashiNum + 12) % 12) + 1;
              const rawPlanets = housesData[houseNum] || [];
              const displayPlanets = rawPlanets.filter((p) => p !== 'Lagna');
              const isSelected = selectedHouse === houseNum || hoveredHouse === houseNum;

              return (
                <g
                  key={item.signNum}
                  onClick={() => onSelectHouse?.(houseNum)}
                  onMouseEnter={() => setHoveredHouse(houseNum)}
                  className="cursor-pointer group"
                >
                  <rect
                    x={bx}
                    y={by}
                    width={boxSize}
                    height={boxSize}
                    fill={
                      isSelected
                        ? 'rgba(228, 157, 75, 0.35)'
                        : isLagna
                        ? 'rgba(252, 235, 210, 0.45)'
                        : 'transparent'
                    }
                    stroke="#C46B1E"
                    strokeWidth="1.2"
                    className="transition-colors group-hover:fill-[#F9DAB5]/40"
                  />
                  <text
                    x={bx + 8}
                    y={by + 18}
                    fill={isLagna ? '#7A1612' : '#C46B1E'}
                    className="text-xs font-bold font-serif"
                  >
                    {item.signKey}
                  </text>
                  <text
                    x={bx + boxSize - 8}
                    y={by + 18}
                    textAnchor="end"
                    fill={isLagna ? '#7A1612' : '#C5A059'}
                    className="text-[10px] font-normal font-mono"
                  >
                    {isLagna ? 'LAGNA' : `H${houseNum}`}
                  </text>
                  <g transform={`translate(${bx + 10}, ${by + 36})`} stroke="none" strokeWidth="0">
                    {displayPlanets.map((planetName, pIdx) => {
                      const isRetro = retroSet.has(planetName);
                      const planetInfo = PLANET_NAMES_MAP[planetName];
                      const label = planetInfo?.short || planetName.slice(0, 2);

                      return (
                        <text
                          key={planetName}
                          x={0}
                          y={pIdx * 18}
                          className="text-xs font-normal font-serif"
                          stroke="none"
                          strokeWidth="0"
                          fill={planetName === 'Sun' || planetName === 'Mars' ? '#7A1612' : '#24120B'}
                        >
                          {label} {isRetro ? '℞' : ''}
                        </text>
                      );
                    })}
                  </g>
                </g>
              );
            })}
          </svg>
        </div>
      </div>
    );
  }

  // ---------------------------------------------------------------
  // NORTH INDIAN DIAMOND KUNDALI WITH 3D TILT & DRISHTI RAYCASTING
  // ---------------------------------------------------------------
  const focusedCoords = activeFocusHouse ? NORTH_HOUSE_COORDS[NORTH_HOUSE_TO_POS[activeFocusHouse]] : null;

  return (
    <div className="relative w-full max-w-[580px] mx-auto select-none space-y-2">
      {/* 3D Interactivity Header Control */}
      <div className="flex items-center justify-between px-1 text-xs">
        <div className="flex items-center gap-2 text-[#7A1612]">
          <Orbit className="w-3.5 h-3.5 text-[#C5A059]" />
          <span className="font-serif font-bold tracking-wide">
            {varga.toUpperCase()} {varga === 'd1' ? 'जन्म पत्रिका (Lagna Kundali)' : 'नवमांश पत्रिका (Navamsha)'}
          </span>
          {activeAspects.length > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-[#7A1612]/10 border border-[#7A1612]/20 text-[10px] text-[#7A1612] font-semibold flex items-center gap-1">
              <Eye className="w-2.5 h-2.5" />
              <span>{activeAspects.length} Drishti Rays Active</span>
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setEnable3D(!enable3D)}
            className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-[11px] font-semibold rounded-lg border transition-all cursor-pointer ${
              enable3D
                ? 'bg-[#7A1612] text-[#FAF6F0] border-[#7A1612] shadow-xs'
                : 'bg-white text-[#24120B] border-[#C5A059]/40 hover:bg-[#FAF6F0]'
            }`}
            title="Toggle 3D Astrolabe View"
          >
            <Sparkles className="w-3 h-3 text-[#F5E1BE]" />
            <span>{enable3D ? '3D Astrolabe ON' : 'Flat 2D'}</span>
          </button>
        </div>
      </div>

      {/* Main 3D Tilt Viewport */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{
          transform: enable3D
            ? `perspective(1200px) rotateX(${tilt.x}deg) rotateY(${tilt.y}deg) scale3d(1.015, 1.015, 1.015)`
            : 'none',
          transition: 'transform 0.12s ease-out',
          transformStyle: 'preserve-3d',
        }}
        className="relative rounded-2xl p-1 bg-gradient-to-br from-[#FAF6F0] via-[#FAF6F0] to-[#EADBC8] shadow-lg border border-[#C5A059]/40 transition-shadow hover:shadow-xl"
      >
        {/* Dynamic Specular Sheen Overlay */}
        {enable3D && (
          <div
            className="absolute inset-0 pointer-events-none rounded-2xl z-20 mix-blend-soft-light transition-opacity duration-300"
            style={{
              background: `radial-gradient(circle at ${tilt.sheenX}% ${tilt.sheenY}%, rgba(255,255,255,0.6) 0%, transparent 65%)`,
            }}
          />
        )}

        <svg
          viewBox="0 0 600 420"
          className="w-full h-auto rounded-xl select-none"
        >
          <defs>
            {/* 24K Gold Ray Beam Gradient */}
            <linearGradient id="goldDrishtiGrad" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#7A1612" stopOpacity="0.9" />
              <stop offset="50%" stopColor="#C5A059" stopOpacity="1" />
              <stop offset="100%" stopColor="#A85A1E" stopOpacity="0.8" />
            </linearGradient>

            <filter id="drishtiGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="2.5" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Outer Background Card */}
          <rect
            x="10"
            y="10"
            width="580"
            height="400"
            fill="#FDF5E6"
            stroke="#7A1612"
            strokeWidth="2.5"
            rx="12"
          />

          {/* Diagonal Geometric Structural Lines */}
          <line x1="10" y1="10" x2="590" y2="410" stroke="#E49D4B" strokeWidth="1.2" opacity="0.75" />
          <line x1="590" y1="10" x2="10" y2="410" stroke="#E49D4B" strokeWidth="1.2" opacity="0.75" />

          {/* Inner Diamond Points */}
          <polygon
            points="300,10 590,210 300,410 10,210"
            fill="none"
            stroke="#7A1612"
            strokeWidth="1.8"
          />

          {/* Inner Central Square Framing */}
          <line x1="155" y1="110" x2="445" y2="110" stroke="#E49D4B" strokeWidth="1" opacity="0.6" />
          <line x1="445" y1="110" x2="445" y2="310" stroke="#E49D4B" strokeWidth="1" opacity="0.6" />
          <line x1="445" y1="310" x2="155" y2="310" stroke="#E49D4B" strokeWidth="1" opacity="0.6" />
          <line x1="155" y1="310" x2="155" y2="110" stroke="#E49D4B" strokeWidth="1" opacity="0.6" />

          {/* Render Each Visual House Slot */}
          {Object.entries(NORTH_POSITION_MAP).map(([posKey, houseNum]) => {
            const pos = parseInt(posKey, 10);
            const coords = NORTH_HOUSE_COORDS[pos];
            if (!coords) return null;

            const rashiNum = ((lagnaRashiNum + houseNum - 2) % 12) + 1;
            const isLagnaHouse = houseNum === 1;
            const isSelected = selectedHouse === houseNum;
            const isHovered = hoveredHouse === houseNum;
            const isAspected = activeAspects.some(a => a.targetHouse === houseNum);
            const rawPlanets = housesData[houseNum] || [];
            const planetsInHouse = rawPlanets.filter((p) => p !== 'Lagna');

            return (
              <g
                key={pos}
                className="cursor-pointer group"
                onClick={() => onSelectHouse?.(houseNum)}
                onMouseEnter={() => setHoveredHouse(houseNum)}
              >
                {/* House Background Polygon on Hover/Selection/Aspect */}
                {coords.polygon && (
                  <polygon
                    points={coords.polygon}
                    fill={
                      isSelected || isHovered
                        ? 'rgba(228, 157, 75, 0.40)'
                        : isAspected
                        ? 'rgba(122, 22, 18, 0.15)'
                        : isLagnaHouse
                        ? 'rgba(252, 235, 210, 0.50)'
                        : 'transparent'
                    }
                    className="transition-colors duration-200 group-hover:fill-[#F9DAB5]/50"
                  />
                )}

                {/* Rashi Number in House */}
                <text
                  x={coords.nx}
                  y={coords.ny}
                  textAnchor="middle"
                  stroke="none"
                  strokeWidth="0"
                  className={`font-mono text-xs font-normal transition-transform duration-200 ${
                    isLagnaHouse ? 'fill-[#7A1612] font-bold' : isAspected ? 'fill-[#7A1612]' : 'fill-[#C5A059]'
                  }`}
                >
                  {rashiNum}
                </text>

                {/* Lagna Marker Badge */}
                {isLagnaHouse && (
                  <text
                    x={coords.px}
                    y={coords.py - 22}
                    textAnchor="middle"
                    stroke="none"
                    strokeWidth="0"
                    className="font-serif font-bold text-[12px] fill-[#7A1612] tracking-wider"
                  >
                    LAGNA
                  </text>
                )}

                {/* Occupant Planets in House */}
                {planetsInHouse.length > 0 && (
                  <g stroke="none" strokeWidth="0">
                    {planetsInHouse.map((p, idx) => {
                      const isRetro = retroSet.has(p);
                      const planetInfo = PLANET_NAMES_MAP[p];
                      const label = planetInfo?.short || p.slice(0, 2);
                      const isSpecial = ['Sun', 'Jupiter', 'Mars'].includes(p);

                      const lineHeight = 16;
                      const totalH = (planetsInHouse.length - 1) * lineHeight;
                      const yPos = coords.py - totalH / 2 + idx * lineHeight + (isLagnaHouse ? 10 : 0);

                      return (
                        <text
                          key={p}
                          x={coords.px}
                          y={yPos}
                          textAnchor="middle"
                          stroke="none"
                          strokeWidth="0"
                          className={`text-[12px] font-medium font-serif tracking-wide transition-all ${
                            isSpecial ? 'fill-[#7A1612] font-bold' : 'fill-[#24120B]'
                          }`}
                        >
                          {label}
                          {isRetro && (
                            <tspan className="text-[10px] font-sans fill-[#C5A059]">
                              {' '}℞
                            </tspan>
                          )}
                        </text>
                      );
                    })}
                  </g>
                )}
              </g>
            );
          })}

          {/* ── LIVE DRISHTI ASPECT RAYCASTING BEAMS ── */}
          {focusedCoords && activeAspects.length > 0 && (
            <g className="pointer-events-none" filter="url(#drishtiGlow)">
              {activeAspects.map((aspect) => {
                const targetPos = NORTH_HOUSE_TO_POS[aspect.targetHouse];
                const targetCoords = NORTH_HOUSE_COORDS[targetPos];
                if (!targetCoords) return null;

                // Curved bezier path connecting source house to aspected target
                const midX = (focusedCoords.px + targetCoords.px) / 2;
                const midY = (focusedCoords.py + targetCoords.py) / 2 - 15;

                return (
                  <g key={aspect.targetHouse}>
                    {/* Glowing Energy Laser Arc */}
                    <path
                      d={`M ${focusedCoords.px} ${focusedCoords.py} Q ${midX} ${midY} ${targetCoords.px} ${targetCoords.py}`}
                      fill="none"
                      stroke="url(#goldDrishtiGrad)"
                      strokeWidth="2.5"
                      strokeDasharray="6,4"
                      className="animate-pulse"
                    />

                    {/* Target House Impact Ring */}
                    <circle
                      cx={targetCoords.px}
                      cy={targetCoords.py}
                      r="14"
                      fill="none"
                      stroke="#C5A059"
                      strokeWidth="1.5"
                      strokeDasharray="3,2"
                      className="animate-spin"
                      style={{ transformOrigin: `${targetCoords.px}px ${targetCoords.py}px` }}
                    />
                  </g>
                );
              })}
            </g>
          )}
        </svg>

        {/* ── ACTIVE HOUSE INSPECTOR BADGE ── */}
        {activeFocusHouse && (
          <div className="mt-2 p-2.5 rounded-xl bg-white/95 border border-[#C5A059]/40 backdrop-blur-md shadow-sm flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-full bg-[#7A1612] text-[#FAF6F0] flex items-center justify-center font-serif font-bold text-xs">
                H{activeFocusHouse}
              </span>
              <div>
                <span className="font-serif font-bold text-[#24120B] block">
                  {activeFocusHouse === 1 ? 'लग्न भाव (Ascendant / Soul)' : `भाव ${activeFocusHouse} (House ${activeFocusHouse})`}
                </span>
                <span className="text-[11px] text-[#24120B]/60">
                  Planets: {(housesData[activeFocusHouse] || []).filter(p => p !== 'Lagna').join(', ') || 'None (Empty House)'}
                </span>
              </div>
            </div>

            {activeAspects.length > 0 && (
              <div className="text-right">
                <span className="text-[10px] text-[#A85A1E] font-semibold uppercase tracking-wider block">
                  Vedic Drishti
                </span>
                <span className="text-[11px] text-[#7A1612] font-medium">
                  Aspects H{activeAspects.map(a => a.targetHouse).join(', H')}
                </span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
