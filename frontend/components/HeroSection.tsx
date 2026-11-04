'use client';

import { useTranslations } from 'next-intl';
import { Compass, Calendar, Sparkles, ShieldCheck } from 'lucide-react';
import { Link } from '@/i18n/routing';
import CelestialOrrery from './CelestialOrrery';

export default function HeroSection() {
  const t = useTranslations('hero');

  return (
    <section
      id="observatory"
      className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28 bg-linear-to-b from-[#FDF5E6] via-[#FCEBD2]/50 to-[#FDF5E6] text-[#421A10] border-b border-[#F9DAB5]"
    >
      {/* Background Sacred Geometric Mandala Watermark */}
      <div className="absolute inset-0 pointer-events-none flex items-center justify-center overflow-hidden opacity-30">
        <div className="w-[600px] h-[600px] md:w-[900px] md:h-[900px] rounded-full border border-[#E49D4B]/20 absolute animate-[spin_240s_linear_infinite]" />
        <div className="w-[450px] h-[450px] md:w-[700px] md:h-[700px] rounded-full border border-dashed border-[#821C17]/15 absolute animate-[spin_180s_linear_infinite_reverse]" />
        <div className="w-[300px] h-[300px] md:w-[500px] md:h-[500px] rounded-full border border-[#E49D4B]/25 absolute" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-14 items-center">
          {/* ── LEFT COLUMN: BRAND STORYTELLING ── */}
          <div className="lg:col-span-6 xl:col-span-6 space-y-6 text-center lg:text-left">
            {/* Eyebrow Badge */}
            <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#821C17]/8 border border-[#821C17]/20 text-[#821C17] text-xs font-semibold tracking-widest uppercase shadow-2xs">
              <Compass className="w-3.5 h-3.5 text-[#E49D4B]" />
              <span>{t('eyebrow')}</span>
            </div>

            {/* Main Editorial Headline */}
            <h1 className="font-serif text-3xl sm:text-4xl md:text-5xl lg:text-5xl xl:text-6xl font-normal text-[#421A10] leading-[1.14] tracking-tight">
              {t('titleMain')}{' '}
              <span className="font-serif italic text-[#821C17] block sm:inline font-normal">
                {t('titleItalic')}
              </span>
            </h1>

            {/* Supporting Description */}
            <p className="text-base sm:text-lg text-[#421A10]/80 max-w-xl mx-auto lg:mx-0 leading-relaxed font-normal">
              {t('description')}
            </p>

            {/* Dual CTAs */}
            <div className="pt-2 flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4">
              <Link
                href="/kundali"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 text-sm font-semibold tracking-wider rounded-xl text-[#FDF5E6] bg-linear-to-r from-[#821C17] via-[#C46B1E] to-[#821C17] hover:brightness-105 border border-[#E49D4B]/50 shadow-[0_4px_20px_rgba(130,28,23,0.25)] hover:shadow-[0_6px_28px_rgba(130,28,23,0.4)] transition-all duration-300 hover:-translate-y-0.5 group"
              >
                <Sparkles className="w-4 h-4 text-[#F3C387] group-hover:rotate-12 transition-transform duration-300" />
                <span>{t('ctaKundali')}</span>
              </Link>

              <Link
                href="/panchang"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold tracking-wider rounded-xl text-[#421A10] bg-[#FDF5E6] hover:bg-[#FCEBD2] border border-[#F9DAB5] hover:border-[#821C17]/50 shadow-xs hover:shadow-md transition-all duration-300"
              >
                <Calendar className="w-4 h-4 text-[#C46B1E]" />
                <span>{t('ctaPanchang')}</span>
              </Link>
            </div>

            {/* Subtle Trust Statement */}
            <div className="pt-1 flex items-center justify-center lg:justify-start gap-2 text-xs font-serif tracking-wide text-[#C46B1E]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#E49D4B] inline-block" />
              <span>{t('trustStatement')}</span>
            </div>

            {/* Celestial Metric Strip (4 metrics) */}
            <div className="pt-6 border-t border-[#F9DAB5]">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {/* Metric 1: Navagrahas */}
                <div className="p-3 rounded-xl bg-[#FDF5E6]/90 border border-[#F9DAB5] shadow-xs hover:border-[#821C17]/40 transition-colors">
                  <span className="font-serif text-2xl font-bold text-[#821C17] block">
                    {t('metrics.grahas.val')}
                  </span>
                  <span className="text-xs font-semibold text-[#421A10] block">
                    {t('metrics.grahas.label')}
                  </span>
                  <span className="text-[10px] text-[#C46B1E] block">
                    {t('metrics.grahas.sub')}
                  </span>
                </div>

                {/* Metric 2: Nakshatras */}
                <div className="p-3 rounded-xl bg-[#FDF5E6]/90 border border-[#F9DAB5] shadow-xs hover:border-[#821C17]/40 transition-colors">
                  <span className="font-serif text-2xl font-bold text-[#C46B1E] block">
                    {t('metrics.nakshatras.val')}
                  </span>
                  <span className="text-xs font-semibold text-[#421A10] block">
                    {t('metrics.nakshatras.label')}
                  </span>
                  <span className="text-[10px] text-[#C46B1E] block">
                    {t('metrics.nakshatras.sub')}
                  </span>
                </div>

                {/* Metric 3: Rashis */}
                <div className="p-3 rounded-xl bg-[#FDF5E6]/90 border border-[#F9DAB5] shadow-xs hover:border-[#821C17]/40 transition-colors">
                  <span className="font-serif text-2xl font-bold text-[#E49D4B] block">
                    {t('metrics.rashis.val')}
                  </span>
                  <span className="text-xs font-semibold text-[#421A10] block">
                    {t('metrics.rashis.label')}
                  </span>
                  <span className="text-[10px] text-[#C46B1E] block">
                    {t('metrics.rashis.sub')}
                  </span>
                </div>

                {/* Metric 4: Vargas */}
                <div className="p-3 rounded-xl bg-[#FDF5E6]/90 border border-[#F9DAB5] shadow-xs hover:border-[#821C17]/40 transition-colors">
                  <span className="font-serif text-2xl font-bold text-[#821C17] block">
                    {t('metrics.vargas.val')}
                  </span>
                  <span className="text-xs font-semibold text-[#421A10] block">
                    {t('metrics.vargas.label')}
                  </span>
                  <span className="text-[10px] text-[#C46B1E] block">
                    {t('metrics.vargas.sub')}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* ── RIGHT COLUMN: INTERACTIVE CELESTIAL OBSERVATORY ORRERY ── */}
          <div className="lg:col-span-6 xl:col-span-6 flex items-center justify-center">
            <CelestialOrrery />
          </div>
        </div>
      </div>
    </section>
  );
}
