'use client';

import React, { useState, useEffect, useTransition } from 'react';
import { useLocale } from 'next-intl';
import {
  Compass,
  Sparkles,
  Download,
  Calendar,
  Clock,
  MapPin,
  User,
  ShieldAlert,
  Award,
  Layers,
  Send,
  HelpCircle,
  ChevronRight,
  TrendingUp,
  Heart,
  Briefcase,
  Coins,
  Brain,
  Flame,
  CheckCircle2,
  AlertTriangle,
  Printer,
  FileText,
  Globe,
  X,
  Check,
  BookOpen,
  ChevronDown,
} from 'lucide-react';
import KundaliChart from './KundaliChart';
import { openPrintableKundaliReport, type ReportLanguage } from './kundaliReportGenerator';
import {
  KUNDALI_TRANSLATIONS,
  RASHI_NAMES_MAP,
  PLANET_NAMES_MAP,
  HOUSE_NAMES_DATA,
} from './kundaliLocalization';

export default function KundaliModule() {
  const locale = useLocale();
  const t = KUNDALI_TRANSLATIONS[locale] || KUNDALI_TRANSLATIONS.en;

  // Form State
  const [fullName, setFullName] = useState('');
  const [dob, setDob] = useState('1995-08-15');
  const [tob, setTob] = useState('14:30');
  const [city, setCity] = useState('Delhi');
  const [ayanamsa, setAyanamsa] = useState('Lahiri');

  // Autocomplete
  const [citiesList, setCitiesList] = useState<string[]>([]);
  const [citySuggestions, setCitySuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Chart Presentation & Active Tabs
  const [chartStyle, setChartStyle] = useState<'north' | 'south'>('north');
  const [activeVarga, setActiveVarga] = useState<'d1' | 'd9'>('d1');
  const [activeTab, setActiveTab] = useState<
    'overview' | 'charts' | 'planets' | 'strength' | 'yogas' | 'houses' | 'dasha' | 'chat'
  >('overview');
  const [selectedHouse, setSelectedHouse] = useState<number>(1);

  // Calculation Results
  const [loading, setLoading] = useState(false);
  const [chartData, setChartData] = useState<any>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  // Multilingual Report Generation State
  const [selectedReportLang, setSelectedReportLang] = useState<ReportLanguage>(
    ['en', 'hi', 'mr'].includes(locale) ? (locale as ReportLanguage) : 'en'
  );
  const [isReportModalOpen, setIsReportModalOpen] = useState(false);

  useEffect(() => {
    if (['en', 'hi', 'mr'].includes(locale)) {
      setSelectedReportLang(locale as ReportLanguage);
    }
  }, [locale]);

  // Chat State
  const [chatMessages, setChatMessages] = useState<Array<{ sender: 'user' | 'ai'; text: string }>>([
    {
      sender: 'ai',
      text: 'Namaste! I am your Vedic Astrology AI assistant. Feel free to ask about your ascendant, career indications, marriage timing, or planetary remedies.',
    },
  ]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Load cities on mount
  useEffect(() => {
    fetch('/api/cities')
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setCitiesList(data);
      })
      .catch(() => {});
  }, []);

  // Handle city input typing
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

  // Generate Kundali calculation
  const handleGenerate = async (e?: React.FormEvent) => {
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
      const res = await fetch('/api/kundali', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: fullName.trim() || 'Native',
          year,
          month,
          day,
          hour,
          minute,
          second: 0,
          city: city.trim(),
          ayanamsa,
        }),
      });

      const json = await res.json();
      if (res.ok && json.data) {
        setChartData(json.data);
      } else {
        setErrorMsg(json.message || 'Failed to compute Kundali.');
      }
    } catch (err: any) {
      setErrorMsg(err?.message || 'Connection error with ephemeris backend.');
    } finally {
      setLoading(false);
    }
  };

  // Quick Demo / Pre-fill sample profile
  const handleQuickSample = () => {
    setFullName('Arjun Sharma');
    setDob('1995-08-15');
    setTob('14:30');
    setCity('Delhi');
    setAyanamsa('Lahiri');
    setTimeout(() => {
      handleGenerate();
    }, 50);
  };

  // PDF Report Download (with language selection)
  const handleDownloadPdf = async (langOverride?: ReportLanguage) => {
    if (!chartData) return;
    const targetLang = langOverride || selectedReportLang;
    setDownloadingPdf(true);
    try {
      const chartId = chartData.chart_id || `${dob}_${tob}_${city}`;
      let res = await fetch('/api/download-kundali', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ chart: chartData, chart_id: chartId, lang: targetLang }),
      });

      if (!res.ok) {
        // Fallback to GET by chart_id
        const getUrl = `/api/download-kundali?chart_id=${encodeURIComponent(chartId)}&lang=${targetLang}`;
        res = await fetch(getUrl);
      }

      if (!res.ok) throw new Error('PDF generation failed on server');

      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const safeName = (fullName || 'Vedic').trim().replace(/[^a-zA-Z0-9_\u0900-\u097F]/g, '_');
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `Kundali_Report_${safeName}_${targetLang.toUpperCase()}.pdf`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (err: any) {
      alert('Could not download PDF report: ' + (err?.message || 'Server error'));
    } finally {
      setDownloadingPdf(false);
    }
  };

  // Printable Full Visual Report (matches app/templates/kundali.html)
  const handlePrintReport = (langOverride?: ReportLanguage) => {
    if (!chartData) return;
    const targetLang = langOverride || selectedReportLang;
    openPrintableKundaliReport({
      name: fullName || 'Native',
      dob,
      tob,
      city,
      chartData,
      chartStyle,
      reportLanguage: targetLang,
    });
  };

  // Generate and Open PDF Report (Auto-computes chart if not yet calculated)
  const handleGeneratePdfReport = async () => {
    if (chartData) {
      openPrintableKundaliReport({
        name: fullName || 'Native',
        dob,
        tob,
        city,
        chartData,
        chartStyle,
        reportLanguage: selectedReportLang,
      });
      return;
    }

    if (!dob || !tob || !city) {
      setErrorMsg('Please enter date of birth, time of birth, and city.');
      return;
    }

    setLoading(true);
    setErrorMsg(null);

    const [year, month, day] = dob.split('-').map(Number);
    const [hour, minute] = tob.split(':').map(Number);

    try {
      const res = await fetch('/api/kundali', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: fullName.trim() || 'Native',
          year,
          month,
          day,
          hour,
          minute,
          second: 0,
          city: city.trim(),
          ayanamsa,
        }),
      });

      const json = await res.json();
      if (res.ok && json.data) {
        setChartData(json.data);
        openPrintableKundaliReport({
          name: fullName || 'Native',
          dob,
          tob,
          city,
          chartData: json.data,
          chartStyle,
          reportLanguage: selectedReportLang,
        });
      } else {
        setErrorMsg(json.message || 'Failed to compute Kundali.');
      }
    } catch (err: any) {
      setErrorMsg(err?.message || 'Error communicating with cosmic ephemeris engine.');
    } finally {
      setLoading(false);
    }
  };

  // Send AI Chat Message
  const handleSendChat = async (questionText?: string) => {
    const text = questionText || chatInput;
    if (!text.trim() || chatLoading) return;

    const userMsg = { sender: 'user' as const, text };
    setChatMessages((prev) => [...prev, userMsg]);
    setChatInput('');
    setChatLoading(true);

    try {
      const res = await fetch('/api/kundali-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          chart: chartData || {},
        }),
      });
      const data = await res.json();
      const reply = data.reply || data.response || 'Classical analysis is aligned with your active planetary periods.';
      setChatMessages((prev) => [...prev, { sender: 'ai', text: reply }]);
    } catch {
      setChatMessages((prev) => [
        ...prev,
        {
          sender: 'ai',
          text: 'Vedic assessment indicates positive alignment with key Kendra houses. Consider chanting your Lagna lord Beej mantra during morning hours.',
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  // Compute Lagna Sign for charts
  const lagnaSign = chartData?.lagna || 'Mesha';
  const d1Houses = chartData?.houses || {};
  const d9Houses = chartData?.d9_houses || {};
  const currentHouses = activeVarga === 'd1' ? d1Houses : d9Houses;
  const currentPlanets = chartData?.planets || [];

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

      {/* ── Form Input Section Card (Faithfully matches target design) ── */}
      <div className="sacred-card p-6 sm:p-8 rounded-2xl shadow-sm">
        {/* Card Header: Pen/Sparkles + Title/Subtitle on Left, Use Sample Chart on Right */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 pb-5 border-b border-[#EADBC8] mb-6">
          <div className="flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-[#7A1612]/10 text-[#7A1612] border border-[#7A1612]/20 mt-0.5 shadow-2xs">
              <Sparkles className="w-5 h-5 text-[#7A1612]" />
            </div>
            <div>
              <h2 className="font-serif text-xl sm:text-2xl font-bold text-[#7A1612] tracking-tight">
                {t.inputCardTitle}
              </h2>
              <p className="text-xs text-[#24120B]/70 mt-0.5">
                {t.inputCardSubtitle}
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleQuickSample}
            className="self-start sm:self-center inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-[#7A1612] bg-[#FAF6F0] hover:bg-[#F5EFE6] border border-[#C5A059]/40 transition-all shadow-2xs hover:shadow-xs cursor-pointer active:scale-95"
          >
            <BookOpen className="w-4 h-4 text-[#A85A1E]" />
            <span>{t.sampleProfileBtn}</span>
          </button>
        </div>

        <form onSubmit={handleGenerate} className="space-y-6">
          {/* 4 Balanced Input Columns */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4.5">
            {/* Full Name */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#24120B]">
                {t.fullNameLabel}
              </label>
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A85A1E]" />
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder={t.fullNamePlaceholder}
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FAF6F0] border border-[#C5A059]/35 text-[#24120B] placeholder-[#24120B]/40 focus:outline-none focus:ring-2 focus:ring-[#7A1612]/20 transition-all"
                />
              </div>
            </div>

            {/* Date of Birth */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#24120B]">
                {t.dobLabel}
              </label>
              <div className="relative">
                <Calendar className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A85A1E]" />
                <input
                  type="date"
                  value={dob}
                  onChange={(e) => setDob(e.target.value)}
                  required
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FAF6F0] border border-[#C5A059]/35 text-[#24120B] focus:outline-none focus:ring-2 focus:ring-[#7A1612]/20 transition-all cursor-pointer"
                />
              </div>
            </div>

            {/* Time of Birth */}
            <div className="space-y-1.5">
              <label className="block text-xs font-semibold text-[#24120B]">
                {t.tobLabel}
              </label>
              <div className="relative">
                <Clock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A85A1E]" />
                <input
                  type="time"
                  value={tob}
                  onChange={(e) => setTob(e.target.value)}
                  required
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FAF6F0] border border-[#C5A059]/35 text-[#24120B] focus:outline-none focus:ring-2 focus:ring-[#7A1612]/20 transition-all cursor-pointer"
                />
              </div>
            </div>

            {/* Birth City Autocomplete */}
            <div className="space-y-1.5 relative">
              <label className="block text-xs font-semibold text-[#24120B]">
                {t.cityLabel}
              </label>
              <div className="relative">
                <MapPin className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-[#A85A1E]" />
                <input
                  type="text"
                  value={city}
                  onChange={handleCityChange}
                  onFocus={() => city.trim().length >= 2 && setShowSuggestions(true)}
                  placeholder={t.cityPlaceholder}
                  required
                  className="w-full pl-10 pr-3.5 py-2.5 text-sm rounded-xl bg-[#FAF6F0] border border-[#C5A059]/35 text-[#24120B] placeholder-[#24120B]/40 focus:outline-none focus:ring-2 focus:ring-[#7A1612]/20 transition-all"
                />
              </div>
              {/* Dropdown Suggestions */}
              {showSuggestions && citySuggestions.length > 0 && (
                <ul className="absolute z-30 left-0 right-0 top-[calc(100%+4px)] bg-[#FFFFFF] border border-[#C5A059]/40 rounded-xl shadow-xl max-h-48 overflow-y-auto divide-y divide-[#EADBC8]/60">
                  {citySuggestions.map((c) => (
                    <li
                      key={c}
                      onClick={() => {
                        setCity(c);
                        setShowSuggestions(false);
                      }}
                      className="px-4 py-2.5 text-xs text-[#24120B] hover:bg-[#F5EFE6] hover:text-[#7A1612] cursor-pointer transition-colors"
                    >
                      {c}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          {/* Centered Actions Below Inputs (Matches Image 1) */}
          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            {/* Primary Action Button */}
            <button
              type="submit"
              disabled={loading}
              className="py-3 px-8 rounded-xl bg-linear-to-r from-[#7A1612] via-[#94271F] to-[#7A1612] text-[#FAF6F0] font-bold text-sm shadow-md hover:brightness-110 active:scale-98 transition-all disabled:opacity-50 flex items-center justify-center gap-2.5 cursor-pointer min-w-[200px] border border-[#C5A059]/40"
            >
              <Sparkles className="w-4 h-4 text-[#F5E1BE]" />
              <span>{loading ? t.generatingBtn : t.generateBtn}</span>
            </button>

            {/* Secondary Action: Split Dropdown Button for PDF Report */}
            <div className="inline-flex rounded-xl shadow-xs bg-[#F5EFE6] border border-[#C5A059]/40 hover:border-[#7A1612]/60 transition-all overflow-hidden group">
              <button
                type="button"
                onClick={handleGeneratePdfReport}
                title="Generate and print full visual Vedic Kundali report"
                className="py-3 pl-5 pr-3 text-sm font-bold text-[#7A1612] hover:bg-[#EADBC8] flex items-center gap-2 cursor-pointer transition-colors"
              >
                <FileText className="w-4 h-4 text-[#7A1612]" />
                <span>{t.generatePdfReportBtn}</span>
              </button>
              <div className="w-px bg-[#C5A059]/30 self-stretch my-2" />
              <button
                type="button"
                onClick={() => setIsReportModalOpen(true)}
                title="Select language and format for Kundali report"
                className="py-3 px-3.5 text-[#7A1612] hover:bg-[#EADBC8] flex items-center justify-center cursor-pointer transition-colors"
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
      {chartData ? (
        <div className="space-y-8 animate-fadeIn">
          {/* Navigation Sub-Tabs */}
          <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-[#EADBC8]">
            {[
              { id: 'overview', label: t.tabOverview, icon: Compass },
              { id: 'charts', label: t.tabCharts, icon: Layers },
              { id: 'planets', label: t.tabPlanets, icon: Award },
              { id: 'strength', label: t.tabStrength, icon: TrendingUp },
              { id: 'yogas', label: t.tabYogasDoshas, icon: Flame },
              { id: 'houses', label: t.tabHouses, icon: MapPin },
              { id: 'dasha', label: t.tabDasha, icon: Calendar },
              { id: 'chat', label: t.tabChat, icon: Brain },
            ].map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold tracking-wide uppercase transition-all whitespace-nowrap cursor-pointer ${
                    isActive
                      ? 'bg-[#7A1612] text-[#FAF6F0] shadow-sm border border-[#C5A059]/40'
                      : 'bg-[#F5EFE6] text-[#24120B]/80 hover:text-[#7A1612] hover:bg-[#EADBC8] border border-[#EADBC8]'
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>

          {/* TAB 1: OVERVIEW & BIRTH DETAILS */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Full Report Printable Banner (Matches Old Template Report) */}
              <div className="p-4 sm:p-5 rounded-xl bg-linear-to-r from-[#821C17] to-[#C46B1E] text-[#FDF5E6] flex flex-wrap items-center justify-between gap-4 shadow-sm">
                <div className="space-y-1.5">
                  <div className="flex items-center gap-2 font-serif text-base font-bold">
                    <FileText className="w-5 h-5 text-[#F3C387]" />
                    <span>
                      {locale === 'mr'
                        ? 'संपूर्ण वैदिक जन्म पत्रिका अहवाल (मूळ फॉरमॅट)'
                        : locale === 'hi'
                        ? 'सम्पूर्ण वैदिक जन्म पत्रिका अहवाल (मूल प्रारूप)'
                        : 'Complete Vedic Kundali Report (Original Template Layout)'}
                    </span>
                  </div>
                  <p className="text-xs text-[#FDF5E6]/80 max-w-xl">
                    {locale === 'mr'
                      ? 'D1 आणि D9 कुंडली, नवग्रह स्थिती, बारा भाव, योग, दोष निवारण उपाय आणि विंशोत्तरी महादशेसह मुद्रणयोग्य अहवाल.'
                      : locale === 'hi'
                      ? 'D1 एवं D9 कुंडली, नवग्रह स्पष्ट, द्वादश भाव, योग, दोष निवारण उपाय एवं विंशोत्तरी महादशा सहित सम्पूर्ण जन्म पत्रिका।'
                      : 'Generate the full printable birth chart dossier with D1 & D9 charts, Navagraha table, all 12 Bhavas, yogas, doshas, remedies, and Vimshottari dasha.'}
                  </p>
                  {/* Language Selector pills inside banner */}
                  <div className="flex items-center gap-2 pt-1 text-xs flex-wrap">
                    <span className="text-[#FDF5E6]/75 flex items-center gap-1 font-semibold text-[11px]">
                      <Globe className="w-3.5 h-3.5" />
                      {locale === 'mr' ? 'अहवाल भाषा:' : locale === 'hi' ? 'रिपोर्ट भाषा:' : 'Report Language:'}
                    </span>
                    {(['en', 'hi', 'mr'] as const).map((l) => (
                      <button
                        key={l}
                        type="button"
                        onClick={() => setSelectedReportLang(l)}
                        className={`px-2.5 py-0.5 rounded text-[11px] font-bold transition-all cursor-pointer ${
                          selectedReportLang === l
                            ? 'bg-[#FDF5E6] text-[#821C17] shadow-xs'
                            : 'bg-black/20 text-[#FDF5E6]/80 hover:bg-black/30'
                        }`}
                      >
                        {l === 'en' ? '🇬🇧 English' : l === 'hi' ? '🇮🇳 हिन्दी' : '🚩 मराठी'}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-2 flex-wrap">
                  <button
                    type="button"
                    onClick={() => handlePrintReport(selectedReportLang)}
                    className="px-4 py-2 rounded-lg bg-[#FDF5E6] text-[#821C17] font-bold text-xs uppercase tracking-wider hover:bg-[#FCEBD2] shadow-sm flex items-center gap-1.5 transition-all cursor-pointer"
                  >
                    <Printer className="w-4 h-4" />
                    <span>
                      {selectedReportLang === 'mr'
                        ? 'प्रिंट अहवाल (मराठी)'
                        : selectedReportLang === 'hi'
                        ? 'प्रिंट रिपोर्ट (हिन्दी)'
                        : 'Print Report (PDF)'}
                    </span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsReportModalOpen(true)}
                    className="px-3 py-2 rounded-lg bg-[#FDF5E6]/15 hover:bg-[#FDF5E6]/25 text-[#FDF5E6] font-semibold text-xs border border-[#FDF5E6]/30 flex items-center gap-1.5 transition-all cursor-pointer"
                    title="Change Language & Download Options"
                  >
                    <Globe className="w-4 h-4" />
                    <span>{locale === 'mr' ? 'भाषा पर्याय' : locale === 'hi' ? 'भाषा विकल्प' : 'Language Options'}</span>
                  </button>
                </div>
              </div>

              <div className="sacred-card p-6 sm:p-8 bg-[#FDF5E6] border border-[#F9DAB5]">
                <div className="flex items-center justify-between pb-4 border-b border-[#F9DAB5] mb-6">
                  <h3 className="font-serif text-lg font-bold text-[#821C17]">
                    {t.birthDetailsTitle}
                  </h3>
                  <span className="text-xs font-mono px-2 py-0.5 rounded-sm bg-[#C46B1E]/10 border border-[#C46B1E]/30 text-[#C46B1E]">
                    LA SUID: {chartData.chart_id || 'VERIFIED'}
                  </span>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                  {[
                    { label: t.name, val: fullName || 'Native' },
                    { label: t.dob, val: chartData.birth_date || dob },
                    { label: t.tob, val: `${chartData.birth_hour || 14}:${chartData.birth_minute || 30} IST` },
                    { label: t.birthPlace, val: city },
                    { label: t.lagna, val: `${chartData.lagna} (${RASHI_NAMES_MAP[chartData.lagna]?.hi || ''})`, highlight: true },
                    { label: t.lagnaDegree, val: chartData.lagna_degree || '—' },
                    { label: t.moonSign, val: chartData.planets?.find((p: any) => p.name === 'Moon')?.sign || '—' },
                    { label: t.nakshatra, val: `${chartData.nakshatra || '—'} (Pada ${chartData.nakshatra_pada || 1})` },
                    { label: t.tithi, val: `${chartData.paksha || ''} ${chartData.tithi_name || '—'}` },
                    { label: t.yoga, val: chartData.yoga_name || '—' },
                    { label: t.karana, val: chartData.karana_name || '—' },
                    { label: t.dashaBalance, val: chartData.dasha_balance || '—', highlight: true },
                  ].map((item, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-[#FCEBD2]/60 border border-[#F9DAB5]/60 space-y-1">
                      <div className="text-[10.5px] uppercase font-semibold tracking-wider text-[#421A10]/60">
                        {item.label}
                      </div>
                      <div className={`text-sm font-bold ${item.highlight ? 'text-[#821C17]' : 'text-[#421A10]'}`}>
                        {item.val}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Quick Preview of Charts and Strength */}
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
                <div className="lg:col-span-7 sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5]">
                  <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#F9DAB5]">
                    <span className="font-serif text-base font-bold text-[#821C17]">
                      {t.d1Title}
                    </span>
                    <button
                      onClick={() => setActiveTab('charts')}
                      className="text-xs font-semibold text-[#C46B1E] hover:underline"
                    >
                      Inspect in Full View →
                    </button>
                  </div>
                  <KundaliChart
                    style={chartStyle}
                    varga="d1"
                    lagnaSign={lagnaSign}
                    housesData={d1Houses}
                    planets={currentPlanets}
                    selectedHouse={selectedHouse}
                    onSelectHouse={setSelectedHouse}
                  />
                </div>

                <div className="lg:col-span-5 sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between pb-3 mb-4 border-b border-[#F9DAB5]">
                      <span className="font-serif text-base font-bold text-[#821C17]">
                        {t.strengthTitle}
                      </span>
                      <button
                        onClick={() => setActiveTab('strength')}
                        className="text-xs font-semibold text-[#C46B1E] hover:underline"
                      >
                        All Details →
                      </button>
                    </div>

                    <div className="space-y-3">
                      {[
                        { key: 'overall_strength', label: t.overall, icon: Sparkles, color: '#821C17' },
                        { key: 'career_score', label: t.career, icon: Briefcase, color: '#C46B1E' },
                        { key: 'finance_score', label: t.finance, icon: Coins, color: '#15803D' },
                        { key: 'marriage_score', label: t.relationship, icon: Heart, color: '#DB2777' },
                        { key: 'spirituality_score', label: t.spiritual, icon: Brain, color: '#9333EA' },
                      ].map((s) => {
                        const val = chartData.scores?.[s.key] || 60;
                        const Icon = s.icon;
                        return (
                          <div key={s.key} className="space-y-1">
                            <div className="flex justify-between text-xs font-semibold">
                              <span className="flex items-center gap-1.5 text-[#421A10]">
                                <Icon className="w-3.5 h-3.5" style={{ color: s.color }} />
                                {s.label}
                              </span>
                              <span className="font-mono text-[#821C17]">{val}%</span>
                            </div>
                            <div className="h-2 w-full bg-[#FCEBD2] rounded-full overflow-hidden border border-[#F9DAB5]">
                              <div
                                className="h-full rounded-full transition-all duration-1000"
                                style={{ width: `${val}%`, backgroundColor: s.color }}
                              />
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>

                  <div className="mt-6 pt-4 border-t border-[#F9DAB5] flex items-center justify-between text-xs text-[#421A10]/70">
                    <span>Active Mahadasha: <strong className="text-[#821C17]">{chartData.mahadasha}</strong></span>
                    <span>Remaining: <strong>{chartData.dasha_balance}</strong></span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: VEDIC CHARTS (D1 & D9) */}
          {activeTab === 'charts' && (
            <div className="space-y-6">
              {/* Controls Bar */}
              <div className="sacred-card p-4 bg-[#FDF5E6] border border-[#F9DAB5] flex flex-wrap items-center justify-between gap-4">
                <div className="inline-flex p-1 rounded-lg bg-[#FCEBD2] border border-[#F9DAB5]">
                  <button
                    onClick={() => setActiveVarga('d1')}
                    className={`px-4 py-1.5 text-xs font-bold rounded-md transition-all ${
                      activeVarga === 'd1'
                        ? 'bg-[#821C17] text-[#FDF5E6] shadow-xs'
                        : 'text-[#421A10]/70 hover:text-[#821C17]'
                    }`}
                  >
                    {t.d1Title}
                  </button>
                  <button
                    onClick={() => setActiveVarga('d9')}
                    className={`px-4 py-1.5 text-xs font-bold rounded-md transition-all ${
                      activeVarga === 'd9'
                        ? 'bg-[#821C17] text-[#FDF5E6] shadow-xs'
                        : 'text-[#421A10]/70 hover:text-[#821C17]'
                    }`}
                  >
                    {t.d9Title}
                  </button>
                </div>

                <div className="inline-flex items-center gap-2">
                  <span className="text-xs font-semibold text-[#421A10]/70">{t.chartStyle}:</span>
                  <div className="inline-flex p-1 rounded-lg bg-[#FCEBD2] border border-[#F9DAB5]">
                    <button
                      onClick={() => setChartStyle('north')}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                        chartStyle === 'north'
                          ? 'bg-[#C46B1E] text-[#FDF5E6]'
                          : 'text-[#421A10]/70 hover:text-[#821C17]'
                      }`}
                    >
                      {t.northIndian}
                    </button>
                    <button
                      onClick={() => setChartStyle('south')}
                      className={`px-3 py-1 text-xs font-semibold rounded-md transition-all ${
                        chartStyle === 'south'
                          ? 'bg-[#C46B1E] text-[#FDF5E6]'
                          : 'text-[#421A10]/70 hover:text-[#821C17]'
                      }`}
                    >
                      {t.southIndian}
                    </button>
                  </div>
                </div>
              </div>

              {/* Main Dual Chart Display */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* D1 Rashi Chart */}
                <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] text-center space-y-3">
                  <div className="pb-3 border-b border-[#F9DAB5]">
                    <h4 className="font-serif text-lg font-bold text-[#821C17]">{t.d1Title}</h4>
                    <p className="text-xs text-[#421A10]/60">{t.d1Subtitle}</p>
                  </div>
                  <KundaliChart
                    style={chartStyle}
                    varga="d1"
                    lagnaSign={lagnaSign}
                    housesData={d1Houses}
                    planets={currentPlanets}
                    selectedHouse={selectedHouse}
                    onSelectHouse={setSelectedHouse}
                  />
                </div>

                {/* D9 Navamsha Chart */}
                <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] text-center space-y-3">
                  <div className="pb-3 border-b border-[#F9DAB5]">
                    <h4 className="font-serif text-lg font-bold text-[#821C17]">{t.d9Title}</h4>
                    <p className="text-xs text-[#421A10]/60">{t.d9Subtitle}</p>
                  </div>
                  <KundaliChart
                    style={chartStyle}
                    varga="d9"
                    lagnaSign={chartData.d9_lagna || lagnaSign}
                    housesData={d9Houses}
                    planets={currentPlanets}
                    selectedHouse={selectedHouse}
                    onSelectHouse={setSelectedHouse}
                  />
                </div>
              </div>

              {/* Selected House Quick Inspector */}
              {selectedHouse && (
                <div className="sacred-card p-5 bg-[#FCEBD2] border border-[#821C17]/20 flex flex-wrap items-center justify-between gap-4">
                  <div className="space-y-1">
                    <span className="text-xs uppercase font-bold text-[#821C17]">
                      Inspected: {HOUSE_NAMES_DATA[selectedHouse]?.enName} ({HOUSE_NAMES_DATA[selectedHouse]?.sanskritName})
                    </span>
                    <p className="text-xs text-[#421A10]/80">
                      {locale === 'hi'
                        ? HOUSE_NAMES_DATA[selectedHouse]?.hiDesc
                        : locale === 'mr'
                        ? HOUSE_NAMES_DATA[selectedHouse]?.mrDesc
                        : HOUSE_NAMES_DATA[selectedHouse]?.enDesc}
                    </p>
                  </div>
                  <div className="text-xs font-semibold text-[#C46B1E]">
                    Occupants: <strong>{currentHouses[selectedHouse]?.join(', ') || 'None (Empty Bhava)'}</strong>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: NAVAGRAHA TABLE */}
          {activeTab === 'planets' && (
            <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] space-y-4">
              <div className="pb-3 border-b border-[#F9DAB5]">
                <h3 className="font-serif text-lg font-bold text-[#821C17]">{t.planetsTitle}</h3>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full border-collapse text-left text-xs">
                  <thead>
                    <tr className="bg-[#FCEBD2] text-[#821C17] border-b border-[#F9DAB5] uppercase tracking-wider font-semibold">
                      <th className="py-3 px-3">{t.colPlanet}</th>
                      <th className="py-3 px-3">{t.colSign}</th>
                      <th className="py-3 px-3">{t.colDegree}</th>
                      <th className="py-3 px-3">{t.colHouse}</th>
                      <th className="py-3 px-3">{t.colNakshatra}</th>
                      <th className="py-3 px-3">{t.colPada}</th>
                      <th className="py-3 px-3">{t.colNavamsa}</th>
                      <th className="py-3 px-3">{t.colDignity}</th>
                      <th className="py-3 px-3">{t.colStatus}</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#F9DAB5]/60">
                    {currentPlanets.map((p: any) => {
                      const isRetro = p.retrograde;
                      const planetObj = PLANET_NAMES_MAP[p.name];
                      const rashiObj = RASHI_NAMES_MAP[p.sign];

                      return (
                        <tr key={p.name} className="hover:bg-[#FCEBD2]/50 transition-colors">
                          <td className="py-3 px-3 font-bold text-[#821C17] flex items-center gap-1.5">
                            <span>{planetObj?.symbol || '✦'}</span>
                            <span>{planetObj?.en || p.name}</span>
                          </td>
                          <td className="py-3 px-3 font-semibold text-[#421A10]">
                            {p.sign} {rashiObj ? `(${rashiObj.hi || ''})` : ''}
                          </td>
                          <td className="py-3 px-3 font-mono text-[#C46B1E]">{p.degree}</td>
                          <td className="py-3 px-3 font-bold text-center">
                            <span className="w-6 h-6 rounded-full bg-[#821C17]/10 text-[#821C17] inline-flex items-center justify-center">
                              {p.house}
                            </span>
                          </td>
                          <td className="py-3 px-3 text-[#421A10]">{p.nakshatra}</td>
                          <td className="py-3 px-3 text-center">{p.pada}</td>
                          <td className="py-3 px-3 font-serif font-semibold">{p.navamsa || '—'}</td>
                          <td className="py-3 px-3">
                            <span className="px-2 py-0.5 rounded-sm bg-[#C46B1E]/10 border border-[#C46B1E]/30 text-[#C46B1E] font-semibold text-[11px]">
                              {p.strength || 'Neutral'}
                            </span>
                          </td>
                          <td className="py-3 px-3">
                            {isRetro ? (
                              <span className="px-2 py-0.5 rounded-sm bg-amber-100 text-amber-900 border border-amber-300 font-bold">
                                {t.retrograde}
                              </span>
                            ) : (
                              <span className="px-2 py-0.5 rounded-sm bg-green-100 text-green-900 border border-green-300 font-medium">
                                {t.direct}
                              </span>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: CHART STRENGTH (BHAVA BALA & DOMAIN POTENCY) */}
          {activeTab === 'strength' && (
            <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] space-y-6">
              <div className="pb-3 border-b border-[#F9DAB5]">
                <h3 className="font-serif text-lg font-bold text-[#821C17]">{t.strengthTitle}</h3>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {[
                  { key: 'overall_strength', label: t.overall, icon: Sparkles, color: '#821C17', desc: 'Holistic ascendant & planetary vigor' },
                  { key: 'career_score', label: t.career, icon: Briefcase, color: '#C46B1E', desc: '10th house authority and profession' },
                  { key: 'finance_score', label: t.finance, icon: Coins, color: '#15803D', desc: 'Dhana and Labha wealth accumulations' },
                  { key: 'marriage_score', label: t.relationship, icon: Heart, color: '#DB2777', desc: '7th house partnership harmony' },
                  { key: 'health_score', label: t.health, icon: Award, color: '#DC2626', desc: 'Immunity and vitality longevity' },
                  { key: 'mental_score', label: t.mental, icon: Brain, color: '#9333EA', desc: 'Moon peace of mind and emotional stability' },
                  { key: 'spirituality_score', label: t.spiritual, icon: Compass, color: '#F59E0B', desc: '9th/12th house dharma and moksha' },
                ].map((s) => {
                  const val = chartData.scores?.[s.key] || 60;
                  const Icon = s.icon;
                  return (
                    <div key={s.key} className="p-5 rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="font-serif text-sm font-bold text-[#821C17] flex items-center gap-2">
                          <Icon className="w-4 h-4" style={{ color: s.color }} />
                          {s.label}
                        </span>
                        <span className="text-lg font-bold font-mono text-[#821C17]">{val}%</span>
                      </div>
                      <div className="h-2.5 w-full bg-[#FDF5E6] rounded-full overflow-hidden border border-[#F9DAB5]">
                        <div
                          className="h-full rounded-full transition-all duration-1000"
                          style={{ width: `${val}%`, backgroundColor: s.color }}
                        />
                      </div>
                      <p className="text-[11px] text-[#421A10]/70">{s.desc}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* TAB 5: YOGAS & DOSHAS */}
          {activeTab === 'yogas' && (
            <div className="space-y-8">
              {/* Yogas Section */}
              <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] space-y-4">
                <div className="pb-3 border-b border-[#F9DAB5] flex items-center justify-between">
                  <div>
                    <h3 className="font-serif text-lg font-bold text-[#821C17]">{t.yogasTitle}</h3>
                    <p className="text-xs text-[#421A10]/70">{t.yogasSubtitle}</p>
                  </div>
                  <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-green-100 text-green-900 border border-green-300">
                    {chartData.yogas?.filter((y: any) => y.present).length || 0} {t.activeYogasCount}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {chartData.yogas?.filter((y: any) => y.present).length > 0 ? (
                    chartData.yogas
                      .filter((y: any) => y.present)
                      .map((y: any, idx: number) => (
                        <div key={idx} className="p-4 rounded-xl bg-[#FCEBD2] border-l-4 border-[#15803D] space-y-2">
                          <div className="flex items-center justify-between">
                            <h5 className="font-serif text-sm font-bold text-[#15803D]">{y.name}</h5>
                            <span className="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-[#15803D]/10 text-[#15803D] font-bold">
                              {y.strength || 'ACTIVE'}
                            </span>
                          </div>
                          <p className="text-xs text-[#421A10]/80 leading-relaxed">{y.description}</p>
                          {y.source_reference && (
                            <span className="block text-[10px] text-[#421A10]/50 italic">Ref: {y.source_reference}</span>
                          )}
                        </div>
                      ))
                  ) : (
                    <div className="col-span-2 text-center py-8 text-xs text-[#421A10]/60">
                      {t.noYogas}
                    </div>
                  )}
                </div>
              </div>

              {/* Doshas & Vedic Remedies */}
              <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] space-y-4">
                <div className="pb-3 border-b border-[#F9DAB5]">
                  <h3 className="font-serif text-lg font-bold text-[#821C17]">{t.doshasTitle}</h3>
                  <p className="text-xs text-[#421A10]/70">{t.doshasSubtitle}</p>
                </div>

                <div className="space-y-4">
                  {chartData.doshas?.map((d: any, idx: number) => {
                    const isSevere = d.severity === 'High';
                    const isMod = d.severity === 'Moderate';
                    const borderColor = isSevere ? '#DC2626' : isMod ? '#C46B1E' : '#15803D';
                    const badgeClass = isSevere
                      ? 'bg-red-100 text-red-900 border-red-300'
                      : isMod
                      ? 'bg-amber-100 text-amber-900 border-amber-300'
                      : 'bg-green-100 text-green-900 border-green-300';

                    return (
                      <div key={idx} className="p-4 rounded-xl bg-[#FCEBD2] border-l-4 space-y-2.5" style={{ borderColor }}>
                        <div className="flex items-center justify-between">
                          <h5 className="font-serif text-sm font-bold text-[#421A10]">{d.name}</h5>
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-sm border ${badgeClass}`}>
                            {d.severity === 'High' ? t.severityHigh : d.severity === 'Moderate' ? t.severityModerate : t.severityNone}
                          </span>
                        </div>
                        <p className="text-xs text-[#421A10]/80 leading-relaxed">{d.description}</p>

                        {/* Actionable Remedies */}
                        {d.remedies && d.remedies.length > 0 && (
                          <div className="pt-2 border-t border-[#F9DAB5]/80 space-y-1">
                            <span className="text-[11px] font-bold text-[#821C17] uppercase tracking-wider block">
                              {t.remediesTitle}:
                            </span>
                            <ul className="list-disc list-inside text-xs text-[#421A10]/80 space-y-0.5">
                              {d.remedies.map((rem: string, rIdx: number) => (
                                <li key={rIdx}>{rem}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 6: 12 BHAVAS EXPLORER */}
          {activeTab === 'houses' && (
            <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] space-y-6">
              <div className="pb-3 border-b border-[#F9DAB5]">
                <h3 className="font-serif text-lg font-bold text-[#821C17]">{t.housesTitle}</h3>
                <p className="text-xs text-[#421A10]/70">{t.housesSubtitle}</p>
              </div>

              {/* 12 House Buttons */}
              <div className="grid grid-cols-4 sm:grid-cols-6 lg:grid-cols-12 gap-2">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((h) => (
                  <button
                    key={h}
                    onClick={() => setSelectedHouse(h)}
                    className={`py-2 px-1 rounded-lg text-xs font-bold transition-all ${
                      selectedHouse === h
                        ? 'bg-[#821C17] text-[#FDF5E6] shadow-xs'
                        : 'bg-[#FCEBD2] text-[#421A10] hover:bg-[#F9DAB5]'
                    }`}
                  >
                    H{h}
                  </button>
                ))}
              </div>

              {/* House Details Panel */}
              {selectedHouse && (
                <div className="p-6 rounded-2xl bg-[#FCEBD2] border border-[#821C17]/25 space-y-4">
                  <div className="flex items-center justify-between pb-3 border-b border-[#F9DAB5]">
                    <div>
                      <h4 className="font-serif text-xl font-bold text-[#821C17]">
                        {HOUSE_NAMES_DATA[selectedHouse]?.enName} — {HOUSE_NAMES_DATA[selectedHouse]?.sanskritName}
                      </h4>
                      <p className="text-xs text-[#421A10]/80 mt-1">
                        {locale === 'hi'
                          ? HOUSE_NAMES_DATA[selectedHouse]?.hiDesc
                          : locale === 'mr'
                          ? HOUSE_NAMES_DATA[selectedHouse]?.mrDesc
                          : HOUSE_NAMES_DATA[selectedHouse]?.enDesc}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 pt-2">
                    <div className="p-3 rounded-lg bg-[#FDF5E6] border border-[#F9DAB5]">
                      <span className="text-[10px] uppercase font-bold text-[#C46B1E] block mb-1">
                        {t.houseOccupants}
                      </span>
                      <strong className="text-sm text-[#421A10]">
                        {currentHouses[selectedHouse]?.filter((p: string) => p !== 'Lagna').join(', ') || 'Empty Bhava'}
                      </strong>
                    </div>

                    <div className="p-3 rounded-lg bg-[#FDF5E6] border border-[#F9DAB5]">
                      <span className="text-[10px] uppercase font-bold text-[#C46B1E] block mb-1">
                        {t.houseKaraka}
                      </span>
                      <strong className="text-sm text-[#421A10]">
                        {HOUSE_NAMES_DATA[selectedHouse]?.karaka}
                      </strong>
                    </div>

                    <div className="p-3 rounded-lg bg-[#FDF5E6] border border-[#F9DAB5]">
                      <span className="text-[10px] uppercase font-bold text-[#C46B1E] block mb-1">
                        {t.houseSign}
                      </span>
                      <strong className="text-sm text-[#821C17]">
                        Rashi {((RASHI_NAMES_MAP[lagnaSign]?.num || 1) + selectedHouse - 2) % 12 + 1}
                      </strong>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 7: VIMSHOTTARI DASHA */}
          {activeTab === 'dasha' && (
            <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] space-y-6">
              <div className="pb-3 border-b border-[#F9DAB5]">
                <h3 className="font-serif text-lg font-bold text-[#821C17]">{t.dashaTitle}</h3>
              </div>

              {/* Current Dasha Highlights */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-center space-y-1">
                  <span className="text-[11px] uppercase font-semibold text-[#421A10]/60">{t.currentMahadasha}</span>
                  <div className="font-serif text-2xl font-bold text-[#821C17]">{chartData.mahadasha}</div>
                </div>
                <div className="p-4 rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-center space-y-1">
                  <span className="text-[11px] uppercase font-semibold text-[#421A10]/60">{t.currentAntardasha}</span>
                  <div className="font-serif text-2xl font-bold text-[#C46B1E]">{chartData.antardasha || '—'}</div>
                </div>
                <div className="p-4 rounded-xl bg-[#FCEBD2] border border-[#F9DAB5] text-center space-y-1">
                  <span className="text-[11px] uppercase font-semibold text-[#421A10]/60">{t.balanceRemaining}</span>
                  <div className="font-serif text-2xl font-bold text-[#15803D]">{chartData.dasha_balance || '—'}</div>
                </div>
              </div>

              {/* 120-Year Mahadasha Timeline */}
              <div className="space-y-3 pt-4">
                <h4 className="font-serif text-sm font-bold text-[#421A10] uppercase tracking-wider">
                  {t.dashaTimelineTitle}
                </h4>
                <div className="space-y-2">
                  {chartData.dasha?.timeline?.map((item: any, idx: number) => {
                    const isCurrent = item.lord === chartData.mahadasha;
                    return (
                      <div
                        key={idx}
                        className={`p-3 rounded-lg border flex items-center justify-between text-xs transition-colors ${
                          isCurrent
                            ? 'bg-[#821C17]/10 border-[#821C17] text-[#821C17] font-bold shadow-xs'
                            : 'bg-[#FCEBD2]/50 border-[#F9DAB5] text-[#421A10]'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <span className="w-6 h-6 rounded-full bg-[#821C17]/10 flex items-center justify-center font-serif text-[11px] font-bold text-[#821C17]">
                            {idx + 1}
                          </span>
                          <span className="font-serif text-sm">{item.lord} Mahadasha</span>
                          {isCurrent && (
                            <span className="px-2 py-0.5 rounded-sm bg-[#821C17] text-[#FDF5E6] text-[10px] font-sans font-bold">
                              ACTIVE
                            </span>
                          )}
                        </div>
                        <span className="font-mono text-[#C46B1E]">{item.years} {t.dashaYears}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* TAB 8: CONTEXTUAL ASTRO AI CHAT */}
          {activeTab === 'chat' && (
            <div className="sacred-card p-6 bg-[#FDF5E6] border border-[#F9DAB5] space-y-4">
              <div className="pb-3 border-b border-[#F9DAB5]">
                <h3 className="font-serif text-lg font-bold text-[#821C17]">{t.chatTitle}</h3>
                <p className="text-xs text-[#421A10]/70">{t.chatSubtitle}</p>
              </div>

              {/* Sample Prompts */}
              <div className="flex flex-wrap gap-2">
                {[t.sampleQuestion1, t.sampleQuestion2, t.sampleQuestion3].map((q, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSendChat(q)}
                    className="text-xs px-3 py-1.5 rounded-full bg-[#FCEBD2] border border-[#F9DAB5] text-[#421A10] hover:text-[#821C17] hover:bg-[#F9DAB5] transition-all"
                  >
                    ✦ {q}
                  </button>
                ))}
              </div>

              {/* Chat Message Box */}
              <div className="h-72 overflow-y-auto p-4 rounded-xl bg-[#FCEBD2]/50 border border-[#F9DAB5] space-y-3">
                {chatMessages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] p-3 rounded-xl text-xs leading-relaxed ${
                        msg.sender === 'user'
                          ? 'bg-[#821C17] text-[#FDF5E6] rounded-br-none'
                          : 'bg-[#FDF5E6] text-[#421A10] border border-[#F9DAB5] rounded-bl-none shadow-xs'
                      }`}
                    >
                      {msg.text}
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="p-3 rounded-xl bg-[#FDF5E6] border border-[#F9DAB5] text-xs text-[#C46B1E] flex items-center gap-2">
                      <Sparkles className="w-3.5 h-3.5 animate-spin" />
                      <span>Consulting classical astrological rules...</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Input & Send */}
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSendChat()}
                  placeholder={t.chatPlaceholder}
                  className="flex-1 px-4 py-2 text-xs rounded-lg bg-[#FCEBD2] border border-[#F9DAB5] text-[#421A10] placeholder-[#421A10]/40 focus:outline-none focus:ring-2 focus:ring-[#821C17]/40"
                />
                <button
                  type="button"
                  onClick={() => handleSendChat()}
                  disabled={chatLoading}
                  className="px-5 py-2 rounded-lg bg-[#821C17] text-[#FDF5E6] text-xs font-bold uppercase tracking-wider hover:brightness-110 active:scale-95 transition-all flex items-center gap-1.5"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{t.sendBtn}</span>
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Empty State / Initial Encouragement */
        <div className="sacred-card p-10 text-center bg-[#FDF5E6] border border-[#F9DAB5] space-y-4">
          <div className="w-14 h-14 mx-auto rounded-full bg-[#821C17]/10 border border-[#821C17]/25 flex items-center justify-center text-[#821C17]">
            <Compass className="w-7 h-7 text-[#C46B1E]" />
          </div>
          <h3 className="font-serif text-xl font-bold text-[#821C17]">
            Vedic Ephemeris Ready for Calculation
          </h3>
          <p className="max-w-md mx-auto text-xs text-[#421A10]/70 leading-relaxed">
            Enter your date, exact time, and city of birth above or click{' '}
            <strong
              onClick={handleQuickSample}
              className="text-[#C46B1E] cursor-pointer underline underline-offset-2"
            >
              Quick Sample Chart
            </strong>{' '}
            to explore D1 &amp; D9 charts, planetary longitudes, Vimshottari dasha, and active yogas.
          </p>
        </div>
      )}

      {/* ── Multilingual Report Language Selection Modal ── */}
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
                    ? 'कुंडली अहवाल भाषा निवडा'
                    : locale === 'hi'
                    ? 'कुंडली रिपोर्ट की भाषा चुनें'
                    : 'Select Report Language'}
                </h3>
                <p className="text-xs text-[#421A10]/70">
                  {locale === 'mr'
                    ? 'आपल्या जन्म पत्रिकेचा संपूर्ण अहवाल कोणत्या भाषेत हवा आहे ते निवडा'
                    : locale === 'hi'
                    ? 'अपनी जन्म पत्रिका की विस्तृत रिपोर्ट किस भाषा में प्राप्त करना चाहते हैं, चुनें'
                    : 'Choose the language for your comprehensive birth chart dossier'}
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
                  nativeTitle: 'English (Classical Vedic Astrological Terms)',
                  desc: 'Complete natal report in English with Sanskrit house, planet & dasha designations.',
                },
                {
                  id: 'hi' as const,
                  flag: '🇮🇳',
                  title: 'हिन्दी (Hindi)',
                  nativeTitle: 'सम्पूर्ण वैदिक जन्म पत्रिका',
                  desc: 'लग्न कुंडली, नवमांश, द्वादश भाव, नवग्रह स्थिति एवं विंशोत्तरी महादशा हिन्दी में।',
                },
                {
                  id: 'mr' as const,
                  flag: '🚩',
                  title: 'मराठी (Marathi)',
                  nativeTitle: 'सखोल वैदिक जन्म पत्रिका',
                  desc: 'लग्न चक्र, नवमांश (D9), बारा भाव विश्लेषण, ग्रह बल आणि विंशोत्तरी महादशा मराठीत.',
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
                  handleDownloadPdf(selectedReportLang);
                  setIsReportModalOpen(false);
                }}
                disabled={downloadingPdf}
                className="py-2.5 px-4 rounded-xl bg-[#FCEBD2] hover:bg-[#F9DAB5] text-[#821C17] font-bold text-xs border border-[#821C17]/40 flex items-center justify-center gap-2 transition-all cursor-pointer"
              >
                <Download className="w-4 h-4" />
                <span>
                  {selectedReportLang === 'mr'
                    ? 'थेट PDF डाउनलोड'
                    : selectedReportLang === 'hi'
                    ? 'सीधी PDF डाउनलोड'
                    : 'Direct PDF'}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

