'use client';

import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { Sun, Moon, Sparkles, Clock, Compass } from 'lucide-react';

interface LocalHorizonDomeProps {
  sunrise?: string;
  sunset?: string;
  moonrise?: string;
  moonset?: string;
  city?: string;
  locale: string;
}

// Convert "06:34 AM" or "18:30" string to minutes from midnight
function parseTimeToMinutes(timeStr?: string): number {
  if (!timeStr) return 360; // Default 06:00
  const match = timeStr.match(/(\d{1,2}):(\d{2})\s*(AM|PM)?/i);
  if (!match) return 360;
  let hours = parseInt(match[1], 10);
  const minutes = parseInt(match[2], 10);
  const meridiem = match[3]?.toUpperCase();

  if (meridiem === 'PM' && hours < 12) hours += 12;
  if (meridiem === 'AM' && hours === 12) hours = 0;
  return hours * 60 + minutes;
}

export default function LocalHorizonDome({
  sunrise = '06:34 AM',
  sunset = '06:12 PM',
  moonrise = '02:15 PM',
  moonset = '03:10 AM',
  city = 'Pune',
  locale,
}: LocalHorizonDomeProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [interactiveMinutes, setInteractiveMinutes] = useState<number | null>(null);
  const [currentMinutes, setCurrentMinutes] = useState<number>(720); // 12:00 default
  const [isLiveTime, setIsLiveTime] = useState(true);
  const [tilt, setTilt] = useState<{ x: number; y: number }>({ x: 0, y: 0 });

  // Update real-time minutes
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      const mins = now.getHours() * 60 + now.getMinutes();
      setCurrentMinutes(mins);
    };
    updateTime();
    const interval = setInterval(updateTime, 60000);
    return () => clearInterval(interval);
  }, []);

  const activeMinutes = interactiveMinutes !== null ? interactiveMinutes : currentMinutes;

  const sunriseMins = useMemo(() => parseTimeToMinutes(sunrise), [sunrise]);
  const sunsetMins = useMemo(() => parseTimeToMinutes(sunset), [sunset]);
  const moonriseMins = useMemo(() => parseTimeToMinutes(moonrise), [moonrise]);
  const moonsetMins = useMemo(() => parseTimeToMinutes(moonset), [moonset]);

  // Compute solar progress along arc (0 = East horizon, 0.5 = Zenith, 1 = West horizon)
  const isDaytime = activeMinutes >= sunriseMins && activeMinutes <= sunsetMins;
  const solarFraction = useMemo(() => {
    if (activeMinutes < sunriseMins) {
      // Pre-dawn: beneath eastern horizon
      return -((sunriseMins - activeMinutes) / (24 * 60 - sunsetMins + sunriseMins));
    }
    if (activeMinutes > sunsetMins) {
      // Post-sunset: beneath western horizon
      return 1 + (activeMinutes - sunsetMins) / (24 * 60 - sunsetMins + sunriseMins);
    }
    return (activeMinutes - sunriseMins) / (sunsetMins - sunriseMins);
  }, [activeMinutes, sunriseMins, sunsetMins]);

  // Geometry: semi-circular dome
  const cx = 220;
  const cy = 160;
  const radius = 140;

  // Solar coordinates (East = left, West = right, zenith = top)
  const sunAngle = Math.PI - solarFraction * Math.PI; // PI at East, 0 at West
  const sunX = cx + radius * Math.cos(sunAngle);
  const sunY = cy - radius * Math.sin(sunAngle);

  // Dynamic sky lighting gradient based on sun altitude
  const skyGrad = useMemo(() => {
    if (solarFraction < -0.08 || solarFraction > 1.08) {
      // Deep Night / Ratri
      return {
        top: '#1A0C06',
        bottom: '#2E150C',
        ambient: 'rgba(217, 119, 6, 0.05)',
      };
    }
    if (solarFraction < 0.05 || solarFraction > 0.95) {
      // Dawn/Dusk Twilight (Sandhya / Brahma Muhurta)
      return {
        top: '#3E100A',
        bottom: '#A43E1B',
        ambient: 'rgba(234, 88, 12, 0.25)',
      };
    }
    if (solarFraction < 0.2 || solarFraction > 0.8) {
      // Golden Hour
      return {
        top: '#791412',
        bottom: '#DC9955',
        ambient: 'rgba(245, 158, 11, 0.3)',
      };
    }
    // Midday Solar Zenith
    return {
      top: '#791412',
      bottom: '#FAF3E7',
      ambient: 'rgba(239, 199, 146, 0.5)',
    };
  }, [solarFraction]);

  // Mouse Parallax 3D Tilt
  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLDivElement>) => {
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const px = (x / rect.width) * 2 - 1;
    const py = (y / rect.height) * 2 - 1;
    setTilt({ x: -py * 7, y: px * 7 });
  }, []);

  const handleMouseLeave = useCallback(() => {
    setTilt({ x: 0, y: 0 });
  }, []);

  // Format active time (HH:MM AM/PM)
  const formattedTime = useMemo(() => {
    const h = Math.floor(activeMinutes / 60);
    const m = activeMinutes % 60;
    const period = h >= 12 ? 'PM' : 'AM';
    const displayH = h % 12 === 0 ? 12 : h % 12;
    const displayM = m.toString().padStart(2, '0');
    return `${displayH}:${displayM} ${period}`;
  }, [activeMinutes]);

  return (
    <div className="w-full bg-[#FAF3E7] border border-[#F9DAB5] rounded-3xl p-5 shadow-xs mb-6 overflow-hidden">
      {/* ── TOP HEADER ── */}
      <div className="flex flex-wrap items-center justify-between pb-3 border-b border-[#F9DAB5] gap-3">
        <div className="flex items-center gap-2">
          <Compass className="w-4 h-4 text-[#821C17] animate-spin-slow" />
          <h4 className="font-serif text-sm font-bold text-[#821C17]">
            {locale === 'mr'
              ? 'स्थानिक क्षितिज खगोलीय घुमट'
              : locale === 'hi'
              ? 'स्थानीय क्षितिज खगोलीय गुंबद'
              : 'Local Horizon Sky Dome & Solar Arc'}
          </h4>
          <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#FCEBD2] text-[#821C17] font-semibold border border-[#F9DAB5]">
            {city}
          </span>
        </div>

        {/* Live / Scrubber Toggle */}
        <div className="flex items-center gap-2">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#FCEBD2] border border-[#F9DAB5] text-xs font-mono font-bold text-[#821C17]">
            <Clock className="w-3.5 h-3.5 text-[#C46B1E]" />
            <span>{formattedTime}</span>
            {isLiveTime && (
              <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse ml-0.5" title="Live Clock" />
            )}
          </div>
          <button
            type="button"
            onClick={() => {
              setIsLiveTime(!isLiveTime);
              if (!isLiveTime) setInteractiveMinutes(null);
            }}
            className={`px-2.5 py-1 rounded-full text-xs font-semibold transition-all shadow-2xs cursor-pointer ${
              isLiveTime
                ? 'bg-[#821C17] text-[#FDF5E6]'
                : 'bg-[#FCEBD2] text-[#421A10] border border-[#F9DAB5]'
            }`}
          >
            {isLiveTime ? 'Live Sync' : 'Scrubbing'}
          </button>
        </div>
      </div>

      {/* ── 3D HEMISPHERICAL SKY DOME ── */}
      <div
        ref={containerRef}
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        style={{ perspective: '800px' }}
        className="relative w-full aspect-[22/11] max-h-[260px] my-4 flex items-center justify-center select-none"
      >
        <div
          style={{
            transform: `rotateX(${tilt.x}deg) rotateY(${tilt.y}deg)`,
            transformStyle: 'preserve-3d',
            transition: 'transform 0.15s ease-out',
          }}
          className="w-full h-full relative flex items-center justify-center"
        >
          <svg viewBox="0 0 440 200" className="w-full h-full overflow-visible">
            <defs>
              {/* Dynamic Celestial Sky Dome Radial Gradient */}
              <radialGradient id="skyAtmosphere" cx="50%" cy="100%" r="90%">
                <stop offset="0%" stopColor={skyGrad.bottom} stopOpacity="0.85" />
                <stop offset="60%" stopColor={skyGrad.top} stopOpacity="0.75" />
                <stop offset="100%" stopColor="#1A0C06" stopOpacity="0.9" />
              </radialGradient>

              {/* Sun Volumetric Glow */}
              <radialGradient id="sunGlowGrad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stopColor="#FFF7ED" stopOpacity="1" />
                <stop offset="35%" stopColor="#F59E0B" stopOpacity="0.8" />
                <stop offset="70%" stopColor="#D97706" stopOpacity="0.4" />
                <stop offset="100%" stopColor="#D97706" stopOpacity="0" />
              </radialGradient>
            </defs>

            {/* Sky Dome Hemisphere Mask & Fill */}
            <path
              d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy} Z`}
              fill="url(#skyAtmosphere)"
              stroke="#E8D5B9"
              strokeWidth="1.5"
            />

            {/* Zenith Vertical Meridian Line */}
            <line
              x1={cx}
              y1={cy - radius}
              x2={cx}
              y2={cy}
              stroke="#FAF3E7"
              strokeWidth="0.8"
              strokeDasharray="2 3"
              strokeOpacity="0.35"
            />
            <text
              x={cx}
              y={cy - radius - 6}
              textAnchor="middle"
              fill="#C46B1E"
              fontSize="8"
              fontFamily="sans-serif"
              fontWeight="bold"
            >
              {locale === 'mr' ? 'शिरोबिंदु (Zenith)' : locale === 'hi' ? 'खमध्य (Zenith)' : 'Zenith'}
            </text>

            {/* Daytime Solar Arc (Golden Dotted Trajectory) */}
            <path
              d={`M ${cx - radius} ${cy} A ${radius} ${radius} 0 0 1 ${cx + radius} ${cy}`}
              fill="none"
              stroke="#F59E0B"
              strokeWidth="2.2"
              strokeDasharray="4 4"
              strokeOpacity="0.65"
            />

            {/* Horizon Baseline */}
            <line
              x1={cx - radius - 25}
              y1={cy}
              x2={cx + radius + 25}
              y2={cy}
              stroke="#791412"
              strokeWidth="2"
            />

            {/* Cardinal Horizon Markers */}
            <g transform={`translate(${cx - radius}, ${cy + 15})`}>
              <text textAnchor="middle" fill="#791412" fontSize="9" fontWeight="bold">
                {locale === 'mr' ? 'पूर्व (East)' : locale === 'hi' ? 'पूर्व (East)' : 'East'}
              </text>
              <text textAnchor="middle" y="10" fill="#421A10" fontSize="7" opacity="0.7">
                {sunrise}
              </text>
            </g>

            <g transform={`translate(${cx + radius}, ${cy + 15})`}>
              <text textAnchor="middle" fill="#791412" fontSize="9" fontWeight="bold">
                {locale === 'mr' ? 'पश्चिम (West)' : locale === 'hi' ? 'पश्चिम (West)' : 'West'}
              </text>
              <text textAnchor="middle" y="10" fill="#421A10" fontSize="7" opacity="0.7">
                {sunset}
              </text>
            </g>

            {/* Live Sun Celestial Body */}
            {isDaytime ? (
              <g transform={`translate(${sunX}, ${sunY})`}>
                {/* Outer Glow Halo */}
                <circle cx="0" cy="0" r="22" fill="url(#sunGlowGrad)" />
                {/* Sun Body with Specular Highlight */}
                <circle
                  cx="0"
                  cy="0"
                  r="7.5"
                  fill="#F59E0B"
                  stroke="#FFFFFF"
                  strokeWidth="1.5"
                  className="shadow-md"
                />
                <circle cx="-2" cy="-2" r="2.5" fill="#FFFFFF" opacity="0.8" />
                {/* Sun Tag */}
                <text
                  x="0"
                  y="-12"
                  textAnchor="middle"
                  fill="#FFF7ED"
                  fontSize="8"
                  fontWeight="bold"
                  className="drop-shadow-xs"
                >
                  ☉ Surya
                </text>
              </g>
            ) : (
              /* Night Indicator: Moon visible above horizon */
              <g transform={`translate(${cx}, ${cy - radius * 0.65})`}>
                <circle cx="0" cy="0" r="16" fill="rgba(247, 235, 215, 0.15)" />
                <circle cx="0" cy="0" r="7" fill="#FDF5E6" stroke="#C46B1E" strokeWidth="1" />
                <path d="M 0 -7 A 7 7 0 0 1 0 7 A 4 7 0 0 0 0 -7 Z" fill="#791412" opacity="0.4" />
                <text
                  x="0"
                  y="-11"
                  textAnchor="middle"
                  fill="#FAF3E7"
                  fontSize="8"
                  fontWeight="bold"
                >
                  ☽ Chandra
                </text>
              </g>
            )}

            {/* Central Ground Observation Station */}
            <circle cx={cx} cy={cy} r="5" fill="#791412" stroke="#FAF3E7" strokeWidth="1.5" />
          </svg>
        </div>
      </div>

      {/* ── TIME SCRUBBER SLIDER ── */}
      <div className="flex items-center gap-3 pt-2">
        <label htmlFor="horizon-solar-scrubber" className="sr-only">
          {locale === 'mr' ? 'खगोलीय सौर स्क्रबर' : 'Celestial solar scrubber along local horizon'}
        </label>
        <Sun className="w-4 h-4 text-[#F59E0B] shrink-0" />
        <input
          id="horizon-solar-scrubber"
          aria-label="Celestial solar scrubber along local horizon"
          type="range"
          min="0"
          max="1439"
          value={activeMinutes}
          onChange={(e) => {
            setIsLiveTime(false);
            setInteractiveMinutes(parseInt(e.target.value, 10));
          }}
          className="w-full accent-[#821C17] cursor-pointer h-1.5 bg-[#F9DAB5] rounded-lg"
        />
        <Moon className="w-4 h-4 text-[#791412] shrink-0" />
      </div>
    </div>
  );
}
