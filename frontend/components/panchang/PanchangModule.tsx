'use client';

import { useState, useEffect, useMemo, useCallback } from 'react';
import { useLocale } from 'next-intl';
import {
  Sun,
  Moon,
  Sunrise,
  Sunset,
  Clock,
  Calendar as CalendarIcon,
  MapPin,
  Sparkles,
  CheckCircle2,
  Share2,
  RefreshCw,
  Compass,
  ShieldAlert,
  Download,
  Info,
} from 'lucide-react';
import {
  PANCHANG_UI_TEXT,
  CITIES_LOCALIZED,
  WEEKDAY_DEITIES_LOCALIZED,
  formatLocalizedDate,
  localizeTithi,
  localizePaksha,
  localizeNakshatra,
  localizeYoga,
  localizeKarana,
  localizeVara,
  localizeSamvat,
  localizeDishaShool,
  localizeChoghadiyaItem,
  localizePlanetName,
  localizeRashiName,
  localizeFestivalItem,
} from './panchangLocalization';
import { openPrintablePanchangReport } from './panchangReportGenerator';

interface PanchangData {
  city?: string;
  date?: string;
  samvat?: string | {
    vikram_samvat?: number | string;
    shaka_samvat?: number | string;
    month_amanta?: string;
    [key: string]: any;
  };
  weekday_idx?: number;
  tithi?: string;
  tithi_name?: string;
  tithi_end?: string;
  tithi_progress?: number | string;
  paksha?: string;
  nakshatra?: string;
  nakshatra_end?: string;
  nakshatra_pada?: number;
  yoga?: string;
  yoga_name?: string;
  yoga_end?: string;
  karana?: string;
  karana_name?: string;
  karana_end?: string;
  sunrise?: string;
  sunset?: string;
  moonrise?: string;
  moonset?: string;
  abhijit?: string;
  abhijit_muhurta?: string;
  brahma?: string;
  rahu?: string;
  rahu_kaal?: string;
  yamaganda?: string;
  gulika?: string;
  gulika_kaal?: string;
  disha_shool?: string | {
    direction?: string;
    sanskrit?: string;
    remedy?: string;
    avoid_msg?: string;
    [key: string]: any;
  };
  choghadiya_day?: {
    name: string;
    label: string;
    is_auspicious: boolean;
    ruling_planet?: string;
    start: string;
    end: string;
  }[];
  choghadiya_night?: {
    name: string;
    label: string;
    is_auspicious: boolean;
    ruling_planet?: string;
    start: string;
    end: string;
  }[];
  current_choghadiya?: {
    name: string;
    label: string;
    is_auspicious: boolean;
    ruling_planet?: string;
    start: string;
    end: string;
    time_remaining_str?: string;
  };
  horas?: {
    hour_number: number;
    planet: string;
    start: string;
    end: string;
  }[];
  current_hora?: {
    hour_number: number;
    planet: string;
    start: string;
    end: string;
  };
  planets?: {
    name: string;
    sign: string;
    degree: string;
    nakshatra: string;
    retrograde: boolean;
  }[];
  [key: string]: any;
}

interface FestivalItem {
  name: string;
  date: string;
  iso_date?: string;
  desc: string;
  tithi: string;
  paksha: string;
  nakshatra: string;
  tag: string;
  icon: string;
  remedies?: string;
  is_today?: boolean;
}

const CITIES = [
  'Pune',
  'Mumbai',
  'New Delhi',
  'Varanasi',
  'Bengaluru',
  'Chennai',
  'Kolkata',
  'Hyderabad',
  'Ahmedabad',
  'Jaipur',
  'Ujjain',
  'Haridwar',
];

