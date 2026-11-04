'use client';

import React, { useState, useEffect } from 'react';
import { useLocale } from 'next-intl';
import {
  Compass,
  Sparkles,
  Calendar,
  Clock,
  MapPin,
  User,
  Heart,
  Briefcase,
  Coins,
  Activity,
  Users,
  GraduationCap,
  Home,
  ShieldAlert,
  Plane,
  Flame,
  FileText,
  ChevronDown,
  BookOpen,
  Printer,
  Download,
  AlertTriangle,
  Send,
  Brain,
  Check,
  X,
  Globe,
} from 'lucide-react';

import {
  DOMAINS_LIST,
  PREDICTION_TRANSLATIONS,
  type DomainMeta,
} from './predictionLocalization';
import {
  openPrintablePredictionReport,
  type ReportLanguage,
} from './predictionReportGenerator';

const ICON_MAP: Record<string, any> = {
  Heart,
  Briefcase,
  Coins,
  Activity,
  Users,
  GraduationCap,
  Home,
  ShieldAlert,
  Plane,
  Flame,
};

function scoreColor(s: number): string {
  if (s >= 75) return '#15803D';
  if (s >= 55) return '#C46B1E';
  if (s >= 35) return '#EA580C';
  return '#DC2626';
}

export default function PredictionModule() {
  const locale = useLocale();
  const t = PREDICTION_TRANSLATIONS[locale] || PREDICTION_TRANSLATIONS.en;

  // Form State
  const [fullName, setFullName] = useState('Atharv');
  const [dob, setDob] = useState('2004-11-02');
  const [tob, setTob] = useState('16:15');
  const [city, setCity] = useState('Pune');

  // Autocomplete
  const [citiesList, setCitiesList] = useState<string[]>([]);
  const [citySuggestions, setCitySuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Results State
  const [loading, setLoading] = useState(false);
  const [domainsData, setDomainsData] = useState<any>(null);
  const [activeDomainKey, setActiveDomainKey] = useState<string>('marriage');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Language Selection for Report
  const [selectedReportLang, setSelectedReportLang] = useState<ReportLanguage>(
    (['en', 'hi', 'mr'].includes(locale) ? (locale as ReportLanguage) : 'en')
  );
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);

  // Chat State
  const [chatMessages, setChatMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string }>>([
    {
      sender: 'ai',
      text: 'Namaste! I am your AstroLogic Life Domain Intelligence advisor. You can inquire about career promotion windows, marriage timing, wealth cycles, or specific remedial rituals.',
    },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Sync report language with active locale
  useEffect(() => {
    if (['en', 'hi', 'mr'].includes(locale)) {
      setSelectedReportLang(locale as ReportLanguage);
    }
  }, [locale]);

  // Load cities list
  useEffect(() => {
    fetch('/api/cities')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setCitiesList(data);
      })
      .catch(() => {});
  }, []);

  const handleCityChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setCity(val);
    if (val.trim().length >= 2 && citiesList.length > 0) {
      const q = val.toLowerCase();
      const filtered = citiesList.filter((c) => c.toLowerCase().startsWith(q)).slice(0, 8);
      setCitySuggestions(filtered);
      setShowSuggestions(filtered.length > 0);
    } else {
      setShowSuggestions(false);
    }
  };

  // Sample Profile Quick Fill
  const handleQuickSample = () => {
    setFullName('Atharv');
    setDob('2004-11-02');
    setTob('16:15');
    setCity('Pune');
    setTimeout(() => {
      handleAnalyze();
    }, 50);
  };

  // Main Domain Analysis
  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!dob || !tob || !city) {
      setErrorMsg('Please enter date of birth, time of birth, and city.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    const [year, month, day] = dob.split('-').map(Number);
    const [hour, minute] = tob.split(':').map(Number);

    try {
      const res = await fetch('/api/domains', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          year,
          month,
          day,
          hour: hour || 12,
          minute: minute || 0,
          city: city.trim() || 'Pune',
        }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || data.message || 'Domain analysis failed');
      setDomainsData(data);
    } catch (err: any) {
      setErrorMsg(err.message || 'Error communicating with planetary prediction engine.');
    } finally {
      setLoading(false);
    }
  };

  // Generate & Print Report
  const handlePrintReport = (langOverride?: ReportLanguage) => {
    const targetLang = langOverride || selectedReportLang;
    if (domainsData) {
      openPrintablePredictionReport({
        name: fullName || 'Native',
        dob,
        tob,
        city,
        domainsData,
        reportLanguage: targetLang,
      });
    } else {
      handleAnalyze().then(() => {
        // Will be ready on state update or user can re-click
      });
    }
  };

  // AI Chat Consultation
  const handleSendChat = async (presetText?: string) => {
    const text = presetText || chatInput;
    if (!text.trim() || chatLoading) return;

    setChatMessages((prev) => [...prev, { sender: 'user', text }]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch('/api/kundali-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: `Regarding the 10 life domain predictions: ${text}`,
          chart: domainsData || {},
        }),
      });
      const data = await res.json();
      const reply = data.reply || data.response || 'Planetary alignments indicate key supportive influences in your active houses.';
      setChatMessages((prev) => [...prev, { sender: 'ai', text: reply }]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: 'Vedic assessments point toward positive Dasha triggers in primary Kendra houses. Maintain morning discipline and chant your Lagna lord Beej mantra.',
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const activeDomainMeta = DOMAINS_LIST.find((d) => d.key === activeDomainKey) || DOMAINS_LIST[0];
  const activeDomainData = domainsData?.domains?.[activeDomainKey] || {};
  const activeScore = activeDomainData?.score || 60;
  const activeColor = scoreColor(activeScore);
  const timing = activeDomainData?.timing || {};
  const remedies = activeDomainData?.remedies || {};
  const prList = remedies.planet_remedies || [];

  return (
    <div className="pt-6 sm:pt-10 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-10">
      {/* ── Page Header & Ornamental Eyebrow ── */}
      <div className="text-center max-w-3xl mx-auto space-y-4">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#821C17]/10 border border-[#821C17]/25 text-[#821C17] text-xs font-semibold tracking-wider uppercase">
          <Compass className="w-3.5 h-3.5 text-[#C46B1E]" />
          <span>{t.badge}</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#421A10] tracking-tight">
          {t.title}
        </h1>
        {/* Sacred Almanac Centerline */}
        <div className="flex items-center justify-center gap-3 py-1">
          <span className="h-px w-14 bg-linear-to-r from-transparent to-[#E49D4B]" />
          <span className="w-2 h-2 rotate-45 bg-[#821C17]" />
          <span className="h-px w-14 bg-linear-to-l from-transparent to-[#E49D4B]" />
        </div>
        <p className="text-base text-[#421A10]/75 leading-relaxed">
          {t.subtitle}
        </p>
      </div>

      {/* ── Form Input Section Card (Matches Exact Refined UI) ── */}
      <div className="sacred-card p-6 sm:p-8 border border-[#F9DAB5] shadow-xs bg-[#FDF5E6] rounded-2xl">
        {/* Card Header: Pen/Sparkles + Title/Subtitle on Left, Use Sample Chart on Right */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-5 border-b border-[#F9DAB5] mb-6">
          <div className="flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-[#821C17]/10 text-[#821C17] border border-[#821C17]/20 mt-0.5 shadow-2xs">
              <Sparkles className="w-5 h-5 text-[#821C17]" />
            </div>
            <div>
              <h2 className="font-serif text-xl sm:text-2xl font-bold text-[#821C17] tracking-tight">
                {t.inputCardTitle}
              </h2>
              <p className="text-xs text-[#421A10]/70 mt-0.5">
                {t.inputCardSubtitle}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleQuickSample}
            className="self-start sm:self-center inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#821C17] bg-[#FDF5E6] hover:bg-[#FCEBD2] border border-[#821C17]/30 transition-all shadow-2xs hover:shadow-xs cursor-pointer active:scale-95"
          >
            <BookOpen className="w-4 h-4 text-[#C46B1E]" />
            <span>{t.sampleProfileBtn}</span>
          </button>
        </div>

        <form onSubmit={handleAnalyze} className="space-y-6">
          {/* 4 Balanced Input Columns */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4.5">
            {/* Full Name */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#421A10]">
                {t.fullNameLabel}
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#C46B1E]" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder={t.fullNamePlaceholder}
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-[#421A10] placeholder-[#421A10]/40 focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 transition-all"
                />
              </div>
            </div>

            {/* Date of Birth */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#421A10]">
                {t.dobLabel}
              </label>
              <div className="relative">
                <Calendar className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#C46B1E]" />
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  required
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-[#421A10] focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 transition-all cursor-pointer"
                />
              </div>
            </div>

            {/* Time of Birth */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#421A10]">
                {t.tobLabel}
              </label>
              <div className="relative">
                <Clock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#C46B1E]" />
                <input
                  type="time"
                  value={tob}
                  onChange={(e) => setTob(e.target.value)}
                  required
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-[#421A10] focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 transition-all cursor-pointer"
                />
              </div>
            </div>

            {/* Birth City Autocomplete */}
            <div className="space-y-1.5 relative">
              <label className="block text-xs font-semibold text-[#421A10]">
                {t.cityLabel}
              </label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#C46B1E]" />
                <input
                  type="text"
                  value={city}
                  onChange={handleCityChange}
                  onFocus={() => city.trim().length >= 2 && setShowSuggestions(true)}
                  placeholder={t.cityPlaceholder}
                  required
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-[#421A10] placeholder-[#421A10]/40 focus:outline-none focus:ring-2 focus:ring-[#821C17]/30 transition-all"
                />
              </div>
              {/* Dropdown Suggestions */}
              {showSuggestions && citySuggestions.length > 0 && (
                <ul className="absolute z-30 left-0 right-0 top-[calc(100%+4px)] bg-[#FDF5E6] border border-[#821C17]/30 rounded-xl shadow-xl max-h-48 overflow-y-auto divide-y divide-[#F9DAB5]/60">
                  {citySuggestions.map((c) => (
                    <li
                      key={c}
                      onClick={() => {
                        setCity(c);
                        setShowSuggestions(false);
                      }}
                      className="px-4 py-2.5 text-xs text-[#421A10] hover:bg-[#FCEBD2] hover:text-[#821C17] cursor-pointer transition-colors"
                    >
                      {c}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Centered Actions Below Inputs */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            {/* Primary Action Button */}
            <button
              type="submit"
              disabled={loading}
              className="py-3 px-8 rounded-xl bg-linear-to-r from-[#821C17] via-[#9E2A2B] to-[#821C17] text-[#FDF5E6] font-bold text-sm shadow-md hover:brightness-110 active:scale-98 transition-all disabled:opacity-50 flex items-center justify-center gap-2.5 cursor-pointer min-w-[220px]"
            >
              <Sparkles className="w-4 h-4 text-[#F3C387]" />
              <span>{loading ? t.generatingBtn : t.generateBtn}</span>
            </button>

            {/* Secondary Action: Split Dropdown Button for PDF Report */}
            <div className="inline-flex rounded-xl shadow-xs bg-[#FCEBD2] border border-[#821C17]/30 hover:border-[#821C17]/60 transition-all overflow-hidden group">
              <button
                type="button"
                onClick={() => {
                  if (domainsData) {
                    handlePrintReport(selectedReportLang);
                  } else {
                    handleAnalyze();
                  }
                }}
                title="Generate and print full visual 10-domain report"
                className="py-3 pl-5 pr-3 text-sm font-bold text-[#821C17] hover:bg-[#F9DAB5] flex items-center gap-2 cursor-pointer transition-colors"
              >
                <FileText className="w-4 h-4 text-[#821C17]" />
                <span>{t.generatePdfReportBtn}</span>
              </button>
              <div className="w-px bg-[#821C17]/25 self-stretch my-2" />
              <button
                type="button"
                onClick={() => setIsReportModalOpen(true)}
                title="Select language and format for prediction report"
                className="py-3 px-3.5 text-[#821C17] hover:bg-[#F9DAB5] flex items-center justify-center cursor-pointer transition-colors"
              >
                <ChevronDown className="w-4 h-4" />
              </button>
            </div>
          </div>
        </form>

        {errorMsg && (
          <div className="mt-5 p-3.5 rounded-xl bg-red-100/90 border border-red-300 text-red-900 text-xs flex items-center gap-2.5">
            <AlertTriangle className="w-4 h-4 shrink-0 text-red-700" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* ── Results Container ── */}
      {domainsData ? (
        <div className="space-y-10 animate-fadeIn">
          {/* Birth Context Ribbon */}
          <div className="p-4 rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] flex flex-wrap items-center justify-between gap-4 text-xs font-medium text-[#421A10]">
            <div className="flex items-center gap-3">
              <span className="font-bold text-[#821C17]">🌅 Lagna:</span>
              <span className="font-semibold">{domainsData.lagna || '—'}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-bold text-[#C46B1E]">⏱ Active Dasha:</span>
              <span className="font-semibold">{domainsData.mahadasha || '—'} / {domainsData.antardasha || '—'}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="font-bold text-[#15803D]">✦ Synthesis:</span>
              <span>10 Life Domains Parashari Fusion</span>
            </div>
            <button
              onClick={() => setIsReportModalOpen(true)}
              className="ml-auto inline-flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[#821C17] text-[#FDF5E6] font-bold text-xs hover:brightness-110 cursor-pointer shadow-2xs"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>{selectedReportLang === 'mr' ? 'अहवाल प्रिंट करा' : selectedReportLang === 'hi' ? 'रिपोर्ट प्रिंट करें' : 'Print Dossier'}</span>
            </button>
          </div>

          {/* ── 10 Domains Overview Grid ── */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="font-serif text-lg font-bold text-[#821C17]">
                {t.overviewTitle}
              </h3>
              <span className="text-xs text-[#421A10]/70">
                {t.overviewSubtitle}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3.5">
              {DOMAINS_LIST.map((dm) => {
                const Icon = ICON_MAP[dm.icon] || Sparkles;
                const d = domainsData.domains?.[dm.key] || {};
                const sc = d.score || 60;
                const col = scoreColor(sc);
                const isActive = activeDomainKey === dm.key;
                const domainTitle = locale === 'mr' ? dm.mrName : locale === 'hi' ? dm.hiName : dm.enName;

                return (
                  <div
                    key={dm.key}
                    onClick={() => setActiveDomainKey(dm.key)}
                    className={`p-4 rounded-xl border-2 transition-all cursor-pointer flex flex-col justify-between group ${
                      isActive
                        ? 'bg-[#FCEBD2] border-[#821C17] shadow-sm ring-1 ring-[#821C17]'
                        : 'bg-[#FDF5E6] border-[#F9DAB5] hover:border-[#821C17]/40 hover:-translate-y-0.5'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <div className={`p-2 rounded-lg ${isActive ? 'bg-[#821C17] text-[#FDF5E6]' : 'bg-[#FCEBD2] text-[#821C17] group-hover:bg-[#821C17] group-hover:text-[#FDF5E6]'} transition-colors`}>
                          <Icon className="w-4 h-4" />
                        </div>
                        {d.dasha_active && (
                          <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-[#dcfce7] text-[#15803d]">
                            Dasha
                          </span>
                        )}
                      </div>
                      <div className="font-serif text-xs font-bold text-[#421A10] group-hover:text-[#821C17] transition-colors leading-tight line-clamp-1">
                        {domainTitle}
                      </div>
                      <div className="text-[10px] text-[#421A10]/60 mt-0.5 font-mono">
                        {dm.house.split('·')[0]}
                      </div>
                    </div>

                    <div className="mt-3 pt-2 border-t border-[#F9DAB5]/60">
                      <div className="flex items-baseline justify-between mb-1">
                        <span className="text-[10px] uppercase font-semibold text-[#421A10]/70">Score</span>
                        <span className="font-bold text-sm" style={{ color: col }}>
                          {sc}%
                        </span>
                      </div>
                      <div className="bg-[#FCEBD2] h-1.5 rounded-full overflow-hidden">
                        <div className="h-full rounded-full transition-all duration-700" style={{ width: `${sc}%`, backgroundColor: col }} />
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* ── Sub-Tabs Navigation for 10 Domains ── */}
          <div className="flex items-center gap-2 overflow-x-auto pb-3 border-b border-[#E49D4B]/30 scrollbar-none">
            {DOMAINS_LIST.map((dm) => {
              const Icon = ICON_MAP[dm.icon] || Sparkles;
              const isActive = activeDomainKey === dm.key;
              const d = domainsData.domains?.[dm.key] || {};
              const sc = d.score || 60;
              const domainTitle = locale === 'mr' ? dm.mrName : locale === 'hi' ? dm.hiName : dm.enName;

              return (
                <button
                  key={dm.key}
                  onClick={() => setActiveDomainKey(dm.key)}
                  className={`inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-bold tracking-wide transition-all whitespace-nowrap cursor-pointer ${
                    isActive
                      ? 'bg-[#821C17] text-[#FDF5E6] shadow-sm ring-1 ring-[#821C17]'
                      : 'bg-[#FCEBD2] text-[#421A10]/75 hover:text-[#821C17] hover:bg-[#F9DAB5]'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{domainTitle}</span>
                  <span className={`px-1.5 py-0.2 rounded text-[10px] ${isActive ? 'bg-black/20 text-[#FDF5E6]' : 'bg-[#821C17]/10 text-[#821C17]'}`}>
                    {sc}%
                  </span>
                </button>
              );
            })}
          </div>

          {/* ── Domain Detail Panel (Split Layout from prediction.html) ── */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
            {/* Left 2 Cols: Main Evaluation & Indicators */}
            <div className="lg:col-span-2 space-y-6">
              {/* Domain Header Card */}
              <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] rounded-2xl space-y-5">
                <div className="flex items-center justify-between pb-4 border-b border-[#F9DAB5]">
                  <div className="flex items-center gap-3">
                    <div className="p-3 rounded-xl bg-[#821C17] text-[#FDF5E6] shadow-sm">
                      {React.createElement(ICON_MAP[activeDomainMeta.icon] || Sparkles, { className: 'w-6 h-6' })}
                    </div>
                    <div>
                      <h3 className="font-serif text-2xl font-bold text-[#821C17]">
                        {locale === 'mr' ? activeDomainMeta.mrName : locale === 'hi' ? activeDomainMeta.hiName : activeDomainMeta.enName}
                      </h3>
                      <p className="text-xs text-[#421A10]/70 font-medium mt-0.5">
                        {activeDomainMeta.house} &nbsp;·&nbsp;
                        {activeDomainData.dasha_active ? (
                          <span className="text-[#15803D] font-bold">✓ {t.dashaActiveBadge}</span>
                        ) : (
                          <span className="text-[#421A10]/60">{t.dashaInactiveBadge}</span>
                        )}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <div className="font-serif text-3xl font-bold" style={{ color: activeColor }}>
                      {activeScore}%
                    </div>
                    <div className="text-[10px] uppercase font-semibold text-[#421A10]/60 tracking-wider">
                      {t.domainScoreLabel}
                    </div>
                  </div>
                </div>

                {/* Narrative Astrological Analysis */}
                <div className="space-y-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#C46B1E] flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>{t.analysisTitle}</span>
                  </h4>
                  <p className="text-sm text-[#421A10] leading-relaxed font-serif bg-[#FCEBD2]/50 p-4 rounded-xl border border-[#F9DAB5]">
                    {activeDomainData.analysis || (locale === 'mr' ? activeDomainMeta.mrSub : locale === 'hi' ? activeDomainMeta.hiSub : activeDomainMeta.enSub)}
                  </p>
                </div>

                {/* Key Indicators Rows */}
                <div className="space-y-3 pt-2">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-[#821C17] flex items-center gap-2 border-b border-[#F9DAB5]/60 pb-2">
                    <Compass className="w-3.5 h-3.5" />
                    <span>{t.keyIndicatorsTitle}</span>
                  </h4>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    {activeDomainKey === 'marriage' && (
                      <>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Type of Union:</span>
                          <strong className="text-[#821C17]">{activeDomainData.marriage_type || 'Traditional arrangement with strong mutual dharma'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Partner Sign / Traits:</span>
                          <strong className="text-[#421A10]">{activeDomainData.partner_sign || 'Aligned Kendra sign'} ({activeDomainData.partner_traits || 'Responsible, cultured'})</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Mangal Dosh:</span>
                          <strong className={activeDomainData.mangal_dosh ? 'text-red-700' : 'text-green-700'}>
                            {activeDomainData.mangal_dosh ? '⚠ Present — Peace rituals advised' : '✓ Absent / Mitigated'}
                          </strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">7th House Lord:</span>
                          <strong>{activeDomainData.seventh_lord || 'Favorable placement'}</strong>
                        </div>
                      </>
                    )}

                    {activeDomainKey === 'career' && (
                      <>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Career Sector:</span>
                          <strong className="text-[#821C17]">{activeDomainData.sector || 'Management, Tech & Advisory'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Business vs Employment:</span>
                          <strong className="text-[#421A10]">{activeDomainData.business_vs_job || 'Leadership in structured enterprises'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Raj Yogas in 10th:</span>
                          <strong className="text-green-700">{activeDomainData.raj_yogas?.join(', ') || 'Classical Dharma-Karmadhipati'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">10th House Lord:</span>
                          <strong>{activeDomainData.tenth_lord || 'Sun/Mars influence'}</strong>
                        </div>
                      </>
                    )}

                    {activeDomainKey === 'wealth' && (
                      <>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Primary Incomes:</span>
                          <strong className="text-[#821C17]">{activeDomainData.income_sources || 'Professional expertise and strategic investments'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Dhana Yogas:</span>
                          <strong className="text-green-700">{activeDomainData.dhana_yogas?.join(', ') || 'Lakshmi Yoga alignment'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Debt & Financial Risk:</span>
                          <strong>{activeDomainData.debt_risk || 'Low / Well mitigated'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Wealth Lords (2nd & 11th):</span>
                          <strong>{activeDomainData.second_lord || 'Jupiter / Mercury'}</strong>
                        </div>
                      </>
                    )}

                    {activeDomainKey === 'health' && (
                      <>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Ayurvedic Prakriti:</span>
                          <strong className="text-[#821C17]">{activeDomainData.ayurvedic_dosha || 'Pitta-Vata balance'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Sensitive Areas:</span>
                          <strong className="text-amber-800">{activeDomainData.weak_organs || 'Digestive fire, respiratory rhythms'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Mental Peace:</span>
                          <strong>{activeDomainData.mental_health_ok ? 'Stable Moon indicators' : 'Meditation recommended during full moon'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Lagna Lord:</span>
                          <strong>{activeDomainData.first_lord || 'Vital and protective'}</strong>
                        </div>
                      </>
                    )}

                    {activeDomainKey === 'challenges' && (
                      <>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Kaal Sarp Yoga:</span>
                          <strong>{activeDomainData.kaal_sarp ? '⚠ Active placement' : '✓ Absent'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Sade Sati Phase:</span>
                          <strong>{activeDomainData.sade_sati ? '⚠ Active discipline phase' : '✓ Inactive'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Pitru / Grahan Dosh:</span>
                          <strong>{activeDomainData.pitru_dosh ? 'Charity advised on Amavasya' : '✓ Unafflicted'}</strong>
                        </div>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs">
                          <span className="text-[#421A10]/70 block">Legal & Adversary Risk:</span>
                          <strong>{activeDomainData.legal_risk ? 'Caution during Saturn sub-periods' : '✓ Favorable Kendra protection'}</strong>
                        </div>
                      </>
                    )}

                    {/* Generic Fallback Indicators for remaining domains */}
                    {!['marriage', 'career', 'wealth', 'health', 'challenges'].includes(activeDomainKey) && (
                      <>
                        <div className="p-2.5 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5] text-xs col-span-2">
                          <span className="text-[#421A10]/70 block">Cosmic Indicator Status:</span>
                          <strong className="text-[#821C17]">
                            House activations aligned with {activeDomainMeta.house}
                          </strong>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>

            {/* Right 1 Col: Sidebar with Timing, Remedies & Summary */}
            <div className="space-y-6">
              {/* Timing Windows Box */}
              <div className="sacred-card p-5 bg-[#FDF5E6] border border-[#F9DAB5] rounded-2xl space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#15803D] pb-2 border-b border-[#F9DAB5]">
                  <Clock className="w-4 h-4" />
                  <span>{t.timingTitle}</span>
                </div>
                <div className="space-y-2 text-xs">
                  <div className="flex justify-between pb-1 border-b border-[#F9DAB5]/40">
                    <span className="text-[#421A10]/70">{t.bestWindowLabel}:</span>
                    <strong className="text-[#15803D]">{timing.best_window || 'Auspicious Parashari baseline'}</strong>
                  </div>
                  <div className="flex justify-between pb-1 border-b border-[#F9DAB5]/40">
                    <span className="text-[#421A10]/70">{t.confidenceLabel}:</span>
                    <strong>{timing.confidence || 'Moderate / Favorable'}</strong>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-[#421A10]/70">Dasha Trigger:</span>
                    <strong className={activeDomainData.dasha_active ? 'text-[#15803D]' : 'text-[#421A10]'}>
                      {activeDomainData.dasha_active ? '✓ Currently Activated' : 'Secondary activation'}
                    </strong>
                  </div>
                </div>
              </div>

              {/* Classical Vedic Remedies Box */}
              <div className="sacred-card p-5 bg-[#FDF5E6] border border-[#F9DAB5] rounded-2xl space-y-3">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#821C17] pb-2 border-b border-[#F9DAB5]">
                  <Sparkles className="w-4 h-4 text-[#C46B1E]" />
                  <span>{t.remediesTitle}</span>
                </div>

                <div className="space-y-3 text-xs">
                  {prList.length ? (
                    prList.map((r: any, idx: number) => (
                      <div key={idx} className="p-3 rounded-xl bg-[#FCEBD2]/50 border border-[#F9DAB5] space-y-1.5">
                        <div className="font-bold text-[#821C17] flex items-center justify-between">
                          <span>🪐 {r.planet}</span>
                          <span className="text-[10px] text-[#C46B1E] uppercase font-mono">Prescription</span>
                        </div>
                        {r.gem && <div><strong>💎 {t.gemstoneLabel}:</strong> {r.gem}</div>}
                        {r.mantra && <div><strong>📿 {t.mantraLabel}:</strong> {r.mantra}</div>}
                        {r.fast && <div><strong>🍽 {t.fastLabel}:</strong> {r.fast}</div>}
                        {r.donate && <div><strong>🤲 {t.donateLabel}:</strong> {r.donate}</div>}
                      </div>
                    ))
                  ) : (
                    <div className="p-3 rounded-xl bg-[#FCEBD2]/40 text-[#421A10]/80">
                      Chanting the Gayatri Mantra and watering the Tulsi plant during sunrise hours strengthens general vitality for this domain.
                    </div>
                  )}

                  {remedies.ritual && (
                    <div className="p-2.5 rounded-lg bg-[#FCEBD2] border-l-2 border-[#821C17] text-[11px] text-[#421A10]">
                      🪔 <strong>{t.ritualLabel}:</strong> {remedies.ritual}
                    </div>
                  )}
                </div>
              </div>

              {/* Quick Summary Pill */}
              <div className="p-4 rounded-xl bg-[#821C17] text-[#FDF5E6] space-y-2">
                <div className="font-serif text-sm font-bold flex items-center justify-between">
                  <span>{activeDomainMeta.enName}</span>
                  <span className="text-xs font-mono font-bold bg-[#FDF5E6]/20 px-2 py-0.5 rounded">
                    {activeScore}%
                  </span>
                </div>
                <p className="text-[11px] text-[#FDF5E6]/80 leading-relaxed">
                  Synthesized through Lahiri Ayanamsa and Parashari Gochara transits for {fullName || 'Native'}.
                </p>
              </div>
            </div>
          </div>

          {/* ── Astro AI Assistant Chat ── */}
          <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] rounded-2xl space-y-4">
            <div className="flex items-center gap-2 pb-3 border-b border-[#F9DAB5]">
              <div className="p-2 rounded-lg bg-[#821C17] text-[#FDF5E6]">
                <Brain className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-serif text-lg font-bold text-[#821C17]">
                  {t.chatTitle}
                </h3>
                <p className="text-xs text-[#421A10]/70">
                  {t.chatSubtitle}
                </p>
              </div>
            </div>

            <div className="h-56 overflow-y-auto space-y-3 p-3 rounded-xl bg-[#FCEBD2]/40 border border-[#F9DAB5]">
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] sm:max-w-[75%] p-3 rounded-xl text-xs leading-relaxed ${
                      msg.sender === 'user'
                        ? 'bg-[#821C17] text-[#FDF5E6] rounded-br-xs'
                        : 'bg-[#FDF5E6] border border-[#F9DAB5] text-[#421A10] rounded-bl-xs shadow-2xs font-serif'
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {chatLoading && (
                <div className="flex justify-start">
                  <div className="bg-[#FDF5E6] border border-[#F9DAB5] p-3 rounded-xl text-xs text-[#C46B1E] flex items-center gap-2 font-serif">
                    <Sparkles className="w-3.5 h-3.5 animate-spin" />
                    <span>Synthesizing Vedic domain principles...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Quick Prompts */}
            <div className="flex gap-2 overflow-x-auto pb-1 text-[11px] scrollbar-none">
              {[
                `When is the best timing for ${activeDomainMeta.enName}?`,
                `What gemstone or mantra suits my ${activeDomainMeta.enName}?`,
                `How does my active Dasha affect my overall growth?`,
              ].map((qp, i) => (
                <button
                  key={i}
                  type="button"
                  onClick={() => handleSendChat(qp)}
                  className="px-3 py-1.5 rounded-lg bg-[#FCEBD2] hover:bg-[#F9DAB5] text-[#821C17] font-medium whitespace-nowrap transition-colors cursor-pointer border border-[#821C17]/20"
                >
                  {qp}
                </button>
              ))}
            </div>

            {/* Input Bar */}
            <div className="flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                placeholder={t.chatPlaceholder}
                className="flex-1 px-4 py-2.5 text-xs rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-[#421A10] placeholder-[#421A10]/40 focus:outline-none focus:ring-2 focus:ring-[#821C17]/40"
              />
              <button
                type="button"
                onClick={() => handleSendChat()}
                disabled={chatLoading}
                className="px-5 py-2.5 rounded-xl bg-[#821C17] text-[#FDF5E6] text-xs font-bold uppercase tracking-wider hover:brightness-110 active:scale-95 transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{t.sendBtn}</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Initial Encouragement State (Matches prediction.html placeholder) */
        <div className="sacred-card p-12 text-center bg-[#FDF5E6] border border-[#F9DAB5] rounded-2xl space-y-4">
          <div className="w-16 h-16 mx-auto rounded-full bg-[#821C17]/10 border border-[#821C17]/25 flex items-center justify-center text-[#821C17]">
            <Compass className="w-8 h-8 text-[#C46B1E]" />
          </div>
          <h3 className="font-serif text-2xl font-bold text-[#821C17]">
            10 Life Domains Ready for Parashari Analysis
          </h3>
          <p className="max-w-md mx-auto text-xs text-[#421A10]/75 leading-relaxed">
            Enter your exact birth date, time, and city above, or click{' '}
            <strong
              onClick={handleQuickSample}
              className="text-[#C46B1E] cursor-pointer underline underline-offset-2 hover:text-[#821C17]"
            >
              Use Sample Chart
            </strong>{' '}
            to explore Marriage, Career, Wealth, Health, Children, Education, Property, Challenges, Travel, and Spirituality.
          </p>
        </div>
      )}

      {/* ── Multilingual Prediction Report Language Selection Modal ── */}
      {isReportModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-xs animate-fadeIn">
          <div className="relative w-full max-w-lg rounded-2xl bg-[#FDF5E6] border-2 border-[#821C17] shadow-2xl p-6 text-[#421A10]">
            {/* Close button */}
            <button
              type="button"
              onClick={() => setIsReportModalOpen(false)}
              className="absolute top-4 right-4 p-1.5 rounded-full hover:bg-[#FCEBD2] text-[#821C17] transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            {/* Header */}
            <div className="flex items-center gap-3 mb-4 border-b border-[#821C17]/20 pb-4">
              <div className="p-2.5 rounded-xl bg-[#821C17] text-[#FDF5E6]">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-serif text-xl font-bold text-[#821C17]">
                  {locale === 'mr'
                    ? '१० जीवन पैलू अहवाल भाषा निवडा'
                    : locale === 'hi'
                    ? '१० जीवन आयाम रिपोर्ट की भाषा चुनें'
                    : 'Select Prediction Report Language'}
                </h3>
                <p className="text-xs text-[#421A10]/70">
                  {locale === 'mr'
                    ? 'आपल्या सर्व १० जीवन क्षेत्रांचा सखोल अहवाल कोणत्या भाषेत हवा आहे ते निवडा'
                    : locale === 'hi'
                    ? 'अपने समस्त १० जीवन क्षेत्रों की विस्तृत रिपोर्ट किस भाषा में प्राप्त करना चाहते हैं, चुनें'
                    : 'Choose the language for your comprehensive 10-domain Vedic dossier'}
                </p>
              </div>
            </div>

            {/* Language Selection Cards */}
            <div className="space-y-2.5 mb-6">
              {[
                {
                  id: 'en' as const,
                  flag: '🇬🇧',
                  title: 'English',
                  nativeTitle: 'English (10 Life Domain Dossier)',
                  desc: 'Comprehensive report in English with Sanskrit house designations, timing windows, and remedies.',
                },
                {
                  id: 'hi' as const,
                  flag: '🇮🇳',
                  title: 'हिन्दी (Hindi)',
                  nativeTitle: '१० जीवन आयाम सम्पूर्ण फलादेश',
                  desc: 'विवाह, आजीविका, धन, स्वास्थ्य, शिक्षा, संतान एवं ग्रह शांति उपायों सहित विस्तृत रिपोर्ट।',
                },
                {
                  id: 'mr' as const,
                  flag: '🚩',
                  title: 'मराठी (Marathi)',
                  nativeTitle: '१० जीवन पैलू सखोल भविष्य',
                  desc: 'विवाह, कारकीर्द, संपत्ती, आरोग्य, संतती, शिक्षण आणि सर्व वैदिक उपायांसह मराठीत सखोल अहवाल.',
                },
              ].map((option) => {
                const isSelected = selectedReportLang === option.id;
                return (
                  <div
                    key={option.id}
                    onClick={() => setSelectedReportLang(option.id)}
                    className={`p-3.5 rounded-xl border-2 cursor-pointer transition-all flex items-start gap-3.5 ${
                      isSelected
                        ? 'border-[#821C17] bg-[#FCEBD2] shadow-sm ring-1 ring-[#821C17]'
                        : 'border-[#821C17]/20 bg-white/70 hover:bg-[#FCEBD2]/50'
                    }`}
                  >
                    <div className="text-2xl pt-0.5">{option.flag}</div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-sm text-[#821C17]">{option.title}</span>
                        {isSelected && (
                          <span className="px-2 py-0.5 text-[10px] font-bold rounded-full bg-[#821C17] text-[#FDF5E6] flex items-center gap-1">
                            <Check className="w-3 h-3" /> Selected
                          </span>
                        )}
                      </div>
                      <div className="text-xs font-semibold text-[#421A10]">{option.nativeTitle}</div>
                      <div className="text-[11px] text-[#421A10]/70 mt-0.5 leading-snug">{option.desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-2.5 pt-2 border-t border-[#821C17]/20">
              <button
                type="button"
                onClick={() => {
                  handlePrintReport(selectedReportLang);
                  setIsReportModalOpen(false);
                }}
                className="flex-1 py-2.5 px-4 rounded-xl bg-linear-to-r from-[#821C17] via-[#C46B1E] to-[#821C17] text-[#FDF5E6] font-bold text-xs uppercase tracking-wider hover:brightness-105 active:scale-95 shadow-md flex items-center justify-center gap-2 cursor-pointer transition-all"
              >
                <Printer className="w-4 h-4" />
                <span>
                  {selectedReportLang === 'mr'
                    ? '🖨️ अहवाल उघडा व प्रिंट करा (PDF)'
                    : selectedReportLang === 'hi'
                    ? '🖨️ रिपोर्ट खोलें एवं प्रिंट करें (PDF)'
                    : '🖨️ Open & Print Report (PDF)'}
                </span>
              </button>

              <button
                type="button"
                onClick={() => {
                  handlePrintReport(selectedReportLang);
                  setIsReportModalOpen(false);
                }}
                className="py-2.5 px-4 rounded-xl bg-[#FCEBD2] hover:bg-[#F9DAB5] text-[#821C17] font-bold text-xs border border-[#821C17]/40 flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>
                  {selectedReportLang === 'mr'
                    ? 'PDF सेव्ह करा'
                    : selectedReportLang === 'hi'
                    ? 'PDF सुरक्षित करें'
                    : 'Save as PDF'}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

