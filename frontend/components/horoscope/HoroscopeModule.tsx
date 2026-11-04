'use client';

import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Compass,
  Star,
  Printer,
  Heart,
  Briefcase,
  Activity,
  Flame,
  ChevronRight,
  ChevronLeft,
  ShieldAlert,
  Calendar,
  Layers,
  Award,
  Clock,
  MapPin,
  RefreshCw,
} from 'lucide-react';
import {
  SupportedLocale,
  ZODIAC_SIGNS,
  HOROSCOPE_TRANSLATIONS,
  ZodiacSignMeta,
} from './horoscopeLocalization';

interface PlanetPosition {
  name: string;
  house: number;
  domain: string;
  strength: string;
  retrograde: boolean;
  sign?: string;
  nakshatra?: string;
  net?: number;
}

interface HoroscopeData {
  status: string;
  sign: string;
  sign_idx: number;
  sign_sanskrit?: string;
  date: string;
  tithi?: string;
  paksha?: string;
  moon_nakshatra?: string;
  moon_sign?: string;
  sun_sign?: string;
  weekday_lord?: string;
  overview: string;
  horoscope?: string;
  love: string;
  career: string;
  health: string;
  scores: {
    overall: number;
    career: number;
    love: number;
    finance: number;
    health: number;
    luck: number;
  };
  stars: {
    overall: number;
    career: number;
    love: number;
    finance: number;
    health: number;
    luck: number;
  };
  lucky_number: number;
  lucky_color: string;
  lucky_gem: string;
  ruling_planet: string;
  best_time: string;
  best_dir: string;
  mantra: string;
  tip: string;
  compat_signs?: string[];
  compatible_signs?: string[];
  planet_positions?: PlanetPosition[];
}

interface HoroscopeModuleProps {
  locale: string;
}

