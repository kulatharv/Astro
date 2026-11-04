'use client';

import { useTranslations } from 'next-intl';
import { Sparkles, Calendar, ShieldCheck, Compass } from 'lucide-react';
import { Link } from '@/i18n/routing';

export default function ClosingCTA() {
  const t = useTranslations('closingCta');

  return (
    <section className="py-20 bg-[#FDF5E6] relative border-t border-[#F9DAB5]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative rounded-3xl bg-linear-to-br from-[#821C17] via-[#60100E] to-[#421A10] p-8 sm:p-14 text-center overflow-hidden border-2 border-[#E49D4B]/40 shadow-2xl">
          {/* Subtle background sacred geometry rings */}
          <div className="absolute inset-0 pointer-events-none flex items-center justify-center">
            <div className="w-[500px] h-[500px] rounded-full border border-[#E49D4B]/20 absolute" />
            <div className="w-[300px] h-[300px] rounded-full border border-[#F3C387]/15 absolute" />
            <div className="w-[180px] h-[180px] rounded-full bg-radial from-[#E49D4B]/25 to-transparent absolute blur-xl" />
          </div>

          <div className="relative z-10 max-w-2xl mx-auto space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#FDF5E6]/10 border border-[#E49D4B]/35 text-[#F3C387] text-xs font-semibold tracking-wider uppercase">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Auspicious Beginning</span>
            </div>

            <h2 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-[#FDF5E6] tracking-tight leading-tight">
              {t('title')}
            </h2>

            <p className="text-base sm:text-lg text-[#FCEBD2]/85 leading-relaxed font-normal">
              {t('subtitle')}
            </p>

            {/* CTAs */}
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link
                href="/kundali"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-7 py-3.5 text-sm font-semibold uppercase tracking-wider rounded-lg text-[#421A10] bg-linear-to-r from-[#FDF5E6] via-[#FCEBD2] to-[#F9DAB5] hover:bg-white border border-[#E49D4B] shadow-lg hover:shadow-xl transition-all duration-300 hover:-translate-y-0.5 cursor-pointer"
              >
                <Sparkles className="w-4 h-4 text-[#821C17]" />
                <span>{t('buttonPrimary')}</span>
              </Link>

              <Link
                href="/horoscope"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3.5 text-sm font-semibold tracking-wider rounded-lg text-[#FDF5E6] bg-white/10 hover:bg-white/15 border border-[#F9DAB5]/40 transition-all duration-300 cursor-pointer"
              >
                <Compass className="w-4 h-4 text-[#F3C387]" />
                <span>Explore Daily Horoscope</span>
              </Link>
            </div>

            <div className="pt-4 flex items-center justify-center gap-2 text-xs text-[#F3C387]/85">
              <ShieldCheck className="w-4 h-4 text-[#F3C387]" />
              <span>{t('guarantee')}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
