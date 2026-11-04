'use client';

import React from 'react';
import { RASHI_NAMES_MAP, PLANET_NAMES_MAP } from './kundaliLocalization';

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
  const lagnaRashiInfo = RASHI_NAMES_MAP[lagnaSign] || { num: 1 };
  const lagnaRashiNum = lagnaRashiInfo.num;

  // Build a fast lookup for planet retrograde status
  const retroSet = new Set(
    planets.filter((p) => p.retrograde).map((p) => p.name)
  );

  if (style === 'south') {
    // -------------------------------------------------------------
    // SOUTH INDIAN FIXED-ZODIAC CHART (SQUARE PERIMETER)
    // -------------------------------------------------------------
    const boxSize = 135;
    const padding = 10;
    const totalW = boxSize * 4 + padding * 2;
    const totalH = boxSize * 4 + padding * 2;

    return (
      <div className="relative w-full max-w-[560px] mx-auto select-none">
        <svg
          viewBox={`0 0 ${totalW} ${totalH}`}
          className="w-full h-auto drop-shadow-sm transition-all"
        >
          {/* Outer Border & Parchment Fill */}
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

          {/* Central Sacred Altar (Empty Middle Square) */}
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

          {/* Render 12 Zodiac Boxes */}
          {SOUTH_SIGN_LAYOUT.map((item) => {
            const bx = padding + item.col * boxSize;
            const by = padding + item.row * boxSize;
            const isLagna = item.signNum === lagnaRashiNum;

            // Calculate astrological house from Lagna
            const houseNum = ((item.signNum - lagnaRashiNum + 12) % 12) + 1;
            const isSelected = selectedHouse === houseNum;
            const rawPlanets = housesData[houseNum] || [];
            const displayPlanets = rawPlanets.filter((p) => p !== 'Lagna');

            return (
              <g
                key={item.signNum}
                className="cursor-pointer transition-colors"
                onClick={() => onSelectHouse?.(houseNum)}
              >
                {/* Cell Border & Background */}
                <rect
                  x={bx}
                  y={by}
                  width={boxSize}
                  height={boxSize}
                  fill={isSelected ? '#F9DAB5' : isLagna ? '#FCEBD2' : '#FDF5E6'}
                  stroke="#E49D4B"
                  strokeWidth={isSelected ? '2' : '1'}
                  className="hover:fill-[#F9DAB5]/60 transition-colors"
                />

                {/* Lagna Diagonal Stripe Accent */}
                {isLagna && (
                  <line
                    x1={bx}
                    y1={by}
                    x2={bx + boxSize}
                    y2={by + boxSize}
                    stroke="#821C17"
                    strokeWidth="1.2"
                    strokeDasharray="4 3"
                    opacity="0.4"
                  />
                )}

                {/* Sign Label (Top-Left) */}
                <text
                  x={bx + 8}
                  y={by + 18}
                  fill="#7A1612"
                  stroke="none"
                  strokeWidth="0"
                  className="text-[11px] font-normal tracking-wider font-mono"
                >
                  {item.signNum}. {item.signKey.slice(0, 3).toUpperCase()}
                </text>

                {/* House Num Indicator (Top-Right) */}
                <text
                  x={bx + boxSize - 8}
                  y={by + 18}
                  textAnchor="end"
                  fill="#C5A059"
                  stroke="none"
                  strokeWidth="0"
                  className="text-[10px] font-normal font-mono"
                >
                  {isLagna ? 'LAGNA' : `H${houseNum}`}
                </text>

                {/* Planets Inside this Sign */}
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
    );
  }

  // ---------------------------------------------------------------
  // NORTH INDIAN DIAMOND KUNDALI (CENTRAL LAGNA DIAMOND)
  // ---------------------------------------------------------------
  return (
    <div className="relative w-full max-w-[560px] mx-auto select-none">
      <svg
        viewBox="0 0 600 420"
        className="w-full h-auto drop-shadow-md rounded-xl transition-all"
      >
        {/* Outer Background Card */}
        <rect
          x="10"
          y="10"
          width="580"
          height="400"
          fill="#FDF5E6"
          stroke="#821C17"
          strokeWidth="2.5"
          rx="12"
        />

        {/* Diagonal Geometric Structural Lines */}
        <line x1="10" y1="10" x2="590" y2="410" stroke="#E49D4B" strokeWidth="1.2" opacity="0.75" />
        <line x1="590" y1="10" x2="10" y2="410" stroke="#E49D4B" strokeWidth="1.2" opacity="0.75" />

        {/* Inner Diamond Points: (300,10) - (590,210) - (300,410) - (10,210) */}
        <polygon
          points="300,10 590,210 300,410 10,210"
          fill="none"
          stroke="#821C17"
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

          // Rashi number in this house (1..12) based on Lagna Rashi
          const rashiNum = ((lagnaRashiNum + houseNum - 2) % 12) + 1;
          const isLagnaHouse = houseNum === 1;
          const isSelected = selectedHouse === houseNum;
          const rawPlanets = housesData[houseNum] || [];
          const planetsInHouse = rawPlanets.filter((p) => p !== 'Lagna');

          return (
            <g
              key={pos}
              className="cursor-pointer group"
              onClick={() => onSelectHouse?.(houseNum)}
            >
              {/* Optional House Background Polygon on Hover/Selection */}
              {coords.polygon && (
                <polygon
                  points={coords.polygon}
                  fill={
                    isSelected
                      ? 'rgba(228, 157, 75, 0.35)'
                      : isLagnaHouse
                      ? 'rgba(252, 235, 210, 0.45)'
                      : 'transparent'
                  }
                  className="transition-colors group-hover:fill-[#F9DAB5]/40"
                />
              )}

              {/* Rashi Number in House */}
              <text
                x={coords.nx}
                y={coords.ny}
                textAnchor="middle"
                stroke="none"
                strokeWidth="0"
                className={`font-mono text-xs font-normal ${
                  isLagnaHouse ? 'fill-[#7A1612]' : 'fill-[#C5A059]'
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
                  className="font-serif font-normal text-[12px] fill-[#7A1612] tracking-wider"
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

                    // Vertical layout with staggered centering
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
                        className={`text-[12px] font-normal font-serif tracking-wide ${
                          isSpecial ? 'fill-[#7A1612]' : 'fill-[#24120B]'
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
      </svg>
    </div>
  );
}