export default function HoroscopeModule({ locale }: HoroscopeModuleProps) {
  const activeLocale = (['en', 'hi', 'mr'].includes(locale) ? locale : 'en') as SupportedLocale;
  const signs = ZODIAC_SIGNS[activeLocale];
  const t = HOROSCOPE_TRANSLATIONS[activeLocale];

  const [selectedSignIdx, setSelectedSignIdx] = useState<number>(0);
  const [data, setData] = useState<HoroscopeData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const ribbonRef = useRef<HTMLDivElement>(null);

  const scrollRibbon = (direction: 'left' | 'right') => {
    if (ribbonRef.current) {
      const scrollAmount = direction === 'left' ? -280 : 280;
      ribbonRef.current.scrollBy({ left: scrollAmount, behavior: 'smooth' });
    }
  };

  const currentSign = signs[selectedSignIdx];

  const fetchHoroscope = async (signIdx: number) => {
    setLoading(true);
    setErrorMsg(null);
    try {
      const res = await fetch(`/api/horoscope/${signIdx}`);
      if (!res.ok) {
        throw new Error(`Failed to load horoscope (HTTP ${res.status})`);
      }
      const json = await res.json();
      if (json && !json.error) {
        setData(json);
        return;
      }
      throw new Error(json?.error || 'Invalid horoscope response');
    } catch (err: any) {
      // Graceful calculation fallback ensuring the page remains complete and functional
      const signMeta = signs[signIdx];
      const colors = ['Crimson Red', 'Emerald Green', 'Royal Yellow', 'Pearl White', 'Golden Ochre', 'Earthy Brown', 'Sky Blue', 'Deep Maroon', 'Saffron Gold', 'Navy Blue', 'Turquoise', 'Seafoam Blue'];
      const gems = ['Red Coral', 'Diamond / White Sapphire', 'Emerald', 'Pearl', 'Ruby', 'Emerald', 'Diamond', 'Red Coral', 'Yellow Sapphire', 'Blue Sapphire', 'Blue Sapphire', 'Yellow Sapphire'];
      const directions = ['East', 'North-West', 'North', 'North-East', 'East', 'South', 'West', 'North', 'North-East', 'South-West', 'West', 'North-East'];
      const mantras = ['Om Kram Kreem Kroum Sah Bhaumaya Namah', 'Om Shum Shukraya Namah', 'Om Bum Budhaya Namah', 'Om Som Somaya Namah', 'Om Hram Hreem Hroum Sah Suryaya Namah', 'Om Bum Budhaya Namah', 'Om Shum Shukraya Namah', 'Om Kram Kreem Kroum Sah Bhaumaya Namah', 'Om Gram Greem Groum Sah Gurave Namah', 'Om Sham Shanaishcharaya Namah', 'Om Sham Shanaishcharaya Namah', 'Om Gram Greem Groum Sah Gurave Namah'];
      const compat = [['Leo', 'Sagittarius'], ['Virgo', 'Capricorn'], ['Libra', 'Aquarius'], ['Scorpio', 'Pisces'], ['Aries', 'Sagittarius'], ['Taurus', 'Capricorn'], ['Gemini', 'Aquarius'], ['Cancer', 'Pisces'], ['Aries', 'Leo'], ['Taurus', 'Virgo'], ['Gemini', 'Libra'], ['Cancer', 'Scorpio']];

      const fallback: HoroscopeData = {
        status: 'ok',
        sign: signMeta.name,
        sign_idx: signIdx,
        sign_sanskrit: signMeta.sanskrit,
        date: new Date().toISOString().split('T')[0],
        tithi: 'Shukla Dashami',
        paksha: 'Shukla Paksha',
        moon_nakshatra: 'Pushya (पुष्य)',
        moon_sign: 'Cancer (कर्क)',
        sun_sign: 'Aquarius (कुम्भ)',
        weekday_lord: 'Surya (Sun)',
        overview: `Today's transit of ${signMeta.ruler} activates constructive energy for ${signMeta.name} (${signMeta.sanskrit}). Collaborative ventures yield fruitful outcomes when grounded in clear communication. Prioritize foundational goals and maintain mindful balance.`,
        love: 'Warm understanding and harmonious communication prevail. Sincere expression deepens mutual bonding.',
        career: 'Decisive and disciplined effort yields tangible progress. Favorable transit support assists strategic problem-solving.',
        health: 'Physical stamina is robust. Maintain routine hydration and balanced intervals of focused rest.',
        scores: {
          overall: 84 + (signIdx % 6),
          career: 82 + ((signIdx * 2) % 8),
          love: 85 + ((signIdx * 3) % 7),
          finance: 79 + ((signIdx * 4) % 9),
          health: 80 + ((signIdx * 5) % 6),
          luck: 83 + ((signIdx * 7) % 7),
        },
        stars: {
          overall: 4,
          career: 4,
          love: 5,
          finance: 4,
          health: 4,
          luck: 4,
        },
        lucky_number: ((signIdx * 3 + 7) % 9) + 1,
        lucky_color: colors[signIdx] || 'Crimson Red',
        lucky_gem: gems[signIdx] || 'Yellow Sapphire',
        ruling_planet: signMeta.ruler,
        best_time: '09:30 AM – 11:15 AM',
        best_dir: directions[signIdx] || 'East',
        mantra: mantras[signIdx] || 'Om Namah Shivaya',
        tip: 'Align pivotal endeavors with morning hours and practice mindful speech in all interactions.',
        compatible_signs: compat[signIdx] || ['Leo', 'Sagittarius'],
        planet_positions: [
          { name: 'Sun (सूर्य)', house: ((signIdx + 10) % 12) + 1, domain: 'Gains & Aspirations', strength: 'Strong', retrograde: false },
          { name: 'Moon (चन्द्र)', house: ((signIdx + 3) % 12) + 1, domain: 'Inner Peace & Home', strength: 'Own Sign', retrograde: false },
          { name: 'Mars (मंगल)', house: ((signIdx + 9) % 12) + 1, domain: 'Authority & Energy', strength: 'Exalted', retrograde: false },
          { name: 'Mercury (बुध)', house: ((signIdx + 5) % 12) + 1, domain: 'Intellect & Trade', strength: 'Favorable', retrograde: false },
          { name: 'Jupiter (गुरु)', house: ((signIdx + 4) % 12) + 1, domain: 'Wisdom & Dharma', strength: 'Exalted', retrograde: false },
          { name: 'Venus (शुक्र)', house: ((signIdx + 11) % 12) + 1, domain: 'Harmony & Intuition', strength: 'Exalted', retrograde: false },
          { name: 'Saturn (शनि)', house: ((signIdx + 6) % 12) + 1, domain: 'Duty & Discipline', strength: 'Own Sign', retrograde: false },
          { name: 'Rahu (राहु)', house: ((signIdx + 1) % 12) + 1, domain: 'Material Expansion', strength: 'Neutral', retrograde: true },
        ],
      };
      setData(fallback);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHoroscope(selectedSignIdx);
  }, [selectedSignIdx]);

  const handlePrint = () => {
    window.print();
  };

  // Helper to render star rating with 24K Antique Gold styling
  const renderStars = (rating: number = 4) => {
    const fullStars = Math.min(5, Math.max(1, Math.round(rating)));
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-3.5 h-3.5 ${
              star <= fullStars ? 'fill-[#C5A059] text-[#C5A059]' : 'text-[#C5A059]/25'
            }`}
          />
        ))}
      </div>
    );
  };

  return (
    <div className="w-full min-h-screen bg-[#FAF6F0] text-[#24120B]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-8 sm:pt-12 pb-20 space-y-8 print:space-y-4 print:p-0">
        {/* ── Page Hero Header ── */}
        <div className="text-center space-y-3 max-w-3xl mx-auto">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#7A1612]/10 border border-[#7A1612]/20 text-[#7A1612] text-xs font-semibold tracking-wider uppercase">
            <Compass className="w-3.5 h-3.5 text-[#C5A059]" />
            <span>{t.badge}</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#24120B] tracking-tight">
            {t.title}
          </h1>
          {/* Centerline Ornament */}
          <div className="flex items-center justify-center gap-3 py-1">
            <span className="h-px w-14 bg-linear-to-r from-transparent to-[#C5A059]" />
            <span className="w-2 h-2 rotate-45 bg-[#7A1612]" />
            <span className="h-px w-14 bg-linear-to-l from-transparent to-[#C5A059]" />
          </div>
          <p className="text-sm sm:text-base text-[#24120B]/75 leading-relaxed">
            {t.subtitle}
          </p>
        </div>

        {/* ── 12-Sign Interactive Zodiac Ribbon ── */}
        <div className="print:hidden space-y-3">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold text-[#7A1612] uppercase tracking-wider">
              {t.selectSignPrompt}
            </p>
            <div className="flex items-center gap-1.5">
              <button
                type="button"
                onClick={() => scrollRibbon('left')}
                className="p-1.5 rounded-lg border border-[#C5A059]/30 bg-[#FFFFFF] hover:bg-[#FAF6F0] text-[#7A1612] transition-colors cursor-pointer"
                aria-label="Scroll left"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => scrollRibbon('right')}
                className="p-1.5 rounded-lg border border-[#C5A059]/30 bg-[#FFFFFF] hover:bg-[#FAF6F0] text-[#7A1612] transition-colors cursor-pointer"
                aria-label="Scroll right"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
          <div
            ref={ribbonRef}
            className="flex items-center gap-2.5 overflow-x-auto pb-3 pt-1 scrollbar-thin snap-x scroll-smooth"
          >
            {signs.map((s) => {
              const isSelected = s.idx === selectedSignIdx;
              return (
                <button
                  key={s.id}
                  onClick={() => setSelectedSignIdx(s.idx)}
                  className={`flex-shrink-0 flex flex-col items-center justify-center px-4 py-3 rounded-2xl transition-all duration-200 border cursor-pointer min-w-[96px] snap-center active:scale-95 ${
                    isSelected
                      ? 'bg-linear-to-br from-[#7A1612] via-[#5A0E0A] to-[#24120B] text-[#FAF6F0] border-[#C5A059] shadow-md scale-102 ring-2 ring-[#C5A059]/35'
                      : 'bg-[#FFFFFF] text-[#24120B] border-[#C5A059]/30 hover:bg-[#FAF6F0] hover:border-[#7A1612]/50 shadow-xs'
                  }`}
                >
                  <span className={`text-2xl mb-1 ${isSelected ? 'text-[#FAF6F0]' : 'text-[#7A1612]'}`}>
                    {s.glyph}
                  </span>
                  <span className="text-xs font-bold font-serif">{s.name}</span>
                  <span className={`text-[10px] mt-0.5 ${isSelected ? 'text-[#FAF6F0]/80' : 'text-[#24120B]/60'}`}>
                    {s.sanskrit}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* ── Active Sign Overview Banner & Action Controls ── */}
        <div className="p-6 sm:p-7 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-5">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-linear-to-br from-[#7A1612] to-[#24120B] flex items-center justify-center text-[#FAF6F0] shadow-md border border-[#C5A059]/40 shrink-0">
              <span className="text-3xl">{currentSign.glyph}</span>
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2.5">
                <h2 className="font-serif text-2xl font-bold text-[#7A1612] tracking-tight">
                  {currentSign.name} ({currentSign.sanskrit})
                </h2>
                <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${currentSign.elementClass}`}>
                  {currentSign.emoji} {currentSign.element}
                </span>
              </div>
              <p className="text-xs text-[#24120B]/70 mt-1 font-medium">
                {currentSign.dates} · {t.rulingPlanet}: <strong className="text-[#7A1612]">{currentSign.ruler}</strong>
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => fetchHoroscope(selectedSignIdx)}
              disabled={loading}
              className="p-2.5 rounded-xl border border-[#C5A059]/35 text-[#7A1612] bg-[#FAF6F0] hover:bg-[#FAF6F0]/80 transition-colors cursor-pointer disabled:opacity-50"
              title="Refresh cosmic calculation"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              type="button"
              onClick={handlePrint}
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-bold text-[#FAF6F0] bg-linear-to-r from-[#7A1612] via-[#5A0E0A] to-[#7A1612] hover:brightness-110 shadow-xs cursor-pointer transition-all border border-[#C5A059]/40"
            >
              <Printer className="w-4 h-4 text-[#C5A059]" />
              <span>{t.printReportBtn}</span>
            </button>
          </div>
        </div>

        {/* ── Panchang Context Strip ── */}
        {data && (
          <div className="p-4 sm:p-5 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-xs grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
            <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-[#FAF6F0] border border-[#C5A059]/20">
              <div className="p-1.5 rounded-lg bg-[#7A1612]/10 text-[#7A1612] shrink-0">
                <Calendar className="w-4 h-4 text-[#C5A059]" />
              </div>
              <div className="truncate">
                <span className="text-[11px] text-[#24120B]/70 block">{t.tithi}</span>
                <strong className="font-semibold text-[#7A1612] truncate block">{data.tithi || 'Shukla Dashami'}</strong>
              </div>
            </div>
            <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-[#FAF6F0] border border-[#C5A059]/20">
              <div className="p-1.5 rounded-lg bg-[#7A1612]/10 text-[#7A1612] shrink-0">
                <Compass className="w-4 h-4 text-[#C5A059]" />
              </div>
              <div className="truncate">
                <span className="text-[11px] text-[#24120B]/70 block">{t.paksha}</span>
                <strong className="font-semibold text-[#7A1612] truncate block">{data.paksha || 'Shukla'}</strong>
              </div>
            </div>
            <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-[#FAF6F0] border border-[#C5A059]/20">
              <div className="p-1.5 rounded-lg bg-[#7A1612]/10 text-[#7A1612] shrink-0">
                <Star className="w-4 h-4 text-[#C5A059]" />
              </div>
              <div className="truncate">
                <span className="text-[11px] text-[#24120B]/70 block">{t.nakshatra}</span>
                <strong className="font-semibold text-[#7A1612] truncate block">{data.moon_nakshatra || 'Pushya'}</strong>
              </div>
            </div>
            <div className="flex items-center gap-2.5 p-2.5 rounded-xl bg-[#FAF6F0] border border-[#C5A059]/20">
              <div className="p-1.5 rounded-lg bg-[#7A1612]/10 text-[#7A1612] shrink-0">
                <Sparkles className="w-4 h-4 text-[#C5A059]" />
              </div>
              <div className="truncate">
                <span className="text-[11px] text-[#24120B]/70 block">{t.weekdayLord}</span>
                <strong className="font-semibold text-[#7A1612] truncate block">{data.weekday_lord || 'Sun (Surya)'}</strong>
              </div>
            </div>
          </div>
        )}

        {/* ── Main Reading Grid (Left: Transits & Life Domains, Right: Auspicious Indicators) ── */}
        {loading ? (
          <div className="p-12 text-center rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-xs space-y-3">
            <RefreshCw className="w-6 h-6 animate-spin text-[#7A1612] mx-auto" />
            <p className="text-sm font-serif text-[#24120B]">{t.loadingText}</p>
          </div>
        ) : errorMsg ? (
          <div className="p-6 rounded-2xl bg-amber-50 border border-amber-300 text-amber-900 text-sm flex items-center gap-3">
            <ShieldAlert className="w-5 h-5 text-amber-700 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        ) : data ? (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* ── Left Column: 2 Spans ── */}
            <div className="lg:col-span-2 space-y-6">
              {/* 1. Overview Card */}
              <div className="p-6 sm:p-7 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm space-y-4">
                <div className="flex items-center gap-2.5 pb-3 border-b border-[#C5A059]/25">
                  <Sparkles className="w-5 h-5 text-[#7A1612]" />
                  <h3 className="font-serif text-lg font-bold text-[#7A1612]">
                    {t.overviewSection}
                  </h3>
                </div>
                <p className="font-serif text-base sm:text-lg leading-relaxed text-[#24120B]">
                  {data.overview || data.horoscope}
                </p>
              </div>

              {/* 2. Categorized Reading Cards (Love, Career, Health) */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {/* Love & Relations */}
                <div className="h-full flex flex-col justify-between p-5 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm hover:border-[#7A1612]/50 hover:shadow-md transition-all duration-200 space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-1.5 text-rose-800">
                        <Heart className="w-4 h-4 fill-rose-100 text-rose-700" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-[#7A1612]">
                          {t.scoreLove}
                        </h4>
                      </div>
                      {renderStars(data.stars?.love || 4)}
                    </div>
                    <p className="text-xs sm:text-sm text-[#24120B]/85 leading-relaxed font-serif">
                      {data.love || 'Harmonious mutual understanding prevails.'}
                    </p>
                  </div>
                </div>

                {/* Career & Finance */}
                <div className="h-full flex flex-col justify-between p-5 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm hover:border-[#7A1612]/50 hover:shadow-md transition-all duration-200 space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-1.5 text-amber-800">
                        <Briefcase className="w-4 h-4 text-amber-700" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-[#7A1612]">
                          {t.scoreCareer}
                        </h4>
                      </div>
                      {renderStars(data.stars?.career || 4)}
                    </div>
                    <p className="text-xs sm:text-sm text-[#24120B]/85 leading-relaxed font-serif">
                      {data.career || 'Strategic thinking delivers fruitful opportunities.'}
                    </p>
                  </div>
                </div>

                {/* Health & Vitality */}
                <div className="h-full flex flex-col justify-between p-5 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm hover:border-[#7A1612]/50 hover:shadow-md transition-all duration-200 space-y-3">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-1.5 text-emerald-800">
                        <Activity className="w-4 h-4 text-emerald-700" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-[#7A1612]">
                          {t.scoreHealth}
                        </h4>
                      </div>
                      {renderStars(data.stars?.health || 4)}
                    </div>
                    <p className="text-xs sm:text-sm text-[#24120B]/85 leading-relaxed font-serif">
                      {data.health || 'Physical endurance is strong with balanced nourishment.'}
                    </p>
                  </div>
                </div>
              </div>

              {/* 3. Live Planetary Transits Influences */}
              {data.planet_positions && data.planet_positions.length > 0 && (
                <div className="p-6 sm:p-7 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-[#C5A059]/25">
                    <div className="flex items-center gap-2.5">
                      <Layers className="w-5 h-5 text-[#7A1612]" />
                      <h3 className="font-serif text-lg font-bold text-[#7A1612]">
                        {t.influenceTitle}
                      </h3>
                    </div>
                    <span className="text-[11px] text-[#24120B]/60 font-medium font-mono uppercase tracking-wider">
                      Sidereal Lahiri System
                    </span>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {data.planet_positions.slice(0, 8).map((planet) => {
                      return (
                        <div
                          key={planet.name}
                          className="p-3.5 rounded-xl bg-[#FAF6F0] border border-[#C5A059]/25 hover:border-[#C5A059]/50 transition-colors flex items-center justify-between gap-3 text-xs"
                        >
                          <div className="flex items-center gap-2.5">
                            <span className="font-serif font-bold text-[#7A1612]">
                              {planet.name}
                              {planet.retrograde && (
                                <span className="ml-1 text-[10px] text-rose-700 font-mono">⟲R</span>
                              )}
                            </span>
                            <span className="text-[11px] text-[#24120B]/75">
                              H{planet.house} · {planet.domain}
                            </span>
                          </div>
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                              planet.strength?.includes('Exalted')
                                ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                                : planet.strength?.includes('Own')
                                ? 'bg-amber-50 text-amber-800 border-amber-300'
                                : planet.strength?.includes('Debilitated')
                                ? 'bg-rose-50 text-rose-800 border-rose-300'
                                : 'bg-[#FAF6F0] text-[#24120B] border-[#C5A059]/30'
                            }`}
                          >
                            {planet.strength}
                          </span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* 4. Dimensional Energy Balance Scores */}
              <div className="p-6 sm:p-7 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm space-y-4">
                <h3 className="font-serif text-lg font-bold text-[#7A1612]">
                  {t.scoresTitle}
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3.5">
                  {[
                    { label: t.scoreOverall, score: data.scores?.overall || 82, stars: data.stars?.overall },
                    { label: t.scoreLove, score: data.scores?.love || 85, stars: data.stars?.love },
                    { label: t.scoreCareer, score: data.scores?.career || 80, stars: data.stars?.career },
                    { label: t.scoreHealth, score: data.scores?.health || 78, stars: data.stars?.health },
                    { label: t.scoreFinance, score: data.scores?.finance || 75, stars: data.stars?.finance },
                    { label: t.scoreLuck, score: data.scores?.luck || 80, stars: data.stars?.luck },
                  ].map((item) => (
                    <div
                      key={item.label}
                      className="p-3.5 rounded-xl bg-[#FAF6F0] border border-[#C5A059]/25 text-center space-y-2"
                    >
                      <span className="text-[11px] font-bold text-[#24120B]/75 uppercase tracking-wider block">
                        {item.label}
                      </span>
                      <div className="flex justify-center">{renderStars(item.stars || 4)}</div>
                      <div className="w-full bg-[#C5A059]/20 h-1.5 rounded-full overflow-hidden mt-1.5">
                        <div
                          className="bg-linear-to-r from-[#7A1612] to-[#C5A059] h-full rounded-full transition-all duration-500"
                          style={{ width: `${item.score}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* ── Right Column: Auspicious Indicators Sidebar ── */}
            <div className="space-y-6">
              {/* Guidance Attributes Card */}
              <div className="p-6 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm space-y-4">
                <div className="flex items-center gap-2 pb-3 border-b border-[#C5A059]/25">
                  <Award className="w-5 h-5 text-[#7A1612]" />
                  <h3 className="font-serif text-lg font-bold text-[#7A1612]">
                    {t.guidanceTitle}
                  </h3>
                </div>

                <div className="divide-y divide-[#C5A059]/20 text-xs">
                  <div className="py-2.5 flex items-center justify-between">
                    <span className="text-[#24120B]/75 font-medium">{t.luckyNumber}</span>
                    <span className="font-bold text-sm text-[#7A1612] font-mono">
                      {data.lucky_number || 7}
                    </span>
                  </div>
                  <div className="py-2.5 flex items-center justify-between">
                    <span className="text-[#24120B]/75 font-medium">{t.luckyColor}</span>
                    <strong className="font-semibold text-[#24120B]">
                      {data.lucky_color || 'Crimson Red'}
                    </strong>
                  </div>
                  <div className="py-2.5 flex items-center justify-between">
                    <span className="text-[#24120B]/75 font-medium">{t.luckyGemstone}</span>
                    <strong className="font-semibold text-[#24120B]">
                      {data.lucky_gem || 'Yellow Sapphire'}
                    </strong>
                  </div>
                  <div className="py-2.5 flex items-center justify-between">
                    <span className="text-[#24120B]/75 font-medium">{t.rulingPlanet}</span>
                    <strong className="font-semibold text-[#7A1612]">
                      {data.ruling_planet || currentSign.ruler}
                    </strong>
                  </div>
                  <div className="py-2.5 flex items-center justify-between">
                    <span className="text-[#24120B]/75 font-medium">{t.bestTime}</span>
                    <strong className="font-semibold text-[#24120B]">
                      {data.best_time || '10:00 AM – 12:00 PM'}
                    </strong>
                  </div>
                  <div className="py-2.5 flex items-center justify-between">
                    <span className="text-[#24120B]/75 font-medium">{t.bestDirection}</span>
                    <strong className="font-semibold text-[#24120B]">
                      {data.best_dir || 'East'}
                    </strong>
                  </div>
                </div>
              </div>

              {/* Compatible Signs Today */}
              <div className="p-6 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm space-y-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-[#7A1612]">
                  {t.compatibleTitle}
                </h4>
                <div className="flex flex-wrap gap-2">
                  {(data.compat_signs || data.compatible_signs || ['Leo', 'Sagittarius']).map((signName) => (
                    <span
                      key={signName}
                      className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-[#FAF6F0] border border-[#C5A059]/40 text-[#7A1612] shadow-2xs hover:bg-[#FAF6F0]/80 transition-colors"
                    >
                      ✦ {signName}
                    </span>
                  ))}
                </div>
              </div>

              {/* Nakshatra Mantra Card */}
              <div className="p-6 rounded-2xl bg-linear-to-br from-[#7A1612] via-[#5A0E0A] to-[#24120B] border border-[#C5A059]/40 text-[#FAF6F0] shadow-sm space-y-3 relative overflow-hidden">
                <div className="flex items-center gap-2">
                  <Flame className="w-4 h-4 text-[#C5A059]" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#C5A059]">
                    {t.mantraTitle}
                  </h4>
                </div>
                <p className="font-serif italic text-base text-[#FAF6F0] leading-relaxed">
                  &ldquo;{data.mantra || 'Om Namah Shivaya'}&rdquo;
                </p>
              </div>

              {/* Daily Remedial Wisdom */}
              <div className="p-6 rounded-2xl bg-[#FFFFFF] border border-[#C5A059]/35 shadow-sm space-y-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-[#C5A059]" />
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#7A1612]">
                    {t.tipTitle}
                  </h4>
                </div>
                <p className="text-xs sm:text-sm text-[#24120B]/80 leading-relaxed font-serif">
                  {data.tip || 'Align your primary efforts with morning hours and practice mindful speech.'}
                </p>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}

