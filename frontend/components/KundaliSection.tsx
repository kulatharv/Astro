'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Compass, Sparkles, CheckCircle2 } from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function KundaliSection() {
  const t = useTranslations('kundaliFeature');
  const [chartType, setChartType] = useState<'north' | 'south'>('north');
  const [activeVarga, setActiveVarga] = useState<'d1' | 'd9'>('d1');

  // Sample planetary placements for visual display
  const planetsD1 = [
    { name: 'लग्न (Asc)', rashi: 'मेष (Aries)', deg: '14°22\'', status: 'Lagna' },
    { name: 'सूर्य (Sun)', rashi: 'सिंह (Leo)', deg: '08°45\'', status: 'स्वक्षेत्री (Own)' },
    { name: 'चन्द्र (Moon)', rashi: 'कर्क (Cancer)', deg: '22°10\'', status: 'स्वक्षेत्री (Own)' },
    { name: 'मंगल (Mars)', rashi: 'मकर (Capricorn)', deg: '28°12\'', status: 'उच्च (Exalted)' },
    { name: 'बुध (Merc)', rashi: 'कन्या (Virgo)', deg: '15°04\'', status: 'उच्च (Exalted)' },
    { name: 'गुरु (Jup)', rashi: 'कर्क (Cancer)', deg: '05°30\'', status: 'उच्च (Exalted)' },
    { name: 'शुक्र (Ven)', rashi: 'मीन (Pisces)', deg: '27°18\'', status: 'उच्च (Exalted)' },
    { name: 'शनि (Sat)', rashi: 'तुला (Libra)', deg: '20°05\'', status: 'उच्च (Exalted)' },
    { name: 'राहु (Rahu)', rashi: 'वृषभ (Taurus)', deg: '12°40\'', status: 'वक्री (R)' },
    { name: 'केतु (Ketu)', rashi: 'वृश्चिक (Scorpio)', deg: '12°40\'', status: 'वक्री (R)' },
  ];

  return (
    <section id="kundali" className="py-24 bg-[#FAF6F0] relative scroll-mt-16 border-t border-[#C5A059]/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto space-y-3 mb-16">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#7A1612]/10 border border-[#7A1612]/20 text-[#7A1612] text-xs font-semibold tracking-wider uppercase">
            <Compass className="w-3.5 h-3.5 text-[#C5A059]" />
            <span>{t('eyebrow')}</span>
          </div>
          <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#24120B] tracking-tight">
            {t('title')}
          </h2>
          {/* Ornamental Divider */}
          <div className="flex items-center justify-center gap-3 py-1">
            <span className="h-px w-12 bg-linear-to-r from-transparent to-[#C5A059]" />
            <span className="w-2 h-2 rotate-45 bg-[#7A1612]" />
            <span className="h-px w-12 bg-linear-to-l from-transparent to-[#C5A059]" />
          </div>
          <p className="text-base text-[#24120B]/75 leading-relaxed">
            {t('subtitle')}
          </p>
        </div>

        {/* Kundali Interactive Showcase */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-center">
          {/* Left Column: Visual Chart Display */}
          <div className="lg:col-span-7 bg-[#FFFFFF] rounded-2xl p-6 sm:p-8 border border-[#C5A059]/35 shadow-sm">
            {/* Controls Bar */}
            <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[#C5A059]/25">
              {/* Varga Selector */}
              <div className="inline-flex p-1 rounded-lg bg-[#FAF6F0] border border-[#C5A059]/30">
                <button
                  type="button"
                  onClick={() => setActiveVarga('d1')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                    activeVarga === 'd1'
                      ? 'bg-[#7A1612] text-[#FAF6F0] shadow-xs'
                      : 'text-[#24120B]/70 hover:text-[#7A1612]'
                  }`}
                >
                  {t('d1Title')}
                </button>
                <button
                  type="button"
                  onClick={() => setActiveVarga('d9')}
                  className={`px-3 py-1.5 text-xs font-semibold rounded-md transition-all ${
                    activeVarga === 'd9'
                      ? 'bg-[#7A1612] text-[#FAF6F0] shadow-xs'
                      : 'text-[#24120B]/70 hover:text-[#7A1612]'
                  }`}
                >
                  {t('d9Title')}
                </button>
              </div>

              {/* Chart Style Selector */}
              <div className="inline-flex items-center gap-2">
                <span className="text-xs font-medium text-[#24120B]/80">{t('chartStyle')}:</span>
                <div className="inline-flex p-1 rounded-lg bg-[#FAF6F0] border border-[#C5A059]/30">
                  <button
                    type="button"
                    onClick={() => setChartType('north')}
                    className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
                      chartType === 'north'
                        ? 'bg-[#7A1612] text-[#FAF6F0]'
                        : 'text-[#24120B]/70 hover:text-[#7A1612]'
                    }`}
                  >
                    {t('northIndian')}
                  </button>
                  <button
                    type="button"
                    onClick={() => setChartType('south')}
                    className={`px-2.5 py-1 text-xs font-medium rounded transition-all ${
                      chartType === 'south'
                        ? 'bg-[#7A1612] text-[#FAF6F0]'
                        : 'text-[#24120B]/70 hover:text-[#7A1612]'
                    }`}
                  >
                    {t('southIndian')}
                  </button>
                </div>
              </div>
            </div>

            {/* Chart SVG Rendering */}
            <div className="my-6 flex items-center justify-center">
              <div className="w-full max-w-[420px] aspect-square bg-[#FAF6F0] border border-[#C5A059]/40 rounded-xl relative p-2 shadow-inner">
                {chartType === 'north' ? (
                  /* North Indian Diamond Chart SVG */
                  <svg
                    viewBox="0 0 400 400"
                    className="w-full h-full select-none"
                  >
                    {/* Geometric Structural Lines with explicit stroke */}
                    <g stroke="#7A1612" strokeWidth="1.8" fill="none">
                      {/* Outer Square */}
                      <rect x="5" y="5" width="390" height="390" strokeWidth="2" />
                      
                      {/* Diagonal Crosses */}
                      <line x1="5" y1="5" x2="395" y2="395" />
                      <line x1="395" y1="5" x2="5" y2="395" />
                      
                      {/* Inner Diamond */}
                      <polygon points="200,5 395,200 200,395 5,200" strokeWidth="2" fill="#FAF6F0" fillOpacity="0.45" />
                    </g>

                    {/* House Text Elements - strictly normal weight without ANY stroke */}
                    <g stroke="none" strokeWidth="0" fontWeight="400" className="font-normal" style={{ textRendering: 'geometricPrecision' }}>
                      {/* House 1 (Top Center Diamond) */}
                      <text x="200" y="105" textAnchor="middle" fill="#7A1612" fontSize="13" fontFamily="serif">
                        १ लग्न
                      </text>
                      <text x="200" y="125" textAnchor="middle" fill="#C5A059" fontSize="11" fontFamily="sans-serif">
                        {activeVarga === 'd1' ? 'Ju Me' : 'Su Mo'}
                      </text>

                      {/* House 2 (Top Left Triangle) */}
                      <text x="105" y="55" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">२</text>
                      {/* House 3 */}
                      <text x="55" y="105" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">३</text>
                      {/* House 4 (Left Center Diamond) */}
                      <text x="110" y="200" textAnchor="middle" fill="#7A1612" fontSize="13" fontFamily="serif">४</text>
                      <text x="110" y="220" textAnchor="middle" fill="#C5A059" fontSize="11">Ma</text>
                      {/* House 5 */}
                      <text x="55" y="295" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">५</text>
                      {/* House 6 */}
                      <text x="105" y="345" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">६</text>
                      {/* House 7 (Bottom Center Diamond) */}
                      <text x="200" y="295" textAnchor="middle" fill="#7A1612" fontSize="13" fontFamily="serif">७</text>
                      <text x="200" y="315" textAnchor="middle" fill="#C5A059" fontSize="11">Sa</text>
                      {/* House 8 */}
                      <text x="295" y="345" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">८</text>
                      {/* House 9 */}
                      <text x="345" y="295" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">९</text>
                      {/* House 10 (Right Center Diamond) */}
                      <text x="290" y="200" textAnchor="middle" fill="#7A1612" fontSize="13" fontFamily="serif">१०</text>
                      <text x="290" y="220" textAnchor="middle" fill="#C5A059" fontSize="11">Su</text>
                      {/* House 11 */}
                      <text x="345" y="105" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">११</text>
                      {/* House 12 */}
                      <text x="295" y="55" textAnchor="middle" fill="#24120B" fontSize="11" fontFamily="serif">१२</text>
                    </g>
                  </svg>
                ) : (
                  /* South Indian Grid Chart SVG */
                  <svg
                    viewBox="0 0 400 400"
                    className="w-full h-full select-none"
                  >
                    {/* Outer Square & 4x4 Grid with stroke */}
                    <g stroke="#7A1612" strokeWidth="1.8" fill="none">
                      <rect x="5" y="5" width="390" height="390" strokeWidth="2" />
                      <line x1="102.5" y1="5" x2="102.5" y2="395" />
                      <line x1="200" y1="5" x2="200" y2="395" />
                      <line x1="297.5" y1="5" x2="297.5" y2="395" />
                      <line x1="5" y1="102.5" x2="395" y2="102.5" />
                      <line x1="5" y1="200" x2="395" y2="200" />
                      <line x1="5" y1="297.5" x2="395" y2="297.5" />
                      {/* Center Void Block */}
                      <rect x="102.5" y="102.5" width="195" height="195" fill="#FAF6F0" stroke="#C5A059" strokeWidth="1.5" />
                    </g>

                    {/* Pure Text Group without ANY Stroke */}
                    <g stroke="none" strokeWidth="0" fontWeight="400" className="font-normal" style={{ textRendering: 'geometricPrecision' }}>
                      <text x="200" y="195" textAnchor="middle" fill="#7A1612" fontSize="14" fontFamily="serif">
                        दक्षिण भारतीय
                      </text>
                      <text x="200" y="215" textAnchor="middle" fill="#24120B" fontSize="11">
                        {activeVarga === 'd1' ? 'लग्न कुंडली (D-1)' : 'नवमांश (D-9)'}
                      </text>

                      {/* Fixed Signs Indicators */}
                      <text x="150" y="55" textAnchor="middle" fill="#7A1612" fontSize="11">मेष (Asc)</text>
                      <text x="250" y="55" textAnchor="middle" fill="#24120B" fontSize="11">वृषभ</text>
                      <text x="345" y="55" textAnchor="middle" fill="#24120B" fontSize="11">मिथुन</text>
                      <text x="345" y="150" textAnchor="middle" fill="#C5A059" fontSize="11">कर्क (Mo)</text>
                      <text x="345" y="250" textAnchor="middle" fill="#C5A059" fontSize="11">सिंह (Su)</text>
                      <text x="345" y="345" textAnchor="middle" fill="#C5A059" fontSize="11">कन्या (Me)</text>
                      <text x="250" y="345" textAnchor="middle" fill="#C5A059" fontSize="11">तुला (Sa)</text>
                      <text x="150" y="345" textAnchor="middle" fill="#24120B" fontSize="11">वृश्चिक</text>
                      <text x="55" y="345" textAnchor="middle" fill="#24120B" fontSize="11">धनु</text>
                      <text x="55" y="250" textAnchor="middle" fill="#C5A059" fontSize="11">मकर (Ma)</text>
                      <text x="55" y="150" textAnchor="middle" fill="#24120B" fontSize="11">कुंभ</text>
                      <text x="55" y="55" textAnchor="middle" fill="#C5A059" fontSize="11">मीन (Ve)</text>
                    </g>
                  </svg>
                )}
              </div>
            </div>

            {/* Quick Chart Legend */}
            <div className="flex flex-wrap items-center justify-center gap-4 text-xs text-[#24120B]/75 pt-2">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#7A1612]" />
                {t('ascendant')}: <span className="font-medium text-[#24120B]">Aries (मेष) 14°22&apos;</span>
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-[#C5A059]" />
                {t('moonSign')}: <span className="font-medium text-[#24120B]">Cancer (कर्क) 22°10&apos;</span>
              </span>
            </div>
          </div>

          {/* Right Column: Planetary Positions & Engine Features */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-[#FFFFFF] rounded-2xl border border-[#C5A059]/35 p-6 shadow-sm">
              <h3 className="font-serif text-lg font-bold text-[#24120B] mb-4 flex items-center justify-between">
                <span>ग्रह स्थिति (Planetary Degrees)</span>
                <span className="text-[11px] font-mono text-[#7A1612] uppercase px-2 py-0.5 rounded bg-[#C5A059]/15 border border-[#C5A059]/30 font-medium">
                  Lahiri Ayanamsha
                </span>
              </h3>

              <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                {planetsD1.map((p, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between py-1.5 px-2.5 rounded-lg bg-[#FAF6F0] hover:bg-[#FAF6F0]/80 text-xs transition-colors border border-[#C5A059]/20"
                  >
                    <span className="font-serif font-medium text-[#24120B]">{p.name}</span>
                    <span className="text-[#24120B]/75">{p.rashi}</span>
                    <span className="font-mono text-[#7A1612] font-medium">{p.deg}</span>
                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#C5A059]/15 text-[#7A1612] font-normal">
                      {p.status}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Feature Checklist */}
            <div className="space-y-3 pt-2">
              {[t('feature1'), t('feature2'), t('feature3'), t('feature4')].map((feat, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <CheckCircle2 className="w-4 h-4 text-[#7A1612] shrink-0 mt-0.5" />
                  <span className="text-sm text-[#24120B]/80 leading-tight">{feat}</span>
                </div>
              ))}
            </div>

            {/* Section CTA */}
            <div className="pt-4">
              <Link
                href="/kundali"
                className="w-full inline-flex items-center justify-center gap-2 px-6 py-3.5 text-xs font-semibold uppercase tracking-wider rounded-xl text-[#FAF6F0] bg-linear-to-r from-[#7A1612] to-[#5A0E0A] hover:brightness-110 border border-[#C5A059]/40 shadow-md hover:shadow-lg transition-all"
              >
                <Sparkles className="w-4 h-4 text-[#C5A059]" />
                <span>{t('cta')}</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