export default function PanchangModule() {
  const rawLocale = useLocale();
  const locale = (rawLocale === 'mr' || rawLocale === 'hi' ? rawLocale : 'en') as 'mr' | 'hi' | 'en';
  const ui = PANCHANG_UI_TEXT[locale] || PANCHANG_UI_TEXT.en;

  const [selectedCity, setSelectedCity] = useState('Pune');
  const [selectedDate, setSelectedDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  });

  const [currentTime, setCurrentTime] = useState('');
  const [panchang, setPanchang] = useState<PanchangData | null>(null);
  const [festivals, setFestivals] = useState<FestivalItem[]>([]);
  const [, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [, setApiStatus] = useState<'live' | 'offline' | 'loading'>('loading');
  const [activeTab, setActiveTab] = useState<'planets' | 'choghadiya' | 'horas' | 'festivals'>('planets');
  const [festivalFilter, setFestivalFilter] = useState<string>('all');
  const [copied, setCopied] = useState(false);

  // Live real-time IST clock
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setCurrentTime(
        now.toLocaleTimeString(locale === 'mr' ? 'mr-IN' : locale === 'hi' ? 'hi-IN' : 'en-IN', {
          timeZone: 'Asia/Kolkata',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: true,
        })
      );
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, [locale]);

  // Fetch Panchang Data
  const fetchPanchang = useCallback(async (city: string, date: string, isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);

    try {
      const res = await fetch('/api/panchang', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ city, date }),
      });

      if (!res.ok) throw new Error('API error');
      const json = await res.json();

      if (json.status === 'live' && json.data) {
        setPanchang(json.data);
        setApiStatus('live');
      } else {
        // Fallback default structure
        setPanchang({
          city,
          date,
          samvat: 'Vikram Samvat 2083 · Ananda',
          vara: 'शनिवार (Shani-vara)',
          tithi: 'शुक्ल दशमी (Shukla Dashami)',
          paksha: 'Shukla',
          tithi_progress: 68,
          nakshatra: 'रोहिणी (Rohini)',
          nakshatra_pada: 3,
          yoga: 'शुक्ल (Shukla)',
          karana: 'तैतिल (Taitila)',
          sunrise: '06:34 AM',
          sunset: '05:42 PM',
          moonrise: '02:15 PM',
          moonset: '03:10 AM',
          abhijit: '11:45 AM – 12:32 PM',
          brahma: '04:58 AM – 05:46 AM',
          rahu: '09:20 AM – 10:45 AM',
          yamaganda: '01:30 PM – 02:55 PM',
          gulika: '06:34 AM – 08:00 AM',
          disha_shool: 'East (Purva) — Chew ginger or mustard seeds before travel',
          planets: [
            { name: 'Surya (Sun)', sign: 'Tula (Libra)', degree: "15°22'", nakshatra: 'Swati', retrograde: false },
            { name: 'Chandra (Moon)', sign: 'Vrishabha (Taurus)', degree: "12°04'", nakshatra: 'Rohini', retrograde: false },
            { name: 'Mangala (Mars)', sign: 'Karka (Cancer)', degree: "04°18'", nakshatra: 'Pushya', retrograde: false },
            { name: 'Budha (Mercury)', sign: 'Tula (Libra)', degree: "28°45'", nakshatra: 'Vishakha', retrograde: false },
            { name: 'Guru (Jupiter)', sign: 'Mithuna (Gemini)', degree: "20°12'", nakshatra: 'Punarvasu', retrograde: true },
            { name: 'Shukra (Venus)', sign: 'Vrishchika (Scorpio)', degree: "18°30'", nakshatra: 'Jyeshtha', retrograde: false },
            { name: 'Shani (Saturn)', sign: 'Kumbha (Aquarius)', degree: "18°50'", nakshatra: 'Shatabhisha', retrograde: true },
            { name: 'Rahu (North Node)', sign: 'Kumbha (Aquarius)', degree: "10°14'", nakshatra: 'Shatabhisha', retrograde: true },
            { name: 'Ketu (South Node)', sign: 'Simha (Leo)', degree: "10°14'", nakshatra: 'Magha', retrograde: true },
          ],
        });
        setApiStatus('offline');
      }
    } catch {
      setApiStatus('offline');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  // Fetch Festivals
  const fetchFestivals = useCallback(async () => {
    try {
      const res = await fetch('/api/festivals/upcoming?limit=14');
      if (res.ok) {
        const json = await res.json();
        setFestivals(json.festivals || []);
      }
    } catch {
      // Handled silently
    }
  }, []);

  useEffect(() => {
    fetchPanchang(selectedCity, selectedDate);
    fetchFestivals();
  }, [fetchPanchang, fetchFestivals, selectedCity, selectedDate]);

  // Moon Emoji computation
  const moonPhaseEmoji = useMemo(() => {
    const prog = typeof panchang?.tithi_progress === 'number' ? panchang.tithi_progress : 50;
    if (prog < 7) return '🌑';
    if (prog < 25) return '🌒';
    if (prog < 45) return '🌓';
    if (prog < 55) return '🌔';
    if (prog < 75) return '🌕';
    if (prog < 85) return '🌖';
    if (prog < 95) return '🌗';
    return '🌘';
  }, [panchang?.tithi_progress]);

  // Ruling deity calculation
  const dayIndex = useMemo(() => {
    const d = new Date(selectedDate);
    return isNaN(d.getDay()) ? 0 : d.getDay();
  }, [selectedDate]);

  const rulingDeity = useMemo(() => {
    return WEEKDAY_DEITIES_LOCALIZED[dayIndex]?.[locale] || 'Surya Dev';
  }, [dayIndex, locale]);

  // Safely format Samvat (may be string or object from backend)
  const samvatString = useMemo(() => {
    return localizeSamvat(panchang?.samvat, locale);
  }, [panchang?.samvat, locale]);

  // Safely format Disha Shool (may be string or object from backend)
  const dishaShoolString = useMemo(() => {
    return localizeDishaShool(panchang?.disha_shool, locale);
  }, [panchang?.disha_shool, locale]);

  // Localized upcoming festivals
  const localizedFestivals = useMemo(() => {
    return festivals.map((f) => localizeFestivalItem(f, locale));
  }, [festivals, locale]);

  // Filtered upcoming festivals
  const filteredFestivals = useMemo(() => {
    if (festivalFilter === 'all') return localizedFestivals;
    return localizedFestivals.filter((f) => f.tag === festivalFilter);
  }, [localizedFestivals, festivalFilter]);

  // Today's prominent festival banner
  const todaysFestivals = useMemo(() => {
    return localizedFestivals.filter((f) => f.is_today);
  }, [localizedFestivals]);

  const handleShare = async () => {
    const locCity = CITIES_LOCALIZED[selectedCity]?.[locale] || selectedCity;
    const formattedDate = formatLocalizedDate(selectedDate, locale);
    const locTithi = localizeTithi(panchang?.tithi, panchang?.paksha, locale);
    const locNak = localizeNakshatra(panchang?.nakshatra, locale);
    const locYoga = localizeYoga(panchang?.yoga, locale);
    const locKarana = localizeKarana(panchang?.karana, locale);
    const locVara = localizeVara(panchang?.vara, panchang?.weekday_idx ?? (new Date(selectedDate).getDay()), locale);
    const abhijit = panchang?.abhijit || panchang?.abhijit_muhurta || '11:42 AM – 12:28 PM';
    const rahu = panchang?.rahu || panchang?.rahu_kaal || '03:05 PM – 04:32 PM';

    const brandedText = `✦ ASTROLOGIC · VEDIC PANCHANG ✦
📅 ${formattedDate}
📍 ${locCity} (18.52° N, 73.86° E)

✧ 5 COSMIC LIMBS (पञ्चाङ्ग) ✧
• Tithi: ${locTithi}
• Nakshatra: ${locNak}
• Yoga: ${locYoga}
• Karana: ${locKarana}
• Vara: ${locVara}

✧ SOLAR & LUNAR TIMINGS ✧
• Sunrise: ${panchang?.sunrise || '06:34 AM'} | Sunset: ${panchang?.sunset || '05:58 PM'}
• Moonrise: ${panchang?.moonrise || '07:15 AM'} | Moonset: ${panchang?.moonset || '06:40 PM'}

✧ AUSPICIOUS & CAUTION MUHURATS ✧
• Abhijit Muhurat: ${abhijit} (Auspicious)
• Rahu Kaal: ${rahu} (Inauspicious)

Explore live Panchang & Birth Chart:
https://astrologic.com/panchang`;

    if (typeof navigator !== 'undefined' && navigator.share) {
      try {
        await navigator.share({
          title: `AstroLogic Vedic Panchang - ${locCity} (${selectedDate})`,
          text: brandedText,
          url: window.location.href,
        });
        return;
      } catch {
        // Fallback to clipboard
      }
    }

    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(brandedText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    }
  };

  const handleDownloadPanchang = () => {
    openPrintablePanchangReport({
      date: formatLocalizedDate(selectedDate, locale),
      city: CITIES_LOCALIZED[selectedCity]?.[locale] || selectedCity,
      panchang,
      locale: (['en', 'hi', 'mr'].includes(locale) ? locale : 'en') as any,
    });
  };

  return (
    <div className="w-full bg-[#FDF5E6] text-[#421A10] min-h-screen pt-8 pb-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        
        {/* ========================================================= */}
        {/* TOP BREADCRUMB & INTRO                                    */}
        {/* ========================================================= */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#F9DAB5] pb-6">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#821C17]/10 border border-[#821C17]/25 text-[#821C17] text-xs font-semibold tracking-wider uppercase">
              <Sparkles className="w-3.5 h-3.5 text-[#C46B1E]" />
              <span>{ui.eyebrow}</span>
            </div>
            <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#421A10] tracking-tight">
              {ui.title}
            </h1>
            <p className="text-sm sm:text-base text-[#421A10]/75 max-w-2xl">
              {ui.subtitle}
            </p>
          </div>

          {/* Action Tools */}
          <div className="flex items-center gap-2.5 self-start sm:self-center">
            <button
              type="button"
              onClick={handleShare}
              className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl bg-[#F5EFE6] hover:bg-[#EADBC8] border border-[#C5A059]/30 text-[#7A1612] transition-all cursor-pointer shadow-2xs"
              title="Share Branded Panchang Dossier"
            >
              <Share2 className="w-4 h-4 text-[#A85A1E]" />
              <span>{copied ? (locale === 'hi' ? 'कॉपी हो गया!' : locale === 'mr' ? 'कॉपी झाले!' : 'Copied!') : ui.share}</span>
            </button>

            <button
              type="button"
              onClick={handleDownloadPanchang}
              className="inline-flex items-center gap-2 px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl bg-linear-to-r from-[#7A1612] to-[#A85A1E] hover:brightness-105 border border-[#C5A059]/40 text-[#FAF6F0] transition-all shadow-xs cursor-pointer"
              title="Download Complete Vedic Panchang Dossier (PDF)"
            >
              <Download className="w-4 h-4 text-[#F5E1BE]" />
              <span>{locale === 'hi' ? 'पंचांग डाउनलोड करें (PDF)' : locale === 'mr' ? 'पंचांग डाउनलोड करा (PDF)' : 'Download Panchang (PDF)'}</span>
            </button>
          </div>
        </div>

        {/* ========================================================= */}
        {/* TODAY'S FESTIVAL BANNER (IF APPLICABLE)                   */}
        {/* ========================================================= */}
        {todaysFestivals.length > 0 && (
          <div className="space-y-3">
            {todaysFestivals.map((fest, idx) => (
              <div
                key={idx}
                className="bg-linear-to-r from-[#821C17]/10 via-[#FCEBD2] to-[#821C17]/10 border-2 border-[#821C17]/35 rounded-2xl p-5 sm:p-6 shadow-sm flex flex-col sm:flex-row items-start sm:items-center gap-5"
              >
                <div className="w-14 h-14 rounded-2xl bg-[#821C17] text-[#FDF5E6] flex items-center justify-center text-3xl shadow-md shrink-0">
                  {fest.icon || '🪔'}
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-serif text-xl sm:text-2xl font-bold text-[#821C17]">
                      {fest.name}
                    </span>
                    <span className="text-[10px] uppercase font-mono font-bold px-2 py-0.5 rounded-full bg-[#E49D4B]/20 border border-[#E49D4B]/35 text-[#821C17]">
                      {ui.todaysCelebration}
                    </span>
                  </div>
                  <p className="text-xs sm:text-sm text-[#421A10]/85 font-medium leading-relaxed">
                    {fest.desc}
                  </p>
                  {fest.remedies && (
                    <div className="pt-1.5 flex items-start gap-1.5 text-xs text-[#821C17] font-semibold">
                      <Sparkles className="w-3.5 h-3.5 text-[#C46B1E] shrink-0 mt-0.5" />
                      <span>{ui.sattvicKarma} {fest.remedies}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* ========================================================= */}
        {/* COSMIC DATE BANNER & CONTROLS BAR                         */}
        {/* ========================================================= */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Main Cosmic Date Display (8 Cols) */}
          <div className="lg:col-span-8 bg-linear-to-br from-[#FCEBD2] to-[#FDF5E6] border border-[#F9DAB5] rounded-3xl p-6 sm:p-8 shadow-sm relative overflow-hidden flex flex-col justify-between">
            {/* Background Sacred Geometric Halo */}
            <div className="absolute right-0 top-0 bottom-0 w-80 pointer-events-none opacity-25 flex items-center justify-center">
              <div className="w-72 h-72 rounded-full border border-[#821C17]/30 absolute" />
              <div className="w-52 h-52 rounded-full border border-[#E49D4B]/35 absolute" />
            </div>

            <div className="relative z-10 space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <span className="text-xs font-mono uppercase tracking-widest text-[#C46B1E] font-semibold flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5" />
                  <span>{ui.astronomicalCalendar}</span>
                </span>
                <span className="text-xs font-mono text-[#821C17] font-bold bg-[#821C17]/10 px-2.5 py-0.5 rounded-full border border-[#821C17]/20">
                  {samvatString}
                </span>
              </div>

              <div className="flex items-baseline gap-3">
                <h2 className="font-serif text-3xl sm:text-4xl font-bold text-[#421A10]">
                  {formatLocalizedDate(selectedDate, locale)}
                </h2>
              </div>

              <div className="text-xs sm:text-sm text-[#421A10]/80 flex flex-wrap items-center gap-x-4 gap-y-1">
                <span className="font-semibold text-[#821C17]">{rulingDeity}</span>
                <span>•</span>
                <span>{ui.locationLabel} <strong>{CITIES_LOCALIZED[selectedCity]?.[locale] || selectedCity}</strong></span>
                <span>•</span>
                <span>{ui.coordinatesLabel} <strong>18.5204° N, 73.8567° E</strong></span>
              </div>
            </div>

            {/* Bottom Row inside banner */}
            <div className="relative z-10 pt-6 mt-6 border-t border-[#F9DAB5] flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="text-4xl select-none" title={ui.lunarPhase}>
                  {moonPhaseEmoji}
                </div>
                <div>
                  <span className="text-[11px] font-mono uppercase text-[#C46B1E] block font-bold">
                    {ui.lunarPhase}
                  </span>
                  <span className="text-sm font-serif font-bold text-[#421A10]">
                    {localizeTithi(panchang?.tithi, panchang?.paksha, locale)} ({localizePaksha(panchang?.paksha, locale)} {locale === 'en' ? 'Paksha' : 'पक्ष'})
                  </span>
                </div>
              </div>

              <div className="text-right">
                <span className="text-[10px] font-mono uppercase text-[#C46B1E] block font-semibold">
                  {ui.realTimeIst}
                </span>
                <span className="font-mono text-xl sm:text-2xl font-bold text-[#821C17]">
                  {currentTime || '12:00:00 PM IST'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Selectors & Filters (4 Cols) */}
          <div className="lg:col-span-4 bg-[#FCEBD2]/60 border border-[#F9DAB5] rounded-3xl p-6 flex flex-col justify-between space-y-4 shadow-sm">
            <div>
              <h3 className="font-serif text-lg font-bold text-[#421A10] mb-3 flex items-center justify-between">
                <span>{ui.configureAlmanac}</span>
                {refreshing && <RefreshCw className="w-4 h-4 text-[#821C17] animate-spin" />}
              </h3>

              {/* City Selection */}
              <div className="space-y-1.5 mb-4">
                <label className="text-xs font-semibold text-[#421A10]/80 uppercase tracking-wider block">
                  {ui.selectLocation}
                </label>
                <div className="relative">
                  <select
                    value={selectedCity}
                    onChange={(e) => setSelectedCity(e.target.value)}
                    className="w-full appearance-none bg-[#FDF5E6] border border-[#F9DAB5] rounded-xl px-3.5 py-2.5 text-sm font-medium text-[#421A10] focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 cursor-pointer shadow-xs"
                  >
                    {CITIES.map((c) => (
                      <option key={c} value={c}>
                        {CITIES_LOCALIZED[c]?.[locale] || c}
                      </option>
                    ))}
                  </select>
                  <MapPin className="w-4 h-4 text-[#C46B1E] absolute right-3 top-3 pointer-events-none" />
                </div>
              </div>

              {/* Date Selection */}
              <div className="space-y-1.5">
                <label className="text-xs font-semibold text-[#421A10]/80 uppercase tracking-wider block">
                  {ui.selectDate}
                </label>
                <div className="relative">
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    className="w-full bg-[#FDF5E6] border border-[#F9DAB5] rounded-xl px-3.5 py-2.5 text-sm font-medium text-[#421A10] focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 shadow-xs cursor-pointer"
                  />
                  <CalendarIcon className="w-4 h-4 text-[#C46B1E] absolute right-3 top-3 pointer-events-none" />
                </div>
              </div>
            </div>

            {/* Quick Presets */}
            <div className="pt-2">
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => {
                    const today = new Date();
                    setSelectedDate(today.toISOString().split('T')[0]);
                  }}
                  className="px-2 py-1.5 text-xs font-semibold rounded-lg bg-[#FDF5E6] hover:bg-[#F9DAB5] border border-[#F9DAB5] text-[#821C17] transition-colors cursor-pointer"
                >
                  {ui.today}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    const tomorrow = new Date();
                    tomorrow.setDate(tomorrow.getDate() + 1);
                    setSelectedDate(tomorrow.toISOString().split('T')[0]);
                  }}
                  className="px-2 py-1.5 text-xs font-semibold rounded-lg bg-[#FDF5E6] hover:bg-[#F9DAB5] border border-[#F9DAB5] text-[#821C17] transition-colors cursor-pointer"
                >
                  {ui.tomorrow}
                </button>
                <button
                  type="button"
                  onClick={() => fetchPanchang(selectedCity, selectedDate, true)}
                  className="px-2 py-1.5 text-xs font-semibold rounded-lg bg-[#821C17] text-[#FDF5E6] hover:bg-[#60100E] border border-[#E49D4B]/40 transition-colors flex items-center justify-center gap-1 cursor-pointer"
                >
                  <RefreshCw className="w-3 h-3" />
                  <span>{ui.refresh}</span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================= */}
        {/* SUN & MOON TIMINGS (4 CARDS)                              */}
        {/* ========================================================= */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-[#FCEBD2] border border-[#F9DAB5] rounded-2xl p-5 shadow-xs relative overflow-hidden group hover:border-[#821C17] transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-[#C46B1E] font-semibold">
                🌅 {ui.sunrise}
              </span>
              <Sunrise className="w-4 h-4 text-[#821C17]" />
            </div>
            <div className="font-serif text-2xl font-bold text-[#821C17]">
              {panchang?.sunrise || '06:34 AM'}
            </div>
            <p className="text-[11px] text-[#421A10]/70 mt-1">
              {ui.sunriseSub}
            </p>
          </div>

          <div className="bg-[#FCEBD2] border border-[#F9DAB5] rounded-2xl p-5 shadow-xs relative overflow-hidden group hover:border-[#821C17] transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-[#C46B1E] font-semibold">
                🌇 {ui.sunset}
              </span>
              <Sunset className="w-4 h-4 text-[#C46B1E]" />
            </div>
            <div className="font-serif text-2xl font-bold text-[#821C17]">
              {panchang?.sunset || '05:42 PM'}
            </div>
            <p className="text-[11px] text-[#421A10]/70 mt-1">
              {ui.sunsetSub}
            </p>
          </div>

          <div className="bg-[#FDF5E6] border border-[#F9DAB5] rounded-2xl p-5 shadow-xs relative overflow-hidden group hover:border-[#821C17] transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-[#C46B1E] font-semibold">
                🌙 {ui.moonrise}
              </span>
              <Moon className="w-4 h-4 text-[#E49D4B]" />
            </div>
            <div className="font-serif text-2xl font-bold text-[#421A10]">
              {panchang?.moonrise || '02:15 PM'}
            </div>
            <p className="text-[11px] text-[#421A10]/70 mt-1">
              {ui.moonriseSub}
            </p>
          </div>

          <div className="bg-[#FDF5E6] border border-[#F9DAB5] rounded-2xl p-5 shadow-xs relative overflow-hidden group hover:border-[#821C17] transition-all">
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono uppercase tracking-wider text-[#C46B1E] font-semibold">
                🌚 {ui.moonset}
              </span>
              <Moon className="w-4 h-4 text-[#421A10]" />
            </div>
            <div className="font-serif text-2xl font-bold text-[#421A10]">
              {panchang?.moonset || '03:10 AM'}
            </div>
            <p className="text-[11px] text-[#421A10]/70 mt-1">
              {ui.moonsetSub}
            </p>
          </div>
        </div>

        {/* ========================================================= */}
        {/* PANCHA-ANGA: THE FIVE SACRED LIMBS                        */}
        {/* ========================================================= */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-[#F9DAB5] pb-2">
            <h3 className="font-serif text-xl sm:text-2xl font-bold text-[#421A10] flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-[#821C17]" />
              <span>{ui.panchaAngaTitle}</span>
            </h3>
            <span className="text-xs font-mono text-[#C46B1E]">
              {ui.suryaSiddhantaPrecision}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* 1. Tithi */}
            <div className="bg-[#FCEBD2]/70 border border-[#F9DAB5] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono uppercase text-[#C46B1E] font-bold block mb-1">
                  {ui.tithiLabel}
                </span>
                <h4 className="font-serif text-lg font-bold text-[#821C17]">
                  {localizeTithi(panchang?.tithi, panchang?.paksha, locale)}
                </h4>
                <p className="text-xs text-[#421A10]/75 mt-1">
                  {panchang?.tithi_end ? `${ui.endsAt} ${panchang.tithi_end}` : ui.activeDaylight}
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-[#F9DAB5]">
                <div className="flex justify-between text-[10px] text-[#421A10]/70 mb-1 font-mono">
                  <span>{ui.elongation}</span>
                  <span>{typeof panchang?.tithi_progress === 'number' ? Math.round(panchang.tithi_progress) : 65}%</span>
                </div>
                <div className="w-full h-1.5 bg-[#FDF5E6] rounded-full overflow-hidden border border-[#F9DAB5]">
                  <div
                    className="h-full bg-linear-to-r from-[#E49D4B] to-[#821C17] rounded-full"
                    style={{ width: `${typeof panchang?.tithi_progress === 'number' ? Math.min(panchang.tithi_progress, 100) : 65}%` }}
                  />
                </div>
              </div>
            </div>

            {/* 2. Nakshatra */}
            <div className="bg-[#FCEBD2]/70 border border-[#F9DAB5] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono uppercase text-[#C46B1E] font-bold block mb-1">
                  {ui.nakshatraLabel}
                </span>
                <h4 className="font-serif text-lg font-bold text-[#821C17]">
                  {localizeNakshatra(panchang?.nakshatra, locale)}
                </h4>
                <p className="text-xs text-[#421A10]/75 mt-1">
                  {ui.pada} {panchang?.nakshatra_pada || 3} {panchang?.nakshatra_end ? `· ${ui.endsAt} ${panchang.nakshatra_end}` : ''}
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-[#F9DAB5] text-[11px] text-[#C46B1E] font-semibold">
                {ui.consciousness}
              </div>
            </div>

            {/* 3. Yoga */}
            <div className="bg-[#FCEBD2]/70 border border-[#F9DAB5] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono uppercase text-[#C46B1E] font-bold block mb-1">
                  {ui.yogaLabel}
                </span>
                <h4 className="font-serif text-lg font-bold text-[#821C17]">
                  {localizeYoga(panchang?.yoga, locale)}
                </h4>
                <p className="text-xs text-[#421A10]/75 mt-1">
                  {panchang?.yoga_end ? `${ui.endsAt} ${panchang.yoga_end}` : ''}
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-[#F9DAB5] text-[11px] text-[#C46B1E] font-semibold">
                {ui.relationship}
              </div>
            </div>

            {/* 4. Karana */}
            <div className="bg-[#FCEBD2]/70 border border-[#F9DAB5] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono uppercase text-[#C46B1E] font-bold block mb-1">
                  {ui.karanaLabel}
                </span>
                <h4 className="font-serif text-lg font-bold text-[#821C17]">
                  {localizeKarana(panchang?.karana, locale)}
                </h4>
                <p className="text-xs text-[#421A10]/75 mt-1">
                  {panchang?.karana_end ? `${ui.endsAt} ${panchang.karana_end}` : ''}
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-[#F9DAB5] text-[11px] text-[#C46B1E] font-semibold">
                {ui.practicalExecution}
              </div>
            </div>

            {/* 5. Vara */}
            <div className="bg-[#FCEBD2]/70 border border-[#F9DAB5] rounded-2xl p-5 shadow-xs flex flex-col justify-between">
              <div>
                <span className="text-[11px] font-mono uppercase text-[#C46B1E] font-bold block mb-1">
                  {ui.varaLabel}
                </span>
                <h4 className="font-serif text-lg font-bold text-[#821C17]">
                  {localizeVara(panchang?.vara, dayIndex, locale)}
                </h4>
                <p className="text-xs text-[#421A10]/75 mt-1">
                  {rulingDeity}
                </p>
              </div>
              <div className="pt-4 mt-3 border-t border-[#F9DAB5] text-[11px] text-[#C46B1E] font-semibold">
                {ui.solarVitality}
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================= */}
        {/* MUHURAT BREAKDOWN: AUSPICIOUS VS INAUSPICIOUS             */}
        {/* ========================================================= */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Auspicious Muhurats (6 Cols) */}
          <div className="lg:col-span-6 bg-[#FDF5E6] border border-[#F9DAB5] rounded-3xl p-6 sm:p-8 space-y-5 shadow-xs">
            <div className="flex items-center justify-between border-b border-[#F9DAB5] pb-3">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-[#821C17]" />
                <h4 className="font-serif text-xl font-bold text-[#421A10]">
                  {ui.shubhMuhurat}
                </h4>
              </div>
              <span className="text-xs font-mono font-bold text-[#821C17] bg-[#E49D4B]/20 border border-[#E49D4B]/35 px-2.5 py-0.5 rounded-full">
                {ui.idealVentures}
              </span>
            </div>

            <div className="space-y-4">
              {/* Abhijit */}
              <div className="bg-[#FCEBD2] border border-[#E49D4B]/40 rounded-2xl p-4.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-serif text-base font-bold text-[#821C17] flex items-center gap-1.5">
                    <Sun className="w-4 h-4 text-[#C46B1E]" />
                    <span>{ui.abhijitMuhurat}</span>
                  </span>
                  <span className="text-[11px] font-mono font-bold text-[#821C17] bg-[#E49D4B]/25 px-2 py-0.5 rounded border border-[#E49D4B]/35">
                    {ui.mostVictorious}
                  </span>
                </div>
                <div className="font-mono text-lg font-bold text-[#421A10]">
                  {panchang?.abhijit || panchang?.abhijit_muhurta || '11:45 AM – 12:32 PM'}
                </div>
                <p className="text-xs text-[#421A10]/75">
                  {ui.abhijitDesc}
                </p>
              </div>

              {/* Brahma Muhurat */}
              <div className="bg-[#FCEBD2]/60 border border-[#F9DAB5] rounded-2xl p-4.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-serif text-base font-bold text-[#421A10] flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-[#E49D4B]" />
                    <span>{ui.brahmaMuhurat}</span>
                  </span>
                  <span className="text-[11px] font-mono font-medium text-[#C46B1E] bg-[#FDF5E6] px-2 py-0.5 rounded border border-[#F9DAB5]">
                    {ui.spiritualDawn}
                  </span>
                </div>
                <div className="font-mono text-lg font-bold text-[#421A10]">
                  {panchang?.brahma || '04:58 AM – 05:46 AM'}
                </div>
                <p className="text-xs text-[#421A10]/75">
                  {ui.brahmaDesc}
                </p>
              </div>
            </div>
          </div>

          {/* Inauspicious Periods (6 Cols) */}
          <div className="lg:col-span-6 bg-[#FDF5E6] border border-[#F9DAB5] rounded-3xl p-6 sm:p-8 space-y-5 shadow-xs">
            <div className="flex items-center justify-between border-b border-[#F9DAB5] pb-3">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-[#821C17]" />
                <h4 className="font-serif text-xl font-bold text-[#421A10]">
                  {ui.ashubhKaal}
                </h4>
              </div>
              <span className="text-xs font-mono font-bold text-[#821C17] bg-[#821C17]/10 border border-[#821C17]/25 px-2.5 py-0.5 rounded-full">
                {ui.avoidUndertakings}
              </span>
            </div>

            <div className="space-y-4">
              {/* Rahu Kaal */}
              <div className="bg-[#FCEBD2]/60 border border-[#821C17]/30 rounded-2xl p-4.5 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-serif text-base font-bold text-[#821C17] flex items-center gap-1.5">
                    <Clock className="w-4 h-4 text-[#821C17]" />
                    <span>{ui.rahuKaal}</span>
                  </span>
                  <span className="text-[11px] font-mono font-bold text-[#821C17] bg-[#821C17]/15 px-2 py-0.5 rounded border border-[#821C17]/30">
                    {ui.avoidInitiations}
                  </span>
                </div>
                <div className="font-mono text-lg font-bold text-[#821C17]">
                  {panchang?.rahu || panchang?.rahu_kaal || '09:20 AM – 10:45 AM'}
                </div>
                <p className="text-xs text-[#421A10]/75">
                  {ui.rahuDesc}
                </p>
              </div>

              {/* Yamaganda & Gulika in 2-col mini grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="bg-[#FDF5E6] border border-[#F9DAB5] rounded-xl p-3.5 space-y-1">
                  <span className="text-[11px] font-mono uppercase font-bold text-[#C46B1E] block">
                    {ui.yamaganda}
                  </span>
                  <span className="font-mono text-sm font-bold text-[#421A10] block">
                    {panchang?.yamaganda || '01:30 PM – 02:55 PM'}
                  </span>
                  <span className="text-[10px] text-[#421A10]/70 block">
                    {ui.yamagandaDesc}
                  </span>
                </div>

                <div className="bg-[#FDF5E6] border border-[#F9DAB5] rounded-xl p-3.5 space-y-1">
                  <span className="text-[11px] font-mono uppercase font-bold text-[#C46B1E] block">
                    {ui.gulikaKaal}
                  </span>
                  <span className="font-mono text-sm font-bold text-[#421A10] block">
                    {panchang?.gulika || panchang?.gulika_kaal || '06:34 AM – 08:00 AM'}
                  </span>
                  <span className="text-[10px] text-[#421A10]/70 block">
                    {ui.gulikaDesc}
                  </span>
                </div>
              </div>

              {/* Disha Shool notice */}
              <div className="bg-[#FCEBD2] rounded-xl p-3 text-xs text-[#421A10]/80 flex items-start gap-2 border border-[#F9DAB5]">
                <Info className="w-4 h-4 text-[#821C17] shrink-0 mt-0.5" />
                <span>
                  <strong>{ui.dishaShoolLabel}</strong> {dishaShoolString}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* ========================================================= */}
        {/* INTERACTIVE MODULE TABS: CHOGHADIYA, HORAS, TRANSITS, ETC.*/}
        {/* ========================================================= */}
        <div className="bg-[#FDF5E6] border border-[#F9DAB5] rounded-3xl p-6 sm:p-8 space-y-6 shadow-sm">
          {/* Navigation Pill Tabs */}
          <div className="flex flex-wrap items-center gap-2 border-b border-[#F9DAB5] pb-4">
            <button
              type="button"
              onClick={() => setActiveTab('planets')}
              className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl transition-all cursor-pointer ${
                activeTab === 'planets'
                  ? 'bg-[#821C17] text-[#FDF5E6] shadow-sm'
                  : 'bg-[#FCEBD2] text-[#421A10] hover:bg-[#F9DAB5]'
              }`}
            >
              {ui.tabPlanets}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('choghadiya')}
              className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl transition-all cursor-pointer ${
                activeTab === 'choghadiya'
                  ? 'bg-[#821C17] text-[#FDF5E6] shadow-sm'
                  : 'bg-[#FCEBD2] text-[#421A10] hover:bg-[#F9DAB5]'
              }`}
            >
              {ui.tabChoghadiya}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('horas')}
              className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl transition-all cursor-pointer ${
                activeTab === 'horas'
                  ? 'bg-[#821C17] text-[#FDF5E6] shadow-sm'
                  : 'bg-[#FCEBD2] text-[#421A10] hover:bg-[#F9DAB5]'
              }`}
            >
              {ui.tabHoras}
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('festivals')}
              className={`px-4 py-2 text-xs font-semibold uppercase tracking-wider rounded-xl transition-all cursor-pointer ${
                activeTab === 'festivals'
                  ? 'bg-[#821C17] text-[#FDF5E6] shadow-sm'
                  : 'bg-[#FCEBD2] text-[#421A10] hover:bg-[#F9DAB5]'
              }`}
            >
              {ui.tabFestivals} ({festivals.length})
            </button>
          </div>

          {/* TAB 1 (DEFAULT): PLANETARY TRANSITS */}
          {activeTab === 'planets' && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="border border-[#F9DAB5] rounded-2xl overflow-hidden bg-[#FDF5E6]">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-[#FCEBD2] text-[#821C17] border-b border-[#F9DAB5]">
                      <th className="py-3 px-4 font-serif font-bold uppercase tracking-wider">{ui.colGraha}</th>
                      <th className="py-3 px-4 font-serif font-bold uppercase tracking-wider">{ui.colRashi}</th>
                      <th className="py-3 px-4 font-serif font-bold uppercase tracking-wider">{ui.colDegrees}</th>
                      <th className="py-3 px-4 font-serif font-bold uppercase tracking-wider">{ui.colNakshatra}</th>
                      <th className="py-3 px-4 font-serif font-bold uppercase tracking-wider">{ui.colGati}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F9DAB5]">
                    {(panchang?.planets || []).map((p, idx) => (
                      <tr key={idx} className="hover:bg-[#FCEBD2]/50 transition-colors">
                        <td className="py-3 px-4 font-serif font-bold text-[#421A10]">
                          {localizePlanetName(p.name, locale)}
                        </td>
                        <td className="py-3 px-4 text-[#421A10]/80">
                          {localizeRashiName(p.sign, locale)}
                        </td>
                        <td className="py-3 px-4 font-mono font-bold text-[#821C17]">
                          {p.degree}
                        </td>
                        <td className="py-3 px-4 text-[#421A10]/80">
                          {localizeNakshatra(p.nakshatra, locale)}
                        </td>
                        <td className="py-3 px-4">
                          {p.retrograde ? (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#821C17]/15 text-[#821C17] border border-[#821C17]/30">
                              {ui.retrograde}
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#E49D4B]/20 text-[#821C17] border border-[#E49D4B]/35">
                              {ui.direct}
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 1: CHOGHADIYA */}
          {activeTab === 'choghadiya' && (
            <div className="space-y-6 animate-in fade-in duration-200">
              {/* Active Choghadiya callout */}
              {panchang?.current_choghadiya && (() => {
                const locCurr = localizeChoghadiyaItem(panchang.current_choghadiya, locale);
                return (
                  <div className="bg-[#FCEBD2] border-2 border-[#821C17]/30 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-xs">
                    <div className="flex items-center gap-3">
                      <span className="w-3 h-3 rounded-full bg-[#821C17] animate-ping" />
                      <div>
                        <span className="text-[11px] font-mono uppercase text-[#C46B1E] font-bold">
                          {ui.activeChoghadiyaNow}
                        </span>
                        <h5 className="font-serif text-lg font-bold text-[#821C17]">
                          {locCurr.name} ({locCurr.label})
                        </h5>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-xs font-mono text-[#421A10]/70">
                        {ui.duration} {panchang.current_choghadiya.start} – {panchang.current_choghadiya.end}
                      </span>
                      {panchang.current_choghadiya.time_remaining_str && (
                        <div className="text-xs font-mono font-bold text-[#821C17]">
                          {ui.remaining} {panchang.current_choghadiya.time_remaining_str}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })()}

              {/* Day & Night Tables */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Day Choghadiya */}
                <div className="space-y-3">
                  <h5 className="font-serif text-base font-bold text-[#421A10] flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <Sun className="w-4 h-4 text-[#E49D4B]" />
                      <span>{ui.dayChoghadiya}</span>
                    </span>
                  </h5>
                  <div className="border border-[#F9DAB5] rounded-2xl overflow-hidden bg-[#FDF5E6]">
                    <div className="divide-y divide-[#F9DAB5]">
                      {(panchang?.choghadiya_day || [
                        { name: 'Shubh', label: 'Auspicious', is_auspicious: true, start: '06:34 AM', end: '07:58 AM' },
                        { name: 'Rog', label: 'Inauspicious (Disease)', is_auspicious: false, start: '07:58 AM', end: '09:22 AM' },
                        { name: 'Udveg', label: 'Inauspicious (Anxiety)', is_auspicious: false, start: '09:22 AM', end: '10:46 AM' },
                        { name: 'Char', label: 'Mobile / Travel', is_auspicious: true, start: '10:46 AM', end: '12:10 PM' },
                        { name: 'Labh', label: 'Auspicious (Gain)', is_auspicious: true, start: '12:10 PM', end: '01:34 PM' },
                        { name: 'Amrit', label: 'Supreme Nectar', is_auspicious: true, start: '01:34 PM', end: '02:58 PM' },
                        { name: 'Kaal', label: 'Inauspicious (Loss)', is_auspicious: false, start: '02:58 PM', end: '04:22 PM' },
                        { name: 'Shubh', label: 'Auspicious', is_auspicious: true, start: '04:22 PM', end: '05:42 PM' },
                      ]).map((item, idx) => {
                        const locItem = localizeChoghadiyaItem(item, locale);
                        return (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-3 text-xs hover:bg-[#FCEBD2]/50 transition-colors"
                          >
                            <div className="flex items-center gap-2">
                              <span
                                className={`w-2 h-2 rounded-full ${
                                  locItem.is_auspicious ? 'bg-[#821C17]' : 'bg-[#421A10]/40'
                                }`}
                              />
                              <span className="font-serif font-bold text-[#421A10]">{locItem.name}</span>
                              <span className="text-[10px] text-[#421A10]/70">({locItem.label})</span>
                            </div>
                            <span className="font-mono text-[#821C17] font-semibold">{locItem.start} – {locItem.end}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Night Choghadiya */}
                <div className="space-y-3">
                  <h5 className="font-serif text-base font-bold text-[#421A10] flex items-center justify-between">
                    <span className="flex items-center gap-1.5">
                      <Moon className="w-4 h-4 text-[#821C17]" />
                      <span>{ui.nightChoghadiya}</span>
                    </span>
                  </h5>
                  <div className="border border-[#F9DAB5] rounded-2xl overflow-hidden bg-[#FDF5E6]">
                    <div className="divide-y divide-[#F9DAB5]">
                      {(panchang?.choghadiya_night || [
                        { name: 'Amrit', label: 'Supreme Nectar', is_auspicious: true, start: '05:42 PM', end: '07:18 PM' },
                        { name: 'Char', label: 'Neutral / Travel', is_auspicious: true, start: '07:18 PM', end: '08:54 PM' },
                        { name: 'Rog', label: 'Inauspicious', is_auspicious: false, start: '08:54 PM', end: '10:30 PM' },
                        { name: 'Kaal', label: 'Inauspicious', is_auspicious: false, start: '10:30 PM', end: '12:06 AM' },
                        { name: 'Labh', label: 'Auspicious (Gain)', is_auspicious: true, start: '12:06 AM', end: '01:42 AM' },
                        { name: 'Udveg', label: 'Inauspicious', is_auspicious: false, start: '01:42 AM', end: '03:18 AM' },
                        { name: 'Shubh', label: 'Auspicious', is_auspicious: true, start: '03:18 AM', end: '04:54 AM' },
                        { name: 'Amrit', label: 'Supreme Nectar', is_auspicious: true, start: '04:54 AM', end: '06:34 AM' },
                      ]).map((item, idx) => {
                        const locItem = localizeChoghadiyaItem(item, locale);
                        return (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-3 text-xs hover:bg-[#FCEBD2]/50 transition-colors"
                          >
                            <div className="flex items-center gap-2">
                              <span
                                className={`w-2 h-2 rounded-full ${
                                  locItem.is_auspicious ? 'bg-[#821C17]' : 'bg-[#421A10]/40'
                                }`}
                              />
                              <span className="font-serif font-bold text-[#421A10]">{locItem.name}</span>
                              <span className="text-[10px] text-[#421A10]/70">({locItem.label})</span>
                            </div>
                            <span className="font-mono text-[#821C17] font-semibold">{locItem.start} – {locItem.end}</span>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: HORAS */}
          {activeTab === 'horas' && (
            <div className="space-y-4 animate-in fade-in duration-200">
              <div className="flex items-center justify-between text-xs text-[#421A10]/75">
                <span>{ui.horasDesc}</span>
                <span className="font-mono text-[#821C17] font-bold">{ui.horaDuration}</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                {(panchang?.horas || [
                  { hour_number: 1, planet: 'Sun', start: '06:34 AM', end: '07:34 AM' },
                  { hour_number: 2, planet: 'Venus', start: '07:34 AM', end: '08:34 AM' },
                  { hour_number: 3, planet: 'Mercury', start: '08:34 AM', end: '09:34 AM' },
                  { hour_number: 4, planet: 'Moon', start: '09:34 AM', end: '10:34 AM' },
                  { hour_number: 5, planet: 'Saturn', start: '10:34 AM', end: '11:34 AM' },
                  { hour_number: 6, planet: 'Jupiter', start: '11:34 AM', end: '12:34 PM' },
                  { hour_number: 7, planet: 'Mars', start: '12:34 PM', end: '01:34 PM' },
                  { hour_number: 8, planet: 'Sun', start: '01:34 PM', end: '02:34 PM' },
                  { hour_number: 9, planet: 'Venus', start: '02:34 PM', end: '03:34 PM' },
                  { hour_number: 10, planet: 'Mercury', start: '03:34 PM', end: '04:34 PM' },
                  { hour_number: 11, planet: 'Moon', start: '04:34 PM', end: '05:34 PM' },
                  { hour_number: 12, planet: 'Saturn', start: '05:34 PM', end: '06:34 PM' },
                ]).map((h, idx) => (
                  <div
                    key={idx}
                    className="bg-[#FCEBD2]/50 border border-[#F9DAB5] rounded-xl p-3 flex items-center justify-between text-xs"
                  >
                    <div>
                      <span className="text-[10px] font-mono text-[#C46B1E] font-bold block">
                        {ui.hora} {h.hour_number}
                      </span>
                      <span className="font-serif font-bold text-[#421A10] text-sm">
                        {localizePlanetName(h.planet, locale)}
                      </span>
                    </div>
                    <span className="font-mono text-[#821C17] font-semibold text-[11px]">
                      {h.start} – {h.end}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}



          {/* TAB 4: UPCOMING FESTIVALS */}
          {activeTab === 'festivals' && (
            <div className="space-y-4 animate-in fade-in duration-200">
              {/* Category Filter Pills */}
              <div className="flex flex-wrap items-center gap-1.5 pb-2">
                {[
                  { id: 'all', label: ui.filterAll },
                  { id: 'major', label: ui.filterMajor },
                  { id: 'ekadashi', label: ui.filterEkadashi },
                  { id: 'vrat', label: ui.filterVrat },
                  { id: 'purnima', label: ui.filterPurnima },
                ].map((f) => (
                  <button
                    key={f.id}
                    type="button"
                    onClick={() => setFestivalFilter(f.id)}
                    className={`px-3 py-1 rounded-lg text-xs font-semibold transition-all cursor-pointer ${
                      festivalFilter === f.id
                        ? 'bg-[#821C17] text-[#FDF5E6]'
                        : 'bg-[#FCEBD2] text-[#421A10] hover:bg-[#F9DAB5]'
                    }`}
                  >
                    {f.label}
                  </button>
                ))}
              </div>

              {/* Festival Cards List */}
              <div className="space-y-3">
                {filteredFestivals.length === 0 ? (
                  <div className="p-8 text-center text-xs text-[#421A10]/70 bg-[#FCEBD2]/50 rounded-2xl border border-[#F9DAB5]">
                    {ui.noFestivals}
                  </div>
                ) : (
                  filteredFestivals.map((fest, idx) => (
                    <div
                      key={idx}
                      className={`p-4 sm:p-5 rounded-2xl border transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 ${
                        fest.is_today
                          ? 'bg-[#FCEBD2] border-2 border-[#821C17]'
                          : 'bg-[#FDF5E6] border-[#F9DAB5] hover:border-[#821C17]'
                      }`}
                    >
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] flex items-center justify-center text-2xl shrink-0">
                          {fest.icon || '🪔'}
                        </div>
                        <div className="space-y-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <h5 className="font-serif text-lg font-bold text-[#421A10]">
                              {fest.name}
                            </h5>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-[#E49D4B]/15 text-[#821C17] border border-[#E49D4B]/30 font-semibold uppercase">
                              {fest.tag}
                            </span>
                          </div>
                          <p className="text-xs text-[#421A10]/75">
                            {fest.desc}
                          </p>
                          <div className="text-[11px] font-mono text-[#C46B1E] flex flex-wrap items-center gap-3 pt-0.5">
                            <span>{fest.tithi}</span>
                            <span>•</span>
                            <span>{fest.paksha} {locale === 'en' ? 'Paksha' : 'पक्ष'}</span>
                            <span>•</span>
                            <span>{ui.colNakshatra}: {fest.nakshatra}</span>
                          </div>
                          {fest.remedies && (
                            <p className="text-xs text-[#821C17] font-semibold pt-1">
                              🙏 {ui.remedyLabel} {fest.remedies}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="text-right sm:self-center shrink-0">
                        <span className="font-serif text-lg font-bold text-[#821C17] block">
                          {fest.date}
                        </span>
                        <span className="text-[10px] font-mono text-[#421A10]/70 uppercase block">
                          {fest.is_today ? ui.today : ui.upcoming}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* ========================================================= */}
        {/* VEDIC WISDOM FOOTNOTE                                     */}
        {/* ========================================================= */}
        <div className="bg-[#421A10] text-[#FDF5E6] rounded-3xl p-6 sm:p-8 border border-[#821C17]/40 space-y-2 text-center">
          <p className="font-serif text-sm sm:text-base font-semibold text-[#F3C387] tracking-wide">
            {ui.shlokaSanskrit}
          </p>
          <p className="text-xs sm:text-sm text-[#FCEBD2]/75 max-w-3xl mx-auto italic">
            {ui.shlokaTranslation}
          </p>
          <span className="text-[10px] font-mono text-[#E49D4B] uppercase tracking-widest block pt-2">
            {ui.shlokaSource}
          </span>
        </div>

      </div>
    </div>
  );
}
